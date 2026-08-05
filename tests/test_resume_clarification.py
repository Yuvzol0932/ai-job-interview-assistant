import pytest

from models.resume import ClarificationItem
from services.resume_clarification import (
    ClarificationError,
    generate_clarification_items,
    merge_profile,
)


class FakeClient:
    mock = False

    def __init__(self, text: str):
        self.text = text

    def chat(self, messages, **kwargs):
        return self.text


ITEMS_JSON = (
    '{"items": ['
    '{"field": "school", "question": "请问您的毕业院校是？", "hint": "例如：青岛理工大学"},'
    '{"field": "target_location", "question": "您期望在哪个城市工作？"},'
    '{"field": "intern_duration", "question": "实习持续了多久？"}'
    "]}"
)


def test_generate_clarification_items():
    client = FakeClient(ITEMS_JSON)
    items = generate_clarification_items(client, "简历文本")
    assert len(items) == 3
    assert items[0].field == "school"
    assert "毕业院校" in items[0].question
    assert items[0].hint == "例如：青岛理工大学"


def test_generate_clarification_invalid():
    client = FakeClient("不是 JSON")
    with pytest.raises(ClarificationError):
        generate_clarification_items(client, "简历文本")


def test_generate_clarification_empty_items():
    client = FakeClient('{"items": []}')
    with pytest.raises(ClarificationError):
        generate_clarification_items(client, "简历文本")


def test_generate_clarification_empty_resume():
    client = FakeClient(ITEMS_JSON)
    with pytest.raises(ClarificationError):
        generate_clarification_items(client, "   ")


def test_merge_profile_known_fields():
    items = [
        ClarificationItem(field="school", question="毕业院校？", answer="青岛理工大学"),
        ClarificationItem(field="target_location", question="城市？", answer="青岛"),
        ClarificationItem(field="intern_duration", question="时长？", answer="4个月"),
    ]
    profile, combined = merge_profile("原始简历", items, market_notes="本地岗位要求会数据分析")
    assert profile.school == "青岛理工大学"
    assert profile.target_location == "青岛"
    assert profile.market_notes == "本地岗位要求会数据分析"
    assert "毕业院校：青岛理工大学" in combined
    assert "期望工作地点：青岛" in combined
    assert "时长？：4个月" in combined


def test_merge_profile_empty_answers():
    items = [ClarificationItem(field="school", question="毕业院校？", answer="")]
    profile, combined = merge_profile("原始简历", items)
    assert profile.school == ""
    assert combined == "原始简历"
