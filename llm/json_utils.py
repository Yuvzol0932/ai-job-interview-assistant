"""把大模型返回的文本稳健地解析为 JSON。"""

import json


def _try_parse(text: str):
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError, ValueError):
        return None


def _balanced_parse(text: str, start: int):
    """从 { 或 [ 开始扫描括号平衡，返回第一个完整结构；失败返回 None。"""
    open_char = text[start]
    close_char = "}" if open_char == "{" else "]"
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == open_char:
            depth += 1
        elif char == close_char:
            depth -= 1
            if depth == 0:
                return _try_parse(text[start : index + 1])
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

    first_brace = text.find("{")
    first_bracket = text.find("[")
    for start in (first_brace, first_bracket):
        if start == -1:
            continue
        parsed = _try_parse(text[start:])
        if parsed is not None:
            return parsed
        parsed = _balanced_parse(text, start)
        if parsed is not None:
            return parsed
    return None
