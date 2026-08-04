"""大模型配置：提供方预设 + 环境变量读取。"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

PROVIDER_PRESETS = {
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
    },
    "custom": {
        "base_url": None,
        "model": None,
    },
}


@dataclass
class LLMConfig:
    """模型配置（契约）。"""

    provider: str = "deepseek"
    base_url: str = "https://api.deepseek.com"
    api_key: str = ""
    model: str = "deepseek-chat"
    timeout: int = 60
    mock: bool = True

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """从环境变量 / .env 读取配置。"""
        load_dotenv()
        provider = os.getenv("LLM_PROVIDER", "deepseek").strip().lower()
        preset = PROVIDER_PRESETS.get(provider, PROVIDER_PRESETS["deepseek"])

        api_key = os.getenv("LLM_API_KEY", "").strip()
        base_url = (os.getenv("LLM_BASE_URL", "").strip() or preset["base_url"] or "")
        model = (os.getenv("LLM_MODEL", "").strip() or preset["model"] or "")
        try:
            timeout = int(os.getenv("LLM_TIMEOUT", "60"))
        except ValueError:
            timeout = 60

        mode = os.getenv("LLM_MODE", "").strip().lower()
        if mode == "real":
            mock = False
        elif mode == "mock":
            mock = True
        else:
            mock = not api_key  # 未配密钥时自动进入模拟演示模式

        return cls(
            provider=provider,
            base_url=base_url,
            api_key=api_key,
            model=model,
            timeout=timeout,
            mock=mock,
        )
