from llm.json_utils import extract_json


def test_extract_json_fenced():
    text = '```json\n{"a": 1}\n```'
    assert extract_json(text) == {"a": 1}


def test_extract_json_prose():
    text = '结果如下：{"a": 1, "b": [1, 2]} 以上就是全部。'
    assert extract_json(text) == {"a": 1, "b": [1, 2]}


def test_extract_json_list():
    assert extract_json('前面说明 [1, 2, 3] 后面') == [1, 2, 3]


def test_extract_json_invalid():
    assert extract_json("完全没有 JSON 的内容") is None
    assert extract_json("") is None
    assert extract_json(None) is None
