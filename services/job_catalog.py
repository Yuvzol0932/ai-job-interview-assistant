"""岗位方向常量。"""

JOB_CATEGORIES = [
    ("product", "产品经理", "负责产品规划、需求分析、项目推进、用户研究等"),
    ("marketing", "市场营销", "品牌推广、市场调研、活动策划、新媒体运营等"),
    ("operations", "运营", "用户运营、内容运营、活动运营、数据分析等"),
    ("finance", "财务", "财务核算、报表分析、税务、审计等"),
    ("hr", "人力资源", "招聘、培训、绩效、员工关系等"),
    ("admin", "行政文秘", "行政事务、文档管理、会务组织、办公支持等"),
    ("management_trainee", "通用管培生", "综合管理类岗位，考察综合素质与潜力"),
]

CUSTOM_LABEL = "自定义岗位"


def job_labels() -> list[str]:
    return [label for _, label, _ in JOB_CATEGORIES] + [CUSTOM_LABEL]


def job_description(label: str) -> str:
    for _, job_label, description in JOB_CATEGORIES:
        if job_label == label:
            return description
    return "自定义岗位方向，由候选人自行描述。"
