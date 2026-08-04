"""面试流程状态机服务。"""

from llm.client import LLMError
from llm.json_utils import extract_json
from llm.prompts import build_questions_messages, mock_questions_response
from models.interview import InterviewState
from services._llm_call import call_chat


class InterviewError(Exception):
    """面试流程失败的统一异常，信息对用户可读。"""


def start_interview(
    client,
    job_label: str,
    resume_text: str = "",
    num_questions: int = 5,
) -> InterviewState:
    """开始面试：请求 AI 出题并初始化状态机。"""
    if not job_label.strip():
        raise InterviewError("请先选择或填写岗位方向。")
    num_questions = max(3, min(8, int(num_questions)))
    messages = build_questions_messages(job_label, resume_text, num_questions)
    try:
        text = call_chat(client, messages, mock_builder=mock_questions_response)
    except LLMError as exc:
        raise InterviewError(str(exc)) from exc

    data = extract_json(text)
    questions = []
    if isinstance(data, dict):
        questions = [str(q).strip() for q in (data.get("questions") or []) if str(q).strip()]
    if not questions:
        raise InterviewError("AI 出题失败，请点击重试。")

    return InterviewState(
        job_label=job_label.strip(),
        questions=questions[:num_questions],
        answers=[""] * min(len(questions), num_questions),
        current_index=0,
        status="in_progress",
    )


def submit_answer(state: InterviewState, answer: str) -> None:
    """提交当前题目的回答并推进到下一题。"""
    if state.status != "in_progress":
        raise InterviewError("当前没有进行中的面试。")
    if not answer.strip():
        raise InterviewError("请先输入回答内容再提交。")
    if state.current_index >= state.total:
        state.status = "finished"
        return
    state.answers[state.current_index] = answer.strip()
    state.current_index += 1
    if state.current_index >= state.total:
        state.status = "finished"


def finish_early(state: InterviewState) -> None:
    """提前结束面试，未答题目留空。"""
    if state.status == "in_progress":
        state.status = "finished"


def transcript(state: InterviewState) -> list[tuple[str, str]]:
    """返回 (题目, 回答) 列表，供报告服务使用。"""
    return [
        (question, state.answers[index] if index < len(state.answers) else "")
        for index, question in enumerate(state.questions)
    ]
