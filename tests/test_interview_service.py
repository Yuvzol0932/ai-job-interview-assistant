import pytest

from models.interview import InterviewState
from services.interview_service import (
    InterviewError,
    finish_early,
    start_interview,
    submit_answer,
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
    assert state.total == 5
    assert state.current_index == 0
    assert state.job_label == "产品经理"


def test_start_interview_failure():
    client = FakeClient("没有任何 JSON")
    with pytest.raises(InterviewError):
        start_interview(client, "产品经理", num_questions=5)


def test_submit_and_finish():
    state = InterviewState(
        job_label="运营",
        questions=["q1", "q2"],
        answers=["", ""],
        status="in_progress",
    )
    submit_answer(state, "回答一")
    assert state.current_index == 1
    assert state.status == "in_progress"
    submit_answer(state, "回答二")
    assert state.status == "finished"


def test_submit_empty_answer():
    state = InterviewState(
        job_label="运营",
        questions=["q1"],
        answers=[""],
        status="in_progress",
    )
    with pytest.raises(InterviewError):
        submit_answer(state, "   ")


def test_finish_early():
    state = InterviewState(
        job_label="运营",
        questions=["q1", "q2", "q3"],
        answers=["已答", "", ""],
        current_index=1,
        status="in_progress",
    )
    finish_early(state)
    assert state.status == "finished"
    pairs = transcript(state)
    assert pairs[1][1] == ""
    assert pairs[0][1] == "已答"


def test_submit_when_not_in_progress():
    state = InterviewState(
        job_label="运营",
        questions=["q1"],
        answers=[""],
        status="finished",
    )
    with pytest.raises(InterviewError):
        submit_answer(state, "回答")
