"""API 依赖：提供大模型客户端。"""

from llm.client import LLMClient
from llm.config import LLMConfig


def get_client() -> LLMClient:
    """每个请求创建一个客户端，配置始终读取最新环境变量。"""
    return LLMClient(LLMConfig.from_env())
