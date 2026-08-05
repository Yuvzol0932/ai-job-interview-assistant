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
class ResumeProfile:
    """用户补充信息（仅用于简历优化）。"""

    school: str = ""
    target_location: str = ""
    target_direction: str = ""
    extra_notes: str = ""
    market_notes: str = ""

    def to_dict(self) -> dict:
        return {
            "school": self.school,
            "target_location": self.target_location,
            "target_direction": self.target_direction,
            "extra_notes": self.extra_notes,
            "market_notes": self.market_notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ResumeProfile":
        return cls(
            school=str(data.get("school", "")),
            target_location=str(data.get("target_location", "")),
            target_direction=str(data.get("target_direction", "")),
            extra_notes=str(data.get("extra_notes", "")),
            market_notes=str(data.get("market_notes", "")),
        )


@dataclass
class ClarificationItem:
    """AI 识别出的简历待确认项（契约）。"""

    field: str  # 字段标识：school / target_location / target_direction / 其他英文标识
    question: str  # 向用户展示的中文问题
    hint: str = ""  # 填写提示
    answer: str = ""  # 用户填写的内容（界面层设置）

    def to_dict(self) -> dict:
        return {
            "field": self.field,
            "question": self.question,
            "hint": self.hint,
            "answer": self.answer,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ClarificationItem":
        return cls(
            field=str(data.get("field", "")),
            question=str(data.get("question", "")),
            hint=str(data.get("hint", "")),
            answer=str(data.get("answer", "")),
        )


@dataclass
class DiagnosisResult:
    """简历诊断结果（契约）。"""

    score: int = 0
    overall_evaluation: str = ""
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    optimized_examples: list[str] = field(default_factory=list)
    requirement_table: list[dict] = field(default_factory=list)
    top_priorities: list[str] = field(default_factory=list)
    market_notes: str = ""

    @classmethod
    def from_llm_json(cls, data: dict) -> "DiagnosisResult":
        """把大模型返回的 JSON 规范为固定结构。"""
        try:
            score = max(0, min(100, int(data.get("score", 0))))
        except (TypeError, ValueError):
            score = 0
        requirement_table = []
        for item in data.get("requirement_table") or []:
            if isinstance(item, dict):
                requirement_table.append(
                    {
                        "requirement": str(item.get("requirement", "")).strip(),
                        "evidence": str(item.get("evidence", "")).strip(),
                        "strength": str(item.get("strength", "")).strip(),
                        "gap": str(item.get("gap", "")).strip(),
                    }
                )
        return cls(
            score=score,
            overall_evaluation=str(data.get("overall_evaluation", "")).strip(),
            strengths=str_list(data.get("strengths")),
            weaknesses=str_list(data.get("weaknesses")),
            suggestions=str_list(data.get("suggestions")),
            optimized_examples=str_list(data.get("optimized_examples")),
            requirement_table=requirement_table,
            top_priorities=str_list(data.get("top_priorities")),
            market_notes=str(data.get("market_notes", "")).strip(),
        )
