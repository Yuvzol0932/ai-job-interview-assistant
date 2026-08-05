import json

import pytest

from models.interview import InterviewState
from services.report_service import ReportError, generate_report

REPORT_JSON = json.dumps(
    {
        "dimensions": {
            "内容准确性": 8,
            "逻辑条理": 7,
            "表达清晰度": 9,
            "岗位匹配度": 6,
            "临场应变": 7,
        },
        "total_score": 74,
        "strengths": ["回答完整", "有具体例子"],
        "weaknesses": ["量化不足"],
        "reference_answers": [
            {"question": "q1", "answer": "参考答案一"},
            {"question": "q2", "answer": "参考答案二"},
        ],
        "suggestions": ["多用 STAR", "提前准备"],
    },
    ensure_ascii=False,
)


class FakeClient:
    mock = False

    def __init__(self, text: str = REPORT_JSON):
        self.text = text
        self.last_messages = None

    def chat(self, messages, **kwargs):
        self.last_messages = messages
        return self.text

    def chat_stream(self, messages, **kwargs):
        mid = len(self.text) // 2
        yield self.text[:mid]
        yield self.text[mid:]


def _finished_state() -> InterviewState:
    return InterviewState(
        job_label="产品经理",
        questions=["q1", "q2"],
        answers=["a1", "a2"],
        status="finished",
    )


def test_generate_report():
    report = generate_report(FakeClient(), _finished_state())
    assert report.job_label == "产品经理"
    assert set(report.dimensions) == {
        "内容准确性",
        "逻辑条理",
        "表达清晰度",
        "岗位匹配度",
        "临场应变",
    }
    assert report.total_score == 74
    assert len(report.reference_answers) == 2


def test_generate_report_stream_tokens():
    tokens = []
    report = generate_report(FakeClient(), _finished_state(), on_token=tokens.append)
    assert report.total_score == 74
    assert "".join(tokens) == REPORT_JSON


def test_generate_report_invalid_json():
    with pytest.raises(ReportError):
        generate_report(FakeClient("完全不是 JSON"), _finished_state())


def test_generate_report_not_finished():
    state = InterviewState(
        job_label="产品经理",
        questions=["q1"],
        answers=[""],
        status="in_progress",
    )
    with pytest.raises(ReportError):
        generate_report(FakeClient(), state)


def test_report_includes_follow_up():
    state = InterviewState(
        job_label="产品经理",
        questions=["q1"],
        answers=["a1"],
        follow_up_questions=["追问：具体怎么做的？"],
        follow_up_answers=["追问回答"],
        status="finished",
        phase="done",
    )
    client = FakeClient()
    report = generate_report(client, state)
    assert report.total_score == 74
    content = client.last_messages[-1]["content"]
    assert "面试官追问" in content
    assert "追问回答" in content
