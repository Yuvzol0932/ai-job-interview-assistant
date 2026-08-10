def test_app_runs_without_exception(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("LLM_MODE", "mock")
    monkeypatch.setenv("LLM_API_KEY", "")

    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file("app.py", default_timeout=30)
    at.run()
    assert not at.exception
    assert any("AI 求职面试助手" in title.value for title in at.title)
