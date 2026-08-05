"""面试报告生成服务。"""

from llm.client import LLMError
from llm.json_utils import extract_json
from llm.prompts import build_report_messages, mock_report_response
from models.interview import InterviewState
from models.report import InterviewReport
from services._llm_call import call_chat
from services.interview_service import transcript


class ReportError(Exception):
    """报告生成失败的统一异常，信息对用户可读。"""


def generate_report(
    client,
    state: InterviewState,
    on_token=None,
) -> InterviewReport:
    """生成面试报告；on_token 用于流式展示。"""
    if state.status != "finished":
        raise ReportError("面试尚未结束，请先完成或提前结束面试。")
    records = transcript(state)
    messages = build_report_messages(
        state.job_label,
        state.questions,
        state.answers,
        follow_ups=records,
    )
    try:
        text = call_chat(client, messages, mock_builder=mock_report_response, on_token=on_token)
    except LLMError as exc:
        raise ReportError(str(exc)) from exc

    data = extract_json(text)
    if not isinstance(data, dict):
        raise ReportError("AI 返回格式异常，请点击重试。")
    try:
        return InterviewReport.from_llm_json(data, job_label=state.job_label)
    except Exception as exc:
        raise ReportError("报告解析失败，请点击重试。") from exc
