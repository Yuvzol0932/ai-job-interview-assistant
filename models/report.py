"""面试报告数据结构。"""

import datetime
import uuid
from dataclasses import dataclass, field

from .utils import str_list

DIMENSIONS = ["内容准确性", "逻辑条理", "表达清晰度", "岗位匹配度", "临场应变"]


@dataclass
class InterviewReport:
    """面试报告（契约）。"""

    report_id: str = ""
    created_at: str = ""
    job_label: str = ""
    dimensions: dict[str, int] = field(default_factory=dict)
    total_score: int = 0
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    reference_answers: list[dict] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)

    @classmethod
    def from_llm_json(cls, data: dict, job_label: str = "") -> "InterviewReport":
        """把大模型返回的 JSON 规范为固定结构。"""
        raw_dimensions = data.get("dimensions") or {}
        dimensions: dict[str, int] = {}
        for name in DIMENSIONS:
            try:
                dimensions[name] = max(0, min(10, int(raw_dimensions.get(name, 0))))
            except (TypeError, ValueError):
                dimensions[name] = 0

        try:
            total_score = max(0, min(100, int(data.get("total_score", 0))))
        except (TypeError, ValueError):
            total_score = 0

        reference_answers = []
        for item in data.get("reference_answers") or []:
            if isinstance(item, dict):
                reference_answers.append(
                    {
                        "question": str(item.get("question", "")).strip(),
                        "answer": str(item.get("answer", "")).strip(),
                    }
                )

        return cls(
            report_id=uuid.uuid4().hex[:12],
            created_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            job_label=job_label or str(data.get("job_label", "")),
            dimensions=dimensions,
            total_score=total_score,
            strengths=str_list(data.get("strengths")),
            weaknesses=str_list(data.get("weaknesses")),
            reference_answers=reference_answers,
            suggestions=str_list(data.get("suggestions")),
        )

    def to_dict(self) -> dict:
        return {
            "report_id": self.report_id,
            "created_at": self.created_at,
            "job_label": self.job_label,
            "dimensions": self.dimensions,
            "total_score": self.total_score,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "reference_answers": self.reference_answers,
            "suggestions": self.suggestions,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "InterviewReport":
        return cls(
            report_id=str(data.get("report_id", "")),
            created_at=str(data.get("created_at", "")),
            job_label=str(data.get("job_label", "")),
            dimensions={str(k): int(v) for k, v in (data.get("dimensions") or {}).items()},
            total_score=int(data.get("total_score", 0)),
            strengths=str_list(data.get("strengths")),
            weaknesses=str_list(data.get("weaknesses")),
            reference_answers=[
                {
                    "question": str(item.get("question", "")),
                    "answer": str(item.get("answer", "")),
                }
                for item in (data.get("reference_answers") or [])
                if isinstance(item, dict)
            ],
            suggestions=str_list(data.get("suggestions")),
        )
