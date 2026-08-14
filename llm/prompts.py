"""各功能的提示词模板与模拟回复。"""

import json
import re

SYSTEM_DIAGNOSIS = """你是资深人力资源专家与职业规划师，擅长结合岗位要求与当地就业市场做简历诊断。请根据用户提供的简历内容、补充信息、目标岗位/地点和市场信息，输出客观、具体、可执行的专属优化方案。
要求：
1. 只输出一个 JSON 对象，不要输出任何其他文字。
2. JSON 字段名固定为英文：score、overall_evaluation、strengths、weaknesses、suggestions、optimized_examples、requirement_table、top_priorities、market_notes。
3. score 是 0-100 的整数，代表简历整体质量。
4. strengths、weaknesses、suggestions 各 4-6 条，每条一句话，必须结合简历中的具体内容。
5. optimized_examples 给 2-3 段改写示例（如经历描述、自我评价），体现 STAR 法则和量化成果。
6. requirement_table 是岗位要求对照表，数组内每项为 {"requirement": "岗位要求", "evidence": "简历中的对应证据（没有则写'未提供'）", "strength": "证据强度（强/中/弱/无）", "gap": "差距说明"}，列出 4-6 项最重要的岗位要求，严禁虚构简历中不存在的证据。
7. top_priorities 给出最优先修改建议 3 条，按性价比排序。
8. market_notes 用 2-4 句话给出目标地点/岗位的就业市场提示（如常见能力要求、竞争情况、求职建议），如果没有目标信息则基于岗位通用情况给出，并保持谨慎表述。"""

SYSTEM_QUESTIONS = """你是资深面试官，擅长为应届生设计面试题。请根据给定岗位生成面试题。
要求：
1. 只输出一个 JSON 对象：{"questions": ["题目1", "题目2", ...]}。
2. 题目数量必须与用户要求的数量一致。
3. 题目应包含：自我介绍类、岗位认知类、情景/行为类（用 STAR 作答）、优缺点类，其余考察综合能力。
4. 题目要具体、贴近真实面试，不要输出题号以外的说明。"""

SYSTEM_REPORT = """你是资深面试官，刚刚完成一场模拟面试。现在请以"面试官"的口吻，给候选人写一份复盘手记，而不是生成一份机械的评估报告。
要求：
1. 只输出一个 JSON 对象，不要输出其他文字。
2. JSON 字段固定为：dimensions、total_score、overall_impression、question_comments、growth_advice、closing。
3. dimensions 的键必须是：内容准确性、逻辑条理、表达清晰度、岗位匹配度、临场应变；值为 0-10 的整数。
4. total_score 是 0-100 的整数，综合五维度得出。
5. overall_impression 是一段 80-150 字的整体印象，像面试官当面点评：先说总体感觉，再点出最明显的优点和不足，口语化、具体，不要用"综上所述""首先其次"这类套话。
6. question_comments 与面试题一一对应，每项为 {"question": "原题", "comment": "对这一题回答的点评"}；comment 40-80 字，要具体引用回答中的细节，指出亮点或问题；若存在面试官追问，点评需覆盖追问环节表现。
7. growth_advice 给出 3-5 条具体可执行的提升建议，像导师给的建议。
8. closing 是一句收尾，像面试结束时的鼓励，简短自然。
9. 全程不得出现"作为AI""模型生成"等字样，也不得空泛表扬。"""

SYSTEM_JOB_MATCH = """你是校园招聘岗位匹配顾问。请根据候选人简历与候选岗位，为每个岗位输出匹配评分。
要求：
1. 只输出一个 JSON 对象：{"results": [{"id": "岗位ID", "score": 0-100, "reasons": ["原因"], "gaps": ["差距"]}]}。
2. score 代表当前简历投递该岗位的匹配度，依据岗位方向、地点、技能与经验综合判断。
3. reasons 给 2-3 条，必须结合简历中的具体信息；gaps 给 1-2 条，指出简历里尚未体现的岗位要求。
4. 结果按 score 从高到低排序。
5. 严禁虚构简历中不存在的经历与技能。"""


def build_diagnosis_messages(
    resume_text: str,
    target_job: str | None = None,
    target_location: str | None = None,
    market_notes: str | None = None,
) -> list[dict]:
    lines = []
    if target_job and target_job.strip():
        lines.append(f"目标岗位：{target_job}")
    if target_location and target_location.strip():
        lines.append(f"期望工作地点：{target_location}")
    if market_notes and market_notes.strip():
        lines.append(f"当地市场补充说明：{market_notes}")
    lines.append("简历内容：")
    lines.append(resume_text)
    user = "\n".join(lines)
    return [
        {"role": "system", "content": SYSTEM_DIAGNOSIS},
        {"role": "user", "content": user},
    ]


SYSTEM_CLARIFICATION = """你是资深人力资源专家。请分析用户提供的简历，找出其中缺失或模糊、但对求职和简历优化很重要的信息。
要求：
1. 只输出一个 JSON 对象：{"items": [{"field": "字段标识", "question": "向用户提问的中文问题", "hint": "填写示例或提示"}]}。
2. 优先检查：毕业院校（field 用 school）、期望工作地点（target_location）、意向从业方向（target_direction）、实习/项目时长、技能等级、证书、可量化的成果。
3. 只列出 3-6 项最重要的待确认信息；简历里已经写清楚的信息不要重复问。
4. field 必须是英文小写标识；question 用第一人称直接提问，例如"请问您的毕业院校是？"；hint 给一个简短示例。"""


def build_clarification_messages(resume_text: str) -> list[dict]:
    return [
        {"role": "system", "content": SYSTEM_CLARIFICATION},
        {"role": "user", "content": f"简历内容：\n{resume_text}"},
    ]


SYSTEM_FOLLOW_UP = """你是资深面试官。候选人刚回答了一道面试题，请根据他的回答生成一个针对性的追问，用来深挖细节、验证真实性和考察临场反应。
要求：
1. 只输出一个 JSON 对象：{"question": "追问内容"}。
2. 追问要具体，例如"你刚才提到组织了活动，具体负责了什么？遇到的最大困难是什么？"。
3. 不要重复原问题，一句话即可。"""


def build_follow_up_messages(
    job_label: str, question: str, answer: str
) -> list[dict]:
    user = (
        f"岗位：{job_label}\n"
        f"原问题：{question}\n"
        f"候选人回答：{answer}"
    )
    return [
        {"role": "system", "content": SYSTEM_FOLLOW_UP},
        {"role": "user", "content": user},
    ]


def build_questions_messages(
    job_label: str, resume_text: str, num_questions: int
) -> list[dict]:
    resume_line = f"\n候选人简历摘要：\n{resume_text}" if resume_text.strip() else ""
    user = f"岗位：{job_label}\n题目数量：{num_questions}{resume_line}"
    return [
        {"role": "system", "content": SYSTEM_QUESTIONS},
        {"role": "user", "content": user},
    ]


def build_report_messages(
    job_label: str,
    questions: list[str],
    answers: list[str],
    follow_ups: list[dict] | None = None,
) -> list[dict]:
    follow_ups = follow_ups or []
    lines = []
    for index, question in enumerate(questions, start=1):
        answer = answers[index - 1].strip() if index - 1 < len(answers) else ""
        lines.append(f"第{index}题：{question}")
        lines.append(f"候选人回答：{answer or '（未作答）'}")
        follow_up = follow_ups[index - 1] if index - 1 < len(follow_ups) else {}
        follow_up_question = str(follow_up.get("follow_up_question", "")).strip()
        follow_up_answer = str(follow_up.get("follow_up_answer", "")).strip()
        if follow_up_question:
            lines.append(f"面试官追问：{follow_up_question}")
            lines.append(f"候选人追问回答：{follow_up_answer or '（未作答）'}")
    user = f"岗位：{job_label}\n\n" + "\n".join(lines)
    return [
        {"role": "system", "content": SYSTEM_REPORT},
        {"role": "user", "content": user},
    ]


def build_job_match_messages(
    resume_text: str,
    target_job: str,
    target_location: str,
    jobs: list[dict],
) -> list[dict]:
    """把简历与候选岗位打包成岗位匹配提示词。"""
    lines = []
    if target_job and target_job.strip():
        lines.append(f"目标岗位：{target_job}")
    if target_location and target_location.strip():
        lines.append(f"期望工作地点：{target_location}")
    lines.append("简历内容：")
    lines.append(resume_text)
    lines.append("候选岗位：")
    for index, job in enumerate(jobs, start=1):
        requirements = "；".join(job.get("requirements") or []) or "未提供"
        tags = "、".join(job.get("tags") or []) or "未提供"
        lines.append(
            f"{index}. id={job.get('id', '')} | {job.get('title', '')} | "
            f"{job.get('company', '')} | {job.get('category', '')} | "
            f"{job.get('location', '')} | {job.get('salary', '')} | "
            f"要求：{requirements} | 关键词：{tags}"
        )
    return [
        {"role": "system", "content": SYSTEM_JOB_MATCH},
        {"role": "user", "content": "\n".join(lines)},
    ]


def _mock_diagnosis(job_label: str = "") -> str:
    job_note = f"（目标岗位：{job_label}）" if job_label else ""
    return json.dumps(
        {
            "score": 72,
            "overall_evaluation": "这是一份有一定基础的简历，结构基本完整，但在成果量化、经历描述和岗位匹配度上还有明显提升空间。"
            + job_note,
            "strengths": [
                "教育背景和基本技能信息完整，便于招聘方快速了解。",
                "有至少一段实习或项目经历，具备可展开的素材。",
                "经历描述使用了部分行业关键词。",
            ],
            "weaknesses": [
                "多数经历缺少量化成果，说服力不足。",
                "自我评价偏空泛，缺少具体证据支撑。",
                "经历描述以职责为主，未体现个人贡献与结果。",
            ],
            "suggestions": [
                "用 STAR 法则重写实习与项目经历，突出背景、任务、行动、结果。",
                "为关键成果补充数字，例如参与人数、提升比例、节约成本等。",
                "针对目标岗位提炼 3-4 个匹配关键词，并让经历与之呼应。",
            ],
            "requirement_table": [
                {
                    "requirement": "熟悉新媒体内容运营",
                    "evidence": "简历提到负责公众号运营",
                    "strength": "中",
                    "gap": "未说明阅读量、粉丝增长等量化结果",
                },
                {
                    "requirement": "具备活动策划与执行能力",
                    "evidence": "简历提到参与活动策划",
                    "strength": "中",
                    "gap": "未说明活动规模与个人贡献",
                },
                {
                    "requirement": "数据分析能力",
                    "evidence": "未提供",
                    "strength": "无",
                    "gap": "建议补充使用 Excel/数据工具分析运营数据的经历",
                },
            ],
            "top_priorities": [
                "给公众号运营经历补上阅读量、涨粉数等量化结果。",
                "用 STAR 法则重写活动策划经历，突出个人角色与结果。",
                "补充一项数据分析相关的课程作业或项目经历。",
            ],
            "market_notes": "当前市场营销类岗位普遍看重内容运营与数据分析结合的能力，一线城市竞争较激烈，建议突出可量化的实习成果，并关注本地中小企业与互联网公司的校招节奏。",
            "optimized_examples": [
                "改写前：负责公众号运营。\n改写后：独立运营校园公众号 6 个月，策划 24 期内容，阅读量从平均 500 提升至 2000+，最高单篇突破 8000。",
                "改写前：参与活动策划。\n改写后：作为核心成员策划 300 人规模迎新活动，负责宣传与物资统筹，活动满意度达 92%。",
            ],
        },
        ensure_ascii=False,
    )


def mock_diagnosis_response(messages: list[dict]) -> str:
    user = messages[-1]["content"]
    job_label = ""
    if "目标岗位：" in user:
        job_label = user.split("目标岗位：")[1].split("\n")[0].strip()
    return _mock_diagnosis(job_label)


def mock_clarification_response(messages: list[dict]) -> str:
    return json.dumps(
        {
            "items": [
                {
                    "field": "school",
                    "question": "请问您的毕业院校是？",
                    "hint": "例如：青岛理工大学",
                },
                {
                    "field": "target_location",
                    "question": "您期望在哪个城市工作？",
                    "hint": "例如：青岛",
                },
                {
                    "field": "target_direction",
                    "question": "您的意向从业方向是？",
                    "hint": "例如：市场营销",
                },
                {
                    "field": "intern_duration",
                    "question": "您的实习/项目具体持续了多久？",
                    "hint": "例如：2025年6月至9月，共4个月",
                },
                {
                    "field": "quantified_results",
                    "question": "实习或项目中有什么可量化的成果？",
                    "hint": "例如：阅读量提升 3 倍、服务 300 人",
                },
            ]
        },
        ensure_ascii=False,
    )


def mock_follow_up_response(messages: list[dict]) -> str:
    return json.dumps(
        {
            "question": "你刚才提到了相关经历，能具体说说你当时负责的部分和最终结果吗？"
        },
        ensure_ascii=False,
    )


def mock_questions_response(messages: list[dict]) -> str:
    user = messages[-1]["content"]
    count = 5
    for line in user.splitlines():
        if line.startswith("题目数量："):
            try:
                count = int(line.split("：")[1].strip())
            except ValueError:
                count = 5
    samples = [
        "请用 1 分钟做自我介绍，并说明你为什么适合这个岗位。",
        "你对我们这个岗位的工作内容有哪些理解？你觉得自己最大的优势是什么？",
        "请分享一次你在团队中遇到分歧并成功解决的经历，你具体做了什么？",
        "你认为自己最大的缺点是什么？你是如何改进的？",
        "如果入职后发现实际工作与你的预期差距很大，你会怎么办？",
        "请举一个你主动推动事情完成的例子，并说明结果。",
        "你如何看待加班和压力？",
        "未来 3 年你的职业规划是什么？",
    ]
    return json.dumps({"questions": samples[:count]}, ensure_ascii=False)


def mock_report_response(messages: list[dict]) -> str:
    return json.dumps(
        {
            "dimensions": {
                "内容准确性": 7,
                "逻辑条理": 7,
                "表达清晰度": 7,
                "岗位匹配度": 6,
                "临场应变": 7,
            },
            "total_score": 68,
            "overall_impression": "整体来看，你是一个有准备、有诚意的候选人，表达也算流畅。印象最深的是你愿意举自己的例子，但好几个回答停在'我做过'，没有说清楚'做成了什么'，这会让面试官很难判断你的真实水平。",
            "question_comments": [
                {
                    "question": "请用 1 分钟做自我介绍。",
                    "comment": "自我介绍结构完整，但信息密度偏低。你说自己'有实习经历'，却没点出实习里最亮眼的数字，这一题值得把简历里最强的成果前置。",
                },
                {
                    "question": "请分享一次你遇到分歧并解决的经历。",
                    "comment": "能举出具体场景，这是加分项。可惜你只说了'最后协调好了'，没有讲你具体做了哪个动作让局面转变，建议补上这一步。",
                },
            ],
            "growth_advice": [
                "把每个经历都按'背景-任务-动作-结果'过一遍，尤其是'动作'和'结果'要说满。",
                "自我介绍控制在 1 分钟内，把最有说服力的一个成果放在最前面。",
                "提前准备 3 个关于岗位的提问，面试结尾问出来，会显得你真的想清楚过这份工作。",
            ],
            "closing": "这轮练习里你已经能看出自己的问题在哪了，剩下的就是把它练成习惯。下次面试，记得先讲结果，再讲过程。",
        },
        ensure_ascii=False,
    )


def mock_job_match_response(messages: list[dict]) -> str:
    user = messages[-1]["content"]
    ids = re.findall(r"id=([A-Za-z0-9_-]+)", user)
    scores = [82, 74, 66, 58, 50, 44]
    results = []
    for index, job_id in enumerate(ids[:6]):
        score = scores[index] if index < len(scores) else 45
        results.append(
            {
                "id": job_id,
                "score": score,
                "reasons": [
                    "岗位方向与你的求职目标相关",
                    "简历中有对应岗位的关键词与经历",
                ],
                "gaps": [
                    "岗位要求中的部分技能未在简历中明确体现",
                ],
            }
        )
    return json.dumps({"results": results}, ensure_ascii=False)
