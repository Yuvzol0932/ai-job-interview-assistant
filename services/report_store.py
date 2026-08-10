"""报告本地存储服务：保存 / 列出 / 读取。"""

import json
from pathlib import Path

from models.report import InterviewReport

REPORT_DIR = Path(__file__).resolve().parents[1] / "data" / "reports"


def _ensure_dir() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)


def save_report(report: InterviewReport) -> Path:
    """保存报告到本地 JSON 文件。"""
    _ensure_dir()
    path = REPORT_DIR / f"{report.report_id}.json"
    path.write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def list_reports() -> list[dict]:
    """按时间倒序返回报告元信息列表。"""
    _ensure_dir()
    reports = []
    for path in REPORT_DIR.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            reports.append(
                {
                    "report_id": str(data.get("report_id", path.stem)),
                    "created_at": str(data.get("created_at", "")),
                    "job_label": str(data.get("job_label", "")),
                    "total_score": int(data.get("total_score", 0)),
                }
            )
        except (json.JSONDecodeError, OSError, ValueError):
            continue
    reports.sort(key=lambda item: item["created_at"], reverse=True)
    return reports


def load_report(report_id: str) -> InterviewReport | None:
    """按 ID 读取报告；不存在或损坏时返回 None。"""
    path = REPORT_DIR / f"{report_id}.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return InterviewReport.from_dict(data)
    except (json.JSONDecodeError, OSError, ValueError, KeyError):
        return None


def delete_report(report_id: str) -> bool:
    """删除本地报告；成功返回 True。"""
    path = REPORT_DIR / f"{report_id}.json"
    if not path.exists():
        return False
    try:
        path.unlink()
        return True
    except OSError:
        return False
