"""面试流程状态机数据结构。"""

from dataclasses import dataclass, field


@dataclass
class InterviewState:
    """面试会话状态（契约）。"""

    job_label: str
    questions: list[str] = field(default_factory=list)
    answers: list[str] = field(default_factory=list)  # 与 questions 一一对应，未答为空串
    current_index: int = 0
    status: str = "ready"  # ready / in_progress / finished

    @property
    def total(self) -> int:
        return len(self.questions)

    @property
    def answered_count(self) -> int:
        return sum(1 for answer in self.answers if answer.strip())

    @property
    def current_question(self) -> str:
        if self.status == "in_progress" and self.current_index < self.total:
            return self.questions[self.current_index]
        return ""

    def to_dict(self) -> dict:
        return {
            "job_label": self.job_label,
            "questions": self.questions,
            "answers": self.answers,
            "current_index": self.current_index,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "InterviewState":
        return cls(
            job_label=str(data.get("job_label", "")),
            questions=[str(q) for q in data.get("questions", [])],
            answers=[str(a) for a in data.get("answers", [])],
            current_index=int(data.get("current_index", 0)),
            status=str(data.get("status", "ready")),
        )
