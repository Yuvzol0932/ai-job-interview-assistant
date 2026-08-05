"""全局测试配置：所有测试不读取真实 .env，避免本地配置干扰。"""

import pytest

from llm import config as config_module


@pytest.fixture(autouse=True)
def no_dotenv(monkeypatch):
    monkeypatch.setattr(config_module, "load_dotenv", lambda *args, **kwargs: False)
