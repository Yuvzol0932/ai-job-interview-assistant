"""岗位聚合服务：本地种子数据 + 可选 RSS 源拉取 + 轻量缓存。"""

import hashlib
import html
import json
import os
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import httpx
from dotenv import dotenv_values

from models.job import JobPosting

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
SEED_PATH = DATA_DIR / "jobs_seed.json"
CACHE_PATH = DATA_DIR / "jobs_cache.json"
REMOTE_SOURCE_ENV = "JOB_RSS_SOURCES"
USER_AGENT = "AI-Job-Interview-Assistant/0.4 (+local demo; respectful crawler)"
REFRESH_TTL_ENV = "JOB_REFRESH_TTL"
REFRESH_TTL_DEFAULT = 900


def _local_name(tag: str) -> str:
    """去掉 XML 命名空间前缀，方便同时解析 RSS 与 Atom。"""
    return tag.rsplit("}", 1)[-1]


def _child_text(element, name: str) -> str:
    for child in element:
        if _local_name(child.tag) == name:
            return (child.text or "").strip()
    return ""


def _split_requirements(text: str) -> list[str]:
    """把一段岗位描述切成一到三条可展示的要求。"""
    cleaned = _clean_text(text)
    pieces = []
    for part in cleaned.replace("；", "。").split("。"):
        part = part.strip()
        if part:
            pieces.append(part)
    return pieces[:3] or ([cleaned] if cleaned else [])


def _clean_text(text: str) -> str:
    """去掉 HTML 标签与 RSSHub 的分隔符，整理成可读文本。"""
    text = html.unescape(text or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[>＞]{2,}", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def jobs_from_rss_xml(xml_text: str, source_label: str) -> list[JobPosting]:
    """从 RSS / Atom XML 文本解析岗位条目，供离线单测与网络拉取共用。"""
    root = ET.fromstring(xml_text)
    entries = [
        node for node in root.iter() if _local_name(node.tag) in ("item", "entry")
    ]
    jobs = []
    for entry in entries:
        title = _clean_text(_child_text(entry, "title"))
        link_node = next(
            (
                child
                for child in entry
                if _local_name(child.tag) == "link"
            ),
            None,
        )
        if link_node is not None:
            url = str(link_node.get("href", "")).strip() or (link_node.text or "").strip()
        else:
            url = ""
        description = _clean_text(
            _child_text(entry, "description")
            or _child_text(entry, "summary")
            or _child_text(entry, "content")
        )
        published = _child_text(entry, "pubDate") or _child_text(entry, "updated")
        if not title:
            continue
        unique_key = url or f"{title}|{published}"
        job_id = "rss-" + hashlib.sha1(unique_key.encode("utf-8")).hexdigest()[:8]
        jobs.append(
            JobPosting(
                id=job_id,
                title=title,
                company=source_label,
                category="通用管培生",
                location="",
                requirements=_split_requirements(description) if description else [title],
                description=description,
                source="rss",
                source_label=source_label,
                url=url,
                posted_at=published[:10] if published else "",
            )
        )
    return jobs


def load_seed_jobs() -> list[JobPosting]:
    """读取内置种子岗位，作为断网演示兜底。"""
    if not SEED_PATH.exists():
        return []
    try:
        data = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    jobs = data.get("jobs") if isinstance(data, dict) else data
    return [JobPosting.from_dict(item) for item in jobs if isinstance(item, dict)]


def load_cached_jobs() -> list[JobPosting]:
    """读取上次 RSS 拉取缓存；损坏时静默降级。"""
    if not CACHE_PATH.exists():
        return []
    try:
        data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    jobs = data.get("jobs") if isinstance(data, dict) else data
    return [JobPosting.from_dict(item) for item in jobs if isinstance(item, dict)]


def _dedupe(jobs: list[JobPosting]) -> list[JobPosting]:
    seen = set()
    result = []
    for job in jobs:
        if job.id in seen:
            continue
        seen.add(job.id)
        result.append(job)
    return result


def load_jobs() -> list[JobPosting]:
    """本地可用的全部岗位：种子优先，缓存补充。"""
    return _dedupe(load_seed_jobs() + load_cached_jobs())


def _save_cache(jobs: list[JobPosting]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(
        json.dumps(
            {
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "jobs": [job.to_dict() for job in jobs],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def _configured_sources() -> list[str]:
    raw = os.getenv(REMOTE_SOURCE_ENV)
    if raw is None:
        env_file = Path(__file__).resolve().parents[1] / ".env"
        raw = str((dotenv_values(env_file) or {}).get(REMOTE_SOURCE_ENV, "") or "")
    raw = raw.strip()
    return [part.strip() for part in raw.replace(";", ",").split(",") if part.strip()]


def fetch_rss_jobs(url: str, timeout: float = 8.0) -> list[JobPosting]:
    """拉取一个 RSS / Atom 源并解析为岗位条目。"""
    response = httpx.get(
        url,
        timeout=timeout,
        follow_redirects=True,
        headers={"User-Agent": USER_AGENT},
    )
    response.raise_for_status()
    return jobs_from_rss_xml(response.text, source_label=url)


def refresh_remote_jobs(sources: list[str] | None = None) -> dict:
    """拉取配置的 RSS 源并合并缓存，返回刷新统计。"""
    if sources is None:
        sources = _configured_sources()
    fetched: list[JobPosting] = []
    errors: list[str] = []
    for source in sources:
        try:
            fetched.extend(fetch_rss_jobs(source))
        except (httpx.HTTPError, ET.ParseError, ValueError, OSError) as exc:
            errors.append(f"{source}: {exc}")
    merged = _dedupe(load_cached_jobs() + fetched)
    if merged:
        _save_cache(merged)
    return {
        "fetched": len(fetched),
        "errors": errors,
        "total": len(load_jobs()),
    }


def maybe_auto_refresh() -> None:
    """缓存超过 TTL 时自动拉取 RSS 源；未配置源则直接跳过。"""
    sources = _configured_sources()
    if not sources:
        return
    try:
        ttl = max(60, int(os.getenv(REFRESH_TTL_ENV, str(REFRESH_TTL_DEFAULT))))
    except ValueError:
        ttl = REFRESH_TTL_DEFAULT
    try:
        age = time.time() - CACHE_PATH.stat().st_mtime
    except OSError:
        age = None
    if age is None or age >= ttl:
        refresh_remote_jobs(sources)


def filter_jobs(
    jobs: list[JobPosting],
    category: str = "",
    location: str = "",
    keyword: str = "",
) -> list[JobPosting]:
    """按岗位方向、城市、关键词做简单筛选。"""
    category = category.strip()
    location = location.strip()
    keyword = keyword.strip().lower()
    result = []
    for job in jobs:
        if category and job.category != category:
            continue
        if location and location not in job.location:
            continue
        if keyword:
            haystack = " ".join(
                [
                    job.title,
                    job.company,
                    job.category,
                    job.location,
                    job.description,
                    " ".join(job.requirements),
                    " ".join(job.tags),
                ]
            ).lower()
            if keyword not in haystack:
                continue
        result.append(job)
    return result


def job_filters(jobs: list[JobPosting]) -> dict:
    """给前端提供筛选选项。"""
    return {
        "categories": sorted({job.category for job in jobs if job.category}),
        "locations": sorted({job.location for job in jobs if job.location}),
        "sources": sorted({job.source_label for job in jobs if job.source_label}),
    }
