"""真机回归脚本：通过 API 完整跑通核心闭环（真实模型模式）。

用法：
1. 双击「启动新版前端.bat」启动服务（或自行启动 uvicorn）。
2. 确认 .env 中 LLM_MODE=real 且已配置密钥。
3. 在本目录执行： .venv\\Scripts\\python.exe scripts\\真实模型回归.py

脚本会打印每个步骤的耗时与关键结果，最后删除本次生成的测试报告。
"""

import time

import httpx

BASE = "http://127.0.0.1:8000"

RESUME_TEXT = (
    "张同学，青岛大学，市场营销专业，2026 届。"
    "在校担任学生会外联部部长，组织过三场校园活动，"
    "在本地一家公司做过两个月新媒体运营实习。"
)


def main() -> None:
    client = httpx.Client(base_url=BASE, timeout=180)

    def timed(label: str, method: str, path: str, **kwargs) -> dict:
        start = time.perf_counter()
        response = client.request(method, path, **kwargs)
        elapsed = time.perf_counter() - start
        if response.status_code >= 400:
            raise SystemExit(
                f"[{label}] HTTP {response.status_code}: {response.text[:300]}"
            )
        print(f"[{label}] {elapsed:.1f}s")
        return response.json()

    try:
        print("== 1/6 简历解析 ==")
        parsed = timed("parse", "POST", "/api/resume/parse", data={"text": RESUME_TEXT})
        resume_text = parsed["content"]
        print(f"   字符数 {parsed['char_count']}")

        print("== 2/6 缺失信息询问 ==")
        clarify = timed("clarify", "POST", "/api/resume/clarify", json={"resume_text": resume_text})
        items = clarify["items"]
        print(f"   待确认项 {len(items)} 条")
        for item in items:
            field = item["field"]
            answers = {
                "school": "青岛大学",
                "target_location": "青岛",
                "target_direction": "市场营销",
            }
            item["answer"] = answers.get(field, "有，可量化：阅读量提升 3 倍，新增关注 300 人。")

        print("== 3/6 专属诊断 ==")
        diagnosis = timed(
            "diagnose",
            "POST",
            "/api/resume/diagnose",
            json={
                "resume_text": resume_text,
                "items": items,
                "market_notes": "本地营销岗位普遍要求会数据分析与短视频剪辑",
                "target_job": "市场营销",
                "target_location": "青岛",
            },
        )
        print(f"   评分 {diagnosis['score']} / 100，最优先建议 {len(diagnosis['top_priorities'])} 条")

        print("== 4/6 模拟面试（3 题 + 1 次追问） ==")
        state = timed(
            "start",
            "POST",
            "/api/interview/start",
            json={"job_label": "产品经理", "num_questions": 3, "resume_text": ""},
        )
        for index in range(state["total"]):
            state = timed(
                "answer",
                "POST",
                "/api/interview/answer",
                json={"state": state, "answer": f"这是第 {index + 1} 题的完整回答。"},
            )
            if index == 0:
                state = timed("followup", "POST", "/api/interview/followup", json={"state": state})
                state = timed(
                    "followup-answer",
                    "POST",
                    "/api/interview/followup-answer",
                    json={"state": state, "answer": "这是对追问的回答。"},
                )
            if state["current_index"] + 1 < state["total"]:
                state = timed("next", "POST", "/api/interview/next", json={"state": state})
        state = timed("finish", "POST", "/api/interview/next", json={"state": state})
        print(f"   回答 {state['answered_count']} / {state['total']} 题")

        print("== 5/6 生成复盘 ==")
        report = timed("report", "POST", "/api/reports/generate", json={"state": state})
        print(f"   总分 {report['total_score']} / 100，五维：{report['dimensions']}")

        print("== 6/6 历史查看与清理 ==")
        listing = timed("list", "GET", "/api/reports")
        assert any(item["report_id"] == report["report_id"] for item in listing["reports"])
        timed("delete", "DELETE", f"/api/reports/{report['report_id']}")
        print("   已删除本次测试报告")

        print("\n[OK] 真机回归通过")
    finally:
        client.close()


if __name__ == "__main__":
    main()
