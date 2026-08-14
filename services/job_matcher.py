"""简历与岗位匹配服务：规则打分兜底，真实模型模式可叠加 LLM 精排。"""

from llm.json_utils import extract_json
from llm.prompts import build_job_match_messages, mock_job_match_response
from services._llm_call import call_chat


def _clamp_score(score: int) -> int:
    return max(0, min(100, score))


def _keyword_tokens(text: str) -> list[str]:
    """从岗位标签与要求中提取可用于匹配的短关键词。"""
    tokens = []
    for item in text.replace("，", ",").replace("、", ",").split(","):
        item = item.strip()
        if item and len(item) >= 2:
            tokens.append(item)
    return tokens


def _score_by_rules(
    resume_text: str,
    jobs,
    target_job: str = "",
    target_location: str = "",
) -> list[dict]:
    resume_lower = resume_text.lower()
    target_job = target_job.strip()
    target_location = target_location.strip()
    results = []
    for job in jobs:
        score = 35
        reasons: list[str] = []
        hits: list[str] = []

        category_related = job.category and (
            (target_job and job.category in target_job)
            or (target_job and target_job in job.category)
            or (not target_job and any(tag in resume_text for tag in job.tags))
        )
        if category_related:
            score += 25
            reasons.append("岗位方向与你的目标或经历匹配")

        location_related = job.location and (
            (target_location and target_location in job.location)
            or (target_location and job.location in target_location)
            or (not target_location and job.location in resume_text)
        )
        if location_related:
            score += 15
            reasons.append("工作地点与期望一致")

        for tag in job.tags:
            tag_lower = tag.lower()
            if tag_lower and tag_lower in resume_lower:
                hits.append(tag)
        for requirement in job.requirements:
            for token in _keyword_tokens(requirement):
                if len(token) >= 2 and token.lower() in resume_lower:
                    hits.append(token)
        unique_hits = list(dict.fromkeys(hits))
        if unique_hits:
            score += min(len(unique_hits) * 8, 30)
            reasons.append(
                f"简历提到{'、'.join(unique_hits[:3])}等关键词"
            )

        if not reasons:
            reasons.append("岗位方向与你的求职背景相关")
        gaps = [
            requirement
            for requirement in job.requirements
            if requirement and requirement.lower() not in resume_lower
        ][:2]
        if not gaps and job.education:
            gaps = [f"岗位学历要求：{job.education}"]

        results.append(
            {
                **job.to_dict(),
                "match_score": _clamp_score(score),
                "match_reasons": reasons[:3],
                "gap_hints": gaps,
            }
        )
    results.sort(key=lambda item: item["match_score"], reverse=True)
    return results


def _rank_with_llm(client, resume_text: str, target_job: str, target_location: str, candidates: list[dict], limit: int) -> dict:
    shortlisted = candidates[:15]
    messages = build_job_match_messages(
        resume_text,
        target_job,
        target_location,
        [item for item in shortlisted],
    )
    text = call_chat(client, messages, mock_builder=mock_job_match_response)
    data = extract_json(text)
    if not isinstance(data, dict):
        raise ValueError("匹配结果解析失败")
    scored = {}
    for item in data.get("results") or []:
        if not isinstance(item, dict) or not item.get("id"):
            continue
        try:
            score = _clamp_score(int(item.get("score", 0)))
        except (TypeError, ValueError):
            score = 0
        scored[str(item["id"])] = {
            "score": score,
            "reasons": [str(text).strip() for text in item.get("reasons") or [] if str(text).strip()][:3],
            "gaps": [str(text).strip() for text in item.get("gaps") or [] if str(text).strip()][:2],
        }
    ranked = []
    for candidate in shortlisted:
        info = scored.get(candidate["id"])
        ranked.append(
            {
                **candidate,
                "match_score": info["score"] if info else candidate["match_score"],
                "match_reasons": info["reasons"] if info and info["reasons"] else candidate["match_reasons"],
                "gap_hints": info["gaps"] if info and info["gaps"] else candidate["gap_hints"],
            }
        )
    ranked.sort(key=lambda item: item["match_score"], reverse=True)
    return {"jobs": ranked[:limit], "strategy": "llm"}


def match_jobs(
    client,
    resume_text: str,
    jobs,
    target_job: str = "",
    target_location: str = "",
    limit: int = 8,
) -> dict:
    """返回可投递岗位；规则结果永远可用，LLM 精排失败时自动降级。"""
    if not resume_text.strip():
        return {"jobs": [], "strategy": "rules"}
    candidates = _score_by_rules(resume_text, jobs, target_job, target_location)
    if client is not None and not getattr(client, "mock", True):
        try:
            return _rank_with_llm(
                client,
                resume_text,
                target_job,
                target_location,
                candidates,
                limit,
            )
        except Exception:
            # 精排失败不影响演示：继续使用规则排序结果
            pass
    return {"jobs": candidates[:limit], "strategy": "rules"}
