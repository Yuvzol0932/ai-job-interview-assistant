"""面试流程状态机服务。"""

from llm.client import LLMError
from llm.json_utils import extract_json
from llm.prompts import (
    build_follow_up_messages,
    build_questions_messages,
    mock_follow_up_response,
    mock_questions_response,
)
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

    count = min(len(questions), num_questions)
    return InterviewState(
        job_label=job_label.strip(),
        questions=questions[:count],
        answers=[""] * count,
        follow_up_questions=[""] * count,
        follow_up_answers=[""] * count,
        current_index=0,
        status="in_progress",
        phase="main",
    )


def submit_main_answer(state: InterviewState, answer: str) -> None:
    """提交当前主问题回答，等待用户选择追问或下一题。"""
    if state.status != "in_progress" or state.phase != "main":
        raise InterviewError("当前不能提交答案。")
    if not answer.strip():
        raise InterviewError("请先输入回答内容再提交。")
    state.answers[state.current_index] = answer.strip()
    state.phase = "answered_main"


def request_follow_up(client, state: InterviewState) -> None:
    """针对当前回答生成一次追问。"""
    if state.status != "in_progress" or state.phase != "answered_main":
        raise InterviewError("请先提交本题回答，再让 AI 追问。")
    if state.follow_up_questions[state.current_index]:
        raise InterviewError("本题已经追问过，不能再次追问。")
    messages = build_follow_up_messages(
        state.job_label,
        state.questions[state.current_index],
        state.answers[state.current_index],
    )
    try:
        text = call_chat(client, messages, mock_builder=mock_follow_up_response)
    except LLMError as exc:
        raise InterviewError(str(exc)) from exc
    data = extract_json(text)
    question = ""
    if isinstance(data, dict):
        question = str(data.get("question", "")).strip()
    if not question:
        raise InterviewError("AI 追问生成失败，请点击重试。")
    state.follow_up_questions[state.current_index] = question
    state.phase = "followup"


def submit_follow_up_answer(state: InterviewState, answer: str) -> None:
    """提交追问的回答。"""
    if state.status != "in_progress" or state.phase != "followup":
        raise InterviewError("当前没有需要回答的追问。")
    if not answer.strip():
        raise InterviewError("请先输入追问的回答内容。")
    state.follow_up_answers[state.current_index] = answer.strip()
    state.phase = "answered_followup"


def next_question(state: InterviewState) -> None:
    """进入下一题；已是最后一题时结束面试。"""
    if state.status != "in_progress":
        raise InterviewError("面试已结束。")
    if state.phase not in ("answered_main", "answered_followup"):
        raise InterviewError("请先完成当前题目。")
    state.current_index += 1
    if state.current_index >= state.total:
        state.status = "finished"
        state.phase = "done"
    else:
        state.phase = "main"


def finish_early(state: InterviewState) -> None:
    """提前结束面试，未答题目留空。"""
    if state.status == "in_progress":
        state.status = "finished"
        state.phase = "done"


def transcript(state: InterviewState) -> list[dict]:
    """返回结构化面试记录（含追问），供报告服务使用。"""
    records = []
    for index, question in enumerate(state.questions):
        records.append(
            {
                "question": question,
                "answer": state.answers[index] if index < len(state.answers) else "",
                "follow_up_question": (
                    state.follow_up_questions[index]
                    if index < len(state.follow_up_questions)
                    else ""
                ),
                "follow_up_answer": (
                    state.follow_up_answers[index]
                    if index < len(state.follow_up_answers)
                    else ""
                ),
            }
        )
    return records
