"""简历相关 API：解析 / 补全 / 诊断。"""

from dataclasses import asdict

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from api.deps import get_client
from api.schemas import ClarifyRequest, DiagnoseRequest
from models.resume import ClarificationItem, ResumeData
from services.resume_clarification import (
    ClarificationError,
    generate_clarification_items,
    merge_profile,
)
from services.resume_diagnosis import DiagnosisError, diagnose_resume
from services.resume_parser import ResumeParseError, parse_resume_file, parse_resume_text

router = APIRouter(prefix="/api/resume", tags=["resume"])


def _resume_payload(resume: ResumeData) -> dict:
    return {
        "content": resume.content,
        "source_type": resume.source_type,
        "filename": resume.filename,
        "char_count": resume.char_count,
        "is_empty": resume.is_empty,
        "too_short": resume.too_short,
        "preview": resume.preview(),
    }


@router.post("/parse")
async def parse_resume(
    file: UploadFile | None = File(default=None),
    text: str | None = Form(default=None),
    _client=Depends(get_client),
) -> dict:
    """粘贴文本或上传 PDF/Word，返回解析结果。"""
    try:
        if file is not None:
            data = await file.read()
            resume = parse_resume_file(file.filename or "resume.pdf", data)
        elif text is not None:
            resume = parse_resume_text(text)
        else:
            raise HTTPException(status_code=400, detail="请提供文本或上传文件。")
        if resume.is_empty:
            raise HTTPException(status_code=400, detail="简历内容为空，请粘贴文本或上传文件。")
        return _resume_payload(resume)
    except ResumeParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/clarify")
def clarify(req: ClarifyRequest, client=Depends(get_client)) -> dict:
    """AI 识别简历中缺失或模糊的信息，返回待确认项。"""
    if not req.resume_text.strip():
        raise HTTPException(status_code=400, detail="简历内容为空，请先提交简历。")
    try:
        items = generate_clarification_items(client, req.resume_text)
        return {"items": [item.to_dict() for item in items]}
    except ClarificationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/diagnose")
def diagnose(req: DiagnoseRequest, client=Depends(get_client)) -> dict:
    """合并补充信息后生成专属优化方案。"""
    if not req.resume_text.strip():
        raise HTTPException(status_code=400, detail="简历内容为空，请先提交简历。")
    items = [ClarificationItem.from_dict(item) for item in req.items]
    _, combined = merge_profile(req.resume_text, items, req.market_notes)
    resume = ResumeData(content=combined, source_type="api")
    try:
        result = diagnose_resume(
            client,
            resume,
            target_job=req.target_job or None,
            target_location=req.target_location or None,
            market_notes=req.market_notes or None,
        )
        return asdict(result)
    except DiagnosisError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
