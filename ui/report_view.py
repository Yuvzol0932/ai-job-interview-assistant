"""面试报告页。"""

import streamlit as st

from services.report_store import list_reports, load_report


def render(client) -> None:
    st.title("📊 面试报告")
    current = st.session_state.get("current_report")
    if current is not None:
        st.subheader("本次面试报告")
        _render_report(current)

    reports = list_reports()
    if reports:
        st.divider()
        options = {
            f"{item['created_at']} ｜ {item['job_label']} ｜ {item['total_score']} 分": item[
                "report_id"
            ]
            for item in reports
        }
        choice = st.selectbox("历史报告", list(options))
        loaded = load_report(options[choice])
        if loaded is not None:
            st.subheader("历史报告")
            _render_report(loaded)
    else:
        st.info("完成一次模拟面试并生成报告后，报告会显示在这里。")


def _render_report(report) -> None:
    st.metric("总分", f"{report.total_score} / 100")
    for name, score in report.dimensions.items():
        st.progress(score / 10, text=f"{name}：{score} / 10")

    st.subheader("✅ 亮点")
    for item in report.strengths:
        st.markdown(f"- {item}")

    st.subheader("⚠️ 短板")
    for item in report.weaknesses:
        st.markdown(f"- {item}")

    st.subheader("📈 提升建议")
    for item in report.suggestions:
        st.markdown(f"- {item}")

    st.subheader("💡 参考答案")
    if not report.reference_answers:
        st.caption("本次报告未生成参考答案。")
    for index, item in enumerate(report.reference_answers, start=1):
        question = item.get("question", "")
        title = f"第 {index} 题" + (f"：{question[:36]}" if question else "")
        with st.expander(title):
            st.markdown(item.get("answer", "（无）"))
