import pytest

from models.interview import InterviewState
from services.interview_service import (
    InterviewError,
    finish_early,
    next_question,
    request_follow_up,
    start_interview,
    submit_follow_up_answer,
    submit_main_answer,
    transcript,
)


class FakeClient:
    mock = False

    def __init__(self, text: str):
        self.text = text

    def chat(self, messages, **kwargs):
        return self.text


def test_start_interview():
    client = FakeClient('{"questions": ["q1", "q2", "q3", "q4", "q5"]}')
    state = start_interview(client, "产品经理", resume_text="有实习经历", num_questions=5)
    assert state.status == "in_progress"
    assert state.phase == "main"
    assert state.total == 5
    assert state.current_index == 0
    assert len(state.follow_up_questions) == 5


def test_start_interview_failure():
    client = FakeClient("没有任何 JSON")
    with pytest.raises(InterviewError):
        start_interview(client, "产品经理", num_questions=5)


def test_main_answer_flow():
    state = InterviewState(
        job_label="运营",
        questions=["q1", "q2"],
        answers=["", ""],
        follow_up_questions=["", ""],
        follow_up_answers=["", ""],
        status="in_progress",
        phase="main",
    )
    submit_main_answer(state, "回答一")
    assert state.phase == "answered_main"
    assert state.current_index == 0
    next_question(state)
    assert state.phase == "main"
    assert state.current_index == 1


def test_empty_main_answer():
    state = InterviewState(
        job_label="运营",
        questions=["q1"],
        answers=[""],
        status="in_progress",
        phase="main",
    )
    with pytest.raises(InterviewError):
        submit_main_answer(state, "   ")


def test_follow_up_flow():
    state = InterviewState(
        job_label="运营",
        questions=["q1"],
        answers=[""],
        follow_up_questions=[""],
        follow_up_answers=[""],
        status="in_progress",
        phase="answered_main",
    )
    client = FakeClient('{"question": "请具体说说你当时负责什么？"}')
    request_follow_up(client, state)
    assert state.phase == "followup"
    assert state.follow_up_questions[0] == "请具体说说你当时负责什么？"

    with pytest.raises(InterviewError, match="不能再次追问"):
        # 追问只能在 answered_main 阶段发起
        state.phase = "answered_main"
        request_follow_up(client, state)

    state.phase = "followup"
    submit_follow_up_answer(state, "我负责活动宣传")
    assert state.phase == "answered_followup"


def test_follow_up_requires_answer():
    state = InterviewState(
        job_label="运营",
        questions=["q1"],
        answers=["已答"],
        follow_up_questions=["追问"],
        follow_up_answers=[""],
        status="in_progress",
        phase="followup",
    )
    with pytest.raises(InterviewError):
        submit_follow_up_answer(state, "  ")


def test_next_question_finishes():
    state = InterviewState(
        job_label="运营",
        questions=["q1"],
        answers=["已答"],
        status="in_progress",
        phase="answered_main",
    )
    next_question(state)
    assert state.status == "finished"


def test_next_question_requires_completion():
    state = InterviewState(
        job_label="运营",
        questions=["q1"],
        answers=[""],
        status="in_progress",
        phase="main",
    )
    with pytest.raises(InterviewError):
        next_question(state)


def test_finish_early():
    state = InterviewState(
        job_label="运营",
        questions=["q1", "q2", "q3"],
        answers=["已答", "", ""],
        status="in_progress",
        phase="main",
    )
    finish_early(state)
    assert state.status == "finished"
    records = transcript(state)
    assert records[0]["answer"] == "已答"
    assert records[1]["answer"] == ""
    assert records[0]["follow_up_question"] == ""


def test_transcript_with_follow_up():
    state = InterviewState(
        job_label="运营",
        questions=["q1"],
        answers=["a1"],
        follow_up_questions=["追问"],
        follow_up_answers=["追问回答"],
        status="finished",
        phase="done",
    )
    records = transcript(state)
    assert records[0]["follow_up_question"] == "追问"
    assert records[0]["follow_up_answer"] == "追问回答"
