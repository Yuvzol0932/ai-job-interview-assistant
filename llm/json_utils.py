"""把大模型返回的文本稳健地解析为 JSON。"""

import json


def _try_parse(text: str):
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError, ValueError):
        return None


def extract_json(text: str):
    """从任意文本中提取第一个 JSON 对象或数组；失败返回 None。"""
    if not text:
        return None
    text = text.strip()

    # 去掉 ```json ... ``` 代码块围栏
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].strip().lower().lstrip("`").strip() in ("json", ""):
            text = "\n".join(lines[1:]).strip()
            if text.endswith("```"):
                text = text[:-3].strip()

    candidates = []
    first_brace = text.find("{")
    first_bracket = text.find("[")
    if first_brace != -1:
        candidates.append(text[first_brace:])
    if first_bracket != -1:
        candidates.append(text[first_bracket:])

    for candidate in candidates:
        parsed = _try_parse(candidate)
        if parsed is not None:
            return parsed
        # 尝试截断到最后一个闭合符
        last_close = max(candidate.rfind("}"), candidate.rfind("]"))
        if last_close > 0:
            parsed = _try_parse(candidate[: last_close + 1])
            if parsed is not None:
                return parsed
    return None
