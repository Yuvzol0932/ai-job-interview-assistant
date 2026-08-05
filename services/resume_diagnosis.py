"""简历诊断服务：组织提示词、调用模型、解析结果。"""

from llm.client import LLMError
from llm.json_utils import extract_json
from llm.prompts import build_diagnosis_messages, mock_diagnosis_response
from models.resume import DiagnosisResult, ResumeData
from services._llm_call import call_chat


class DiagnosisError(Exception):
    """简历诊断失败的统一异常，信息对用户可读。"""


def diagnose_resume(
    client,
    resume: ResumeData,
    target_job: str | None = None,
    target_location: str | None = None,
    market_notes: str | None = None,
    on_token=None,
) -> DiagnosisResult:
    """执行简历诊断；on_token 用于流式展示。"""
    if resume.is_empty:
        raise DiagnosisError("简历内容为空，请粘贴文本或上传文件。")
    messages = build_diagnosis_messages(
        resume.content,
        target_job,
        target_location,
        market_notes,
    )
    try:
        text = call_chat(client, messages, mock_builder=mock_diagnosis_response, on_token=on_token)
    except LLMError as exc:
        raise DiagnosisError(str(exc)) from exc

    data = extract_json(text)
    if not isinstance(data, dict):
        raise DiagnosisError("AI 返回格式异常，请点击重试。")
    try:
        return DiagnosisResult.from_llm_json(data)
    except Exception as exc:
        raise DiagnosisError("诊断结果解析失败，请点击重试。") from exc
