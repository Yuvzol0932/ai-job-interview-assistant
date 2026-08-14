"""岗位聚合与 RSS 解析测试。"""

from services.job_aggregator import filter_jobs, jobs_from_rss_xml, load_jobs

RSS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>校招速递</title>
    <item>
      <title>新媒体运营实习生</title>
      <link>https://example.com/jobs/1</link>
      <description><p>负责公众号内容策划；每周到岗4天</p></description>
      <pubDate>2026-08-10</pubDate>
    </item>
  </channel>
</rss>"""


def test_seed_jobs_and_filters():
    jobs = load_jobs()
    assert len(jobs) >= 30
    categories = {job.category for job in jobs}
    assert {
        "产品经理",
        "市场营销",
        "运营",
        "财务",
        "人力资源",
        "行政文秘",
        "通用管培生",
    } <= categories

    marketing = filter_jobs(jobs, category="市场营销", location="青岛")
    assert marketing
    assert all(
        job.category == "市场营销" and job.location == "青岛" for job in marketing
    )

    keyword = filter_jobs(jobs, keyword="公众号")
    assert keyword
    assert any("公众号" in " ".join(job.tags) for job in keyword)


def test_rss_xml_parsing():
    jobs = jobs_from_rss_xml(RSS_XML, "https://example.com/feed")
    assert len(jobs) == 1
    job = jobs[0]
    assert job.title == "新媒体运营实习生"
    assert job.url == "https://example.com/jobs/1"
    assert job.id.startswith("rss-")
    assert job.source == "rss"
    assert job.requirements
    assert "<p>" not in " ".join(job.requirements)
