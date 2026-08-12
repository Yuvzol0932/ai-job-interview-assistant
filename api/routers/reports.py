"""面试复盘 API：生成 / 列表 / 读取 / 删除。"""

from fastapi import APIRouter, Depends, HTTPException

from api.deps import get_client
from api.schemas import InterviewStateRequest
from models.interview import InterviewState
from services.report_service import ReportError, generate_report
from services.report_store import delete_report, list_reports, load_report, save_report

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("/generate")
def generate(req: InterviewStateRequest, client=Depends(get_client)) -> dict:
    try:
        state = InterviewState.from_dict(req.state)
        report = generate_report(client, state)
        save_report(report)
        return report.to_dict()
    except ReportError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("")
def list_all() -> dict:
    return {"reports": list_reports()}


@router.get("/{report_id}")
def load(report_id: str) -> dict:
    report = load_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="报告不存在或已删除。")
    return report.to_dict()


@router.delete("/{report_id}")
def delete(report_id: str) -> dict:
    if not delete_report(report_id):
        raise HTTPException(status_code=404, detail="报告不存在或已删除。")
    return {"ok": True}
