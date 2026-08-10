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
        "overall_impression": "整体不错，有具体例子，但量化表达可以更强。",
        "question_comments": [
            {"question": "q1", "comment": "第一题回答完整，但可以前置结论。"},
            {"question": "q2", "comment": "第二题例子不错，缺一个量化结果。"},
        ],
        "growth_advice": ["多用 STAR 结构", "提前准备岗位提问"],
        "closing": "下次记得先讲结果。",
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
    assert "整体不错" in report.overall_impression
    assert len(report.question_comments) == 2
    assert len(report.growth_advice) == 2
    assert report.closing


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


def test_delete_report(monkeypatch, tmp_path):
    from services import report_store

    monkeypatch.setattr(report_store, "REPORT_DIR", tmp_path)
    state = _finished_state()
    report = generate_report(FakeClient(), state)
    report_store.save_report(report)
    assert len(report_store.list_reports()) == 1
    assert report_store.delete_report(report.report_id) is True
    assert len(report_store.list_reports()) == 0
    assert report_store.delete_report(report.report_id) is False
