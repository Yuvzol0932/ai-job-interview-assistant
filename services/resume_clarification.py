"""简历信息补全服务：提取缺失项、生成问题、合并补充信息。"""

from llm.client import LLMError
from llm.json_utils import extract_json
from llm.prompts import build_clarification_messages, mock_clarification_response
from models.resume import ClarificationItem, ResumeProfile
from services._llm_call import call_chat


class ClarificationError(Exception):
    """信息补全失败的统一异常，信息对用户可读。"""


_KNOWN_FIELDS = {"school", "target_location", "target_direction"}


def generate_clarification_items(client, resume_text: str) -> list[ClarificationItem]:
    """让 AI 分析简历，返回需要用户补充的待确认项列表。"""
    if not resume_text.strip():
        raise ClarificationError("简历内容为空，请粘贴文本或上传文件。")
    messages = build_clarification_messages(resume_text)
    try:
        text = call_chat(client, messages, mock_builder=mock_clarification_response)
    except LLMError as exc:
        raise ClarificationError(str(exc)) from exc

    data = extract_json(text)
    if not isinstance(data, dict):
        raise ClarificationError("AI 返回格式异常，请重试。")

    items = []
    for raw in data.get("items") or []:
        if not isinstance(raw, dict):
            continue
        field = str(raw.get("field", "")).strip()
        question = str(raw.get("question", "")).strip()
        if field and question:
            items.append(
                ClarificationItem(
                    field=field,
                    question=question,
                    hint=str(raw.get("hint", "")).strip(),
                )
            )
    if not items:
        raise ClarificationError("AI 未识别出需要补充的信息，可直接开始诊断。")
    return items


def merge_profile(
    resume_text: str,
    items: list[ClarificationItem],
    market_notes: str = "",
) -> tuple[ResumeProfile, str]:
    """把用户填写的待确认项与市场说明合并为补充信息，返回（档案，合并后文本）。"""
    profile = ResumeProfile(market_notes=market_notes.strip())
    other_lines = []
    for item in items:
        answer = item.answer.strip()
        if not answer:
            continue
        if item.field in _KNOWN_FIELDS:
            setattr(profile, item.field, answer)
        else:
            other_lines.append(f"- {item.question}：{answer}")

    parts = []
    if profile.school:
        parts.append(f"毕业院校：{profile.school}")
    if profile.target_location:
        parts.append(f"期望工作地点：{profile.target_location}")
    if profile.target_direction:
        parts.append(f"意向从业方向：{profile.target_direction}")
    if other_lines:
        parts.append("其他补充：\n" + "\n".join(other_lines))
    if profile.market_notes:
        parts.append(f"当地市场补充说明：{profile.market_notes}")

    block = "\n".join(parts)
    combined = resume_text
    if block:
        combined = resume_text + "\n\n【用户补充信息】\n" + block
    return profile, combined
