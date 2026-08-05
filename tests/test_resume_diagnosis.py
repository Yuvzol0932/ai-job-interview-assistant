from models.resume import DiagnosisResult, ResumeData
from services.resume_diagnosis import diagnose_resume


class FakeClient:
    mock = False

    def __init__(self, text: str):
        self.text = text

    def chat(self, messages, **kwargs):
        return self.text

    def chat_stream(self, messages, **kwargs):
        yield self.text


EXTENDED_JSON = (
    '{"score": 72, "overall_evaluation": "整体不错", '
    '"strengths": ["s1"], "weaknesses": ["w1"], "suggestions": ["g1"], '
    '"optimized_examples": ["e1"], '
    '"requirement_table": [{"requirement": "新媒体运营", "evidence": "负责公众号", '
    '"strength": "中", "gap": "缺少量化"}], '
    '"top_priorities": ["补量化", "用STAR", "补数据"], '
    '"market_notes": "当地竞争激烈"}'
)


def test_diagnose_extended_fields():
    resume = ResumeData(content="简历内容")
    result = diagnose_resume(FakeClient(EXTENDED_JSON), resume, target_job="市场营销")
    assert isinstance(result, DiagnosisResult)
    assert result.score == 72
    assert len(result.requirement_table) == 1
    assert result.requirement_table[0]["requirement"] == "新媒体运营"
    assert result.requirement_table[0]["strength"] == "中"
    assert len(result.top_priorities) == 3
    assert "当地竞争激烈" in result.market_notes


def test_diagnose_missing_optional_fields():
    resume = ResumeData(content="简历内容")
    result = diagnose_resume(FakeClient('{"score": 60}'), resume)
    assert result.requirement_table == []
    assert result.top_priorities == []
    assert result.market_notes == ""
