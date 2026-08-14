"""简历岗位匹配服务测试。"""

from services.job_aggregator import load_jobs
from services.job_matcher import match_jobs


class FakeClient:
    mock = False

    def __init__(self, text: str):
        self.text = text

    def chat(self, messages, **kwargs):
        return self.text


def test_rule_matching_prefers_target_and_location():
    jobs = load_jobs()
    result = match_jobs(
        None,
        "市场营销专业，运营过公众号和小红书，会剪映与PS，期望在青岛工作",
        jobs,
        target_job="市场营销",
        target_location="青岛",
        limit=5,
    )
    assert result["strategy"] == "rules"
    assert result["jobs"]
    top = result["jobs"][0]
    assert top["category"] == "市场营销"
    assert top["location"] == "青岛"
    assert top["match_score"] >= 70
    assert top["match_reasons"]


def test_llm_rank_uses_model_scores():
    jobs = load_jobs()
    job_id = jobs[0].id
    fake = FakeClient(
        '{"results": [{"id": "%s", "score": 91, '
        '"reasons": ["方向匹配"], "gaps": ["缺少量化"]}]}' % job_id
    )
    result = match_jobs(fake, "做过产品需求与数据分析", jobs, limit=3)
    assert result["strategy"] == "llm"
    assert result["jobs"][0]["id"] == job_id
    assert result["jobs"][0]["match_score"] == 91
