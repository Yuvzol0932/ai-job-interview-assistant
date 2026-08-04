"""统一大模型客户端：负责调用、超时、重试与错误包装。"""

import time

from openai import (
    APIConnectionError,
    APITimeoutError,
    APIError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

from .config import LLMConfig


class LLMError(Exception):
    """模型调用失败的统一异常，信息对用户可读。"""


_RETRYABLE = (APIConnectionError, APITimeoutError, RateLimitError)


def _friendly_error(exc: Exception) -> LLMError:
    if isinstance(exc, AuthenticationError):
        return LLMError("API 密钥无效或已过期，请在 .env 中检查 LLM_API_KEY。")
    if isinstance(exc, RateLimitError):
        return LLMError("请求过于频繁或账户余额不足，请稍后重试或检查额度。")
    if isinstance(exc, APIConnectionError):
        return LLMError("无法连接模型服务，请检查网络后重试。")
    if isinstance(exc, APITimeoutError):
        return LLMError("模型响应超时，请稍后重试。")
    if isinstance(exc, APIError):
        status = getattr(exc, "status_code", None)
        if status == 401:
            return LLMError("API 密钥无效，请检查 LLM_API_KEY。")
        if status == 402:
            return LLMError("账户余额不足，请到模型平台充值后再试。")
        if status == 403:
            return LLMError("没有访问该模型的权限，请检查配置。")
        if status == 429:
            return LLMError("请求过于频繁，请稍后重试。")
        if status and status >= 500:
            return LLMError("模型服务暂时不可用，请稍后重试。")
        return LLMError(f"模型接口返回错误（{status}），请稍后重试。")
    return LLMError("模型调用失败，请稍后重试。")


class LLMClient:
    """统一客户端；mock=True 时返回模拟内容，不消耗真实额度。"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self._openai = None
        if not config.mock:
            self._openai = OpenAI(
                api_key=config.api_key or "sk-missing",
                base_url=config.base_url or None,
                timeout=config.timeout,
            )

    @property
    def mock(self) -> bool:
        return self.config.mock

    def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        mock_builder=None,
    ) -> str:
        if self.config.mock:
            return mock_builder(messages) if mock_builder else "（模拟模式：这是演示内容）"
        last_error = None
        for attempt in range(3):
            try:
                response = self._openai.chat.completions.create(
                    model=self.config.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content or ""
            except _RETRYABLE as exc:
                last_error = exc
                if attempt < 2:
                    time.sleep(1 + attempt)
            except Exception as exc:
                raise _friendly_error(exc) from exc
        raise _friendly_error(last_error)

    def chat_stream(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        mock_builder=None,
    ):
        """流式输出；逐段产出文本。"""
        if self.config.mock:
            yield mock_builder(messages) if mock_builder else "（模拟模式：这是演示内容）"
            return
        last_error = None
        for attempt in range(3):
            try:
                stream = self._openai.chat.completions.create(
                    model=self.config.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True,
                )
                for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        yield delta
                return
            except _RETRYABLE as exc:
                last_error = exc
                if attempt < 2:
                    time.sleep(1 + attempt)
            except Exception as exc:
                raise _friendly_error(exc) from exc
        raise _friendly_error(last_error)
