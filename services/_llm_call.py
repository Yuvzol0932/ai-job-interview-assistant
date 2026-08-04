"""业务层调用模型接口层的统一小工具。"""


def call_chat(client, messages: list[dict], mock_builder=None, on_token=None) -> str:
    """调用模型；传入 on_token 时使用流式输出并逐段回调。"""
    if on_token is None:
        return client.chat(messages, mock_builder=mock_builder)
    parts = []
    for chunk in client.chat_stream(messages, mock_builder=mock_builder):
        parts.append(chunk)
        on_token(chunk)
    return "".join(parts)
