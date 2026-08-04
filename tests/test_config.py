from llm import config as config_module


def test_deepseek_preset(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    monkeypatch.setenv("LLM_MODE", "real")
    cfg = config_module.LLMConfig.from_env()
    assert cfg.mock is False
    assert cfg.model == "deepseek-chat"
    assert "api.deepseek.com" in cfg.base_url


def test_openai_preset(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    monkeypatch.setenv("LLM_MODE", "real")
    cfg = config_module.LLMConfig.from_env()
    assert cfg.mock is False
    assert cfg.model == "gpt-4o-mini"
    assert "api.openai.com" in cfg.base_url


def test_auto_mock_without_key(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.setenv("LLM_MODE", "")
    cfg = config_module.LLMConfig.from_env()
    assert cfg.mock is True


def test_mock_mode_forced(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    monkeypatch.setenv("LLM_MODE", "mock")
    cfg = config_module.LLMConfig.from_env()
    assert cfg.mock is True


def test_custom_preset(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "custom")
    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    monkeypatch.setenv("LLM_MODE", "real")
    monkeypatch.setenv("LLM_BASE_URL", "https://example.com/v1")
    monkeypatch.setenv("LLM_MODEL", "my-model")
    cfg = config_module.LLMConfig.from_env()
    assert cfg.base_url == "https://example.com/v1"
    assert cfg.model == "my-model"
    assert cfg.mock is False
