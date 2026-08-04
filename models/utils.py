"""数据模型通用小工具。"""


def str_list(value) -> list[str]:
    """把任意值规范为字符串列表。"""
    if not isinstance(value, list):
        return []
    result = []
    for item in value:
        text = str(item).strip()
        if text:
            result.append(text)
    return result
