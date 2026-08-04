"""模型接口层：统一大模型客户端与提示词。"""

from .client import LLMClient, LLMError
from .config import LLMConfig

__all__ = ["LLMClient", "LLMError", "LLMConfig"]
