"""简历相关的数据结构。"""

from dataclasses import dataclass, field

from .utils import str_list


@dataclass
class ResumeData:
    """简历解析结果（契约）。"""

    content: str = ""
    source_type: str = "paste"  # paste / pdf / docx
    filename: str | None = None

    @property
    def char_count(self) -> int:
        return len(self.content.strip())

    @property
    def is_empty(self) -> bool:
        return self.char_count == 0

    @property
    def too_short(self) -> bool:
        return 0 < self.char_count < 50

    def preview(self, limit: int = 200) -> str:
        text = self.content.strip().replace("\n", " ")
        return text[:limit] + ("…" if len(text) > limit else "")


@dataclass
class DiagnosisResult:
    """简历诊断结果（契约）。"""

    score: int = 0
    overall_evaluation: str = ""
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    optimized_examples: list[str] = field(default_factory=list)

    @classmethod
    def from_llm_json(cls, data: dict) -> "DiagnosisResult":
        """把大模型返回的 JSON 规范为固定结构。"""
        try:
            score = max(0, min(100, int(data.get("score", 0))))
        except (TypeError, ValueError):
            score = 0
        return cls(
            score=score,
            overall_evaluation=str(data.get("overall_evaluation", "")).strip(),
            strengths=str_list(data.get("strengths")),
            weaknesses=str_list(data.get("weaknesses")),
            suggestions=str_list(data.get("suggestions")),
            optimized_examples=str_list(data.get("optimized_examples")),
        )
