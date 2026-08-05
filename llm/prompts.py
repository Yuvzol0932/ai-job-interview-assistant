"""各功能的提示词模板与模拟回复。"""

import json

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

SYSTEM_REPORT = """你是资深面试官与职业发展导师。请根据岗位、面试题和候选人回答，生成客观的面试评估报告。
要求：
1. 只输出一个 JSON 对象，不要输出其他文字。
2. JSON 字段固定为：dimensions、total_score、strengths、weaknesses、reference_answers、suggestions。
3. dimensions 的键必须是：内容准确性、逻辑条理、表达清晰度、岗位匹配度、临场应变；值为 0-10 的整数。
4. total_score 是 0-100 的整数，综合五维度得出。
5. strengths、weaknesses 各 3-5 条，结合具体回答；suggestions 3-5 条，给出可执行的提升建议。
6. reference_answers 是与面试题一一对应的数组，每项为 {"question": "...", "answer": "高质量参考答案"}；若存在面试官追问，评估需考虑追问环节表现，参考答案可包含对追问的应对。"""


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
    user = messages[-1]["content"]
    questions = []
    answers = []
    lines = user.splitlines()
    for line in lines:
        if line.startswith("第") and "题：" in line and "候选人回答" not in line:
            questions.append(line.split("题：", 1)[1].strip())
        elif line.startswith("候选人回答："):
            answers.append(line.split("候选人回答：", 1)[1].strip())
    reference = [
        {
            "question": question,
            "answer": "参考答案：先用一句话给出结论，再用 STAR 框架展开具体事例，最后落到与岗位的匹配点。",
        }
        for question in questions
    ]
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
            "strengths": [
                "回答基本完整，能够围绕问题展开。",
                "部分回答体现了具体经历，具备一定说服力。",
            ],
            "weaknesses": [
                "部分回答停留在泛泛而谈，缺少量化结果。",
                "岗位匹配度的表达不够突出。",
            ],
            "reference_answers": reference,
            "suggestions": [
                "用 STAR 法则重写关键经历，让回答更有画面感。",
                "提前研究目标岗位的职责，把回答与岗位要求挂钩。",
            ],
        },
        ensure_ascii=False,
    )
