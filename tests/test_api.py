"""API 网关集成测试：使用 mock 模型客户端，不消耗真实额度。"""

import pytest


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("LLM_MODE", "mock")
    monkeypatch.setenv("LLM_API_KEY", "")

    from fastapi.testclient import TestClient

    from api.app import app

    with TestClient(app) as test_client:
        yield test_client


RESUME_TEXT = (
    "张同学，青岛大学，市场营销专业，2026 届。"
    "在校担任学生会外联部部长，组织过三场校园活动，"
    "在本地一家公司做过两个月新媒体运营实习。"
)


def test_health_and_jobs(client):
    assert client.get("/api/health").json()["status"] == "ok"
    labels = client.get("/api/jobs/labels").json()["labels"]
    assert "产品经理" in labels and "自定义岗位" in labels
    feed = client.get("/api/jobs").json()
    assert feed["total"] >= 30
    assert "产品经理" in feed["filters"]["categories"]
    assert "青岛" in feed["filters"]["locations"]


def test_job_match_and_refresh(client):
    matched = client.post(
        "/api/jobs/match",
        json={
            "resume_text": RESUME_TEXT,
            "target_job": "市场营销",
            "target_location": "青岛",
            "limit": 5,
        },
    )
    assert matched.status_code == 200
    payload = matched.json()
    assert payload["jobs"]
    assert all("match_score" in item for item in payload["jobs"])

    empty = client.post("/api/jobs/match", json={"resume_text": ""})
    assert empty.status_code == 400

    refreshed = client.post("/api/jobs/refresh")
    assert refreshed.status_code == 200
    assert refreshed.json()["total"] >= 30


def test_parse_text_and_errors(client):
    ok = client.post("/api/resume/parse", data={"text": RESUME_TEXT})
    assert ok.status_code == 200
    payload = ok.json()
    assert payload["is_empty"] is False
    assert payload["char_count"] > 0

    empty = client.post("/api/resume/parse", data={"text": ""})
    assert empty.status_code == 400

    missing = client.post("/api/resume/parse", data={})
    assert missing.status_code == 400


def test_clarify_and_diagnose(client):
    clarify = client.post("/api/resume/clarify", json={"resume_text": RESUME_TEXT})
    assert clarify.status_code == 200
    items = clarify.json()["items"]
    assert isinstance(items, list)
    assert all("question" in item for item in items)

    diagnose = client.post(
        "/api/resume/diagnose",
        json={
            "resume_text": RESUME_TEXT,
            "items": items,
            "market_notes": "本地岗位普遍要求会数据分析",
            "target_job": "市场营销",
            "target_location": "青岛",
        },
    )
    assert diagnose.status_code == 200
    result = diagnose.json()
    assert 0 <= result["score"] <= 100
    assert isinstance(result["top_priorities"], list)


def test_full_interview_and_report_flow(client):
    start = client.post(
        "/api/interview/start",
        json={"job_label": "运营", "num_questions": 3, "resume_text": ""},
    )
    assert start.status_code == 200
    state = start.json()
    assert state["status"] == "in_progress"
    assert state["total"] == 3
    assert state["current_question"]

    answered = client.post(
        "/api/interview/answer", json={"state": state, "answer": "这是我的回答。"}
    )
    assert answered.status_code == 200
    state = answered.json()
    assert state["phase"] == "answered_main"

    followup = client.post("/api/interview/followup", json={"state": state})
    assert followup.status_code == 200
    state = followup.json()
    assert state["phase"] == "followup"
    assert state["current_follow_up_question"]

    follow_answered = client.post(
        "/api/interview/followup-answer",
        json={"state": state, "answer": "追问的回答。"},
    )
    assert follow_answered.status_code == 200
    state = follow_answered.json()
    assert state["phase"] == "answered_followup"

    # 剩余题目全部作答
    for _ in range(state["total"] - 1):
        nxt = client.post("/api/interview/next", json={"state": state})
        assert nxt.status_code == 200
        state = nxt.json()
        if state["status"] == "finished":
            break
        answered = client.post(
            "/api/interview/answer", json={"state": state, "answer": "继续回答。"}
        )
        state = answered.json()

    if state["status"] != "finished":
        state = client.post("/api/interview/next", json={"state": state}).json()
    assert state["status"] == "finished"

    generated = client.post("/api/reports/generate", json={"state": state})
    assert generated.status_code == 200
    report = generated.json()
    assert report["report_id"]
    assert 0 <= report["total_score"] <= 100

    listing = client.get("/api/reports").json()["reports"]
    assert any(item["report_id"] == report["report_id"] for item in listing)

    loaded = client.get(f"/api/reports/{report['report_id']}")
    assert loaded.status_code == 200
    assert loaded.json()["job_label"] == "运营"

    deleted = client.delete(f"/api/reports/{report['report_id']}")
    assert deleted.status_code == 200
    assert client.get(f"/api/reports/{report['report_id']}").status_code == 404
