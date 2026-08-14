"""岗位招聘 API：列表浏览 / RSS 刷新 / 简历匹配。"""

from fastapi import APIRouter, Depends, HTTPException, Query

from api.deps import get_client
from api.schemas import JobMatchRequest
from services.job_aggregator import (
    filter_jobs,
    job_filters,
    load_jobs,
    refresh_remote_jobs,
)
from services.job_matcher import match_jobs

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("/labels")
def job_labels() -> dict:
    """岗位方向常量，供模拟面试设置页使用。"""
    from services.job_catalog import job_labels as catalog_labels

    return {"labels": catalog_labels()}


@router.get("")
def list_jobs(
    category: str = Query(default=""),
    location: str = Query(default=""),
    keyword: str = Query(default=""),
) -> dict:
    """返回岗位列表与筛选选项；无参数时返回全部。"""
    jobs = load_jobs()
    filtered = filter_jobs(jobs, category, location, keyword)
    return {
        "jobs": [job.to_dict() for job in filtered],
        "filters": job_filters(jobs),
        "total": len(filtered),
        "updated_at": "2026-08-14",
    }


@router.post("/refresh")
def refresh_jobs() -> dict:
    """拉取 JOB_RSS_SOURCES 中配置的 RSS / Atom 源并更新缓存。"""
    result = refresh_remote_jobs()
    return result


@router.post("/match")
def match(req: JobMatchRequest, client=Depends(get_client)) -> dict:
    """按简历文本返回可投递岗位（含匹配度、理由与差距提示）。"""
    if not req.resume_text.strip():
        raise HTTPException(status_code=400, detail="简历内容为空，请先提交简历。")
    limit = max(1, min(req.limit, 20))
    return match_jobs(
        client,
        req.resume_text,
        load_jobs(),
        target_job=req.target_job,
        target_location=req.target_location,
        limit=limit,
    )
