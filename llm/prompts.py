"""各功能的提示词模板与模拟回复。"""

import json

SYSTEM_DIAGNOSIS = """你是资深人力资源专家与职业规划师，擅长简历诊断。请根据用户提供的简历内容和目标岗位，输出客观、具体、可执行的诊断结果。
要求：
1. 只输出一个 JSON 对象，不要输出任何其他文字。
2. JSON 字段名固定为英文：score、overall_evaluation、strengths、weaknesses、suggestions、optimized_examples。
3. score 是 0-100 的整数，代表简历整体质量。
4. strengths、weaknesses、suggestions 各 4-6 条，每条一句话，必须结合简历中的具体内容。
5. optimized_examples 给 2-3 段改写示例（如经历描述、自我评价），体现 STAR 法则和量化成果。"""

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
6. reference_answers 是与面试题一一对应的数组，每项为 {"question": "...", "answer": "高质量参考答案"}。"""


def build_diagnosis_messages(resume_text: str, target_job: str | None = None) -> list[dict]:
    job_line = f"目标岗位：{target_job}\n" if target_job and target_job.strip() else ""
    user = f"{job_line}简历内容：\n{resume_text}"
    return [
        {"role": "system", "content": SYSTEM_DIAGNOSIS},
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
    job_label: str, questions: list[str], answers: list[str]
) -> list[dict]:
    lines = []
    for index, question in enumerate(questions, start=1):
        answer = answers[index - 1].strip() if index - 1 < len(answers) else ""
        lines.append(f"第{index}题：{question}")
        lines.append(f"候选人回答：{answer or '（未作答）'}")
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
