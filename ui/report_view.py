"""面试复盘页：面试官手记 + 历史记录。"""

import streamlit as st

from services.report_store import delete_report, list_reports, load_report


def render(client) -> None:
    st.title("📝 面试复盘")

    current = st.session_state.get("current_report")
    if current is not None:
        st.caption(f"{current.job_label} · {current.created_at} · 本次复盘")
        _render_handnote(current)
        st.divider()

    reports = list_reports()
    if not reports:
        st.info("完成一次模拟面试并生成复盘后，这里会出现你的历史记录。")
        return

    st.subheader("历史复盘")
    for item in reports:
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.markdown(f"**{item['job_label']}**")
            col1.caption(f"{item['created_at']} · 总分 {item['total_score']} / 100")
            if col2.button("查看", key=f"view_{item['report_id']}"):
                st.session_state["viewing_report_id"] = item["report_id"]
            if col3.button("删除", key=f"del_{item['report_id']}"):
                delete_report(item["report_id"])
                if st.session_state.get("viewing_report_id") == item["report_id"]:
                    st.session_state.pop("viewing_report_id", None)
                st.rerun()

    viewing_id = st.session_state.get("viewing_report_id")
    if viewing_id:
        viewing = load_report(viewing_id)
        if viewing is None:
            st.session_state.pop("viewing_report_id", None)
        else:
            st.subheader("这份复盘")
            _render_handnote(viewing)


def _render_handnote(report) -> None:
    if not report.overall_impression and not report.question_comments:
        st.info("这份较早的复盘格式不兼容新版本，建议重新生成一份。")

    if report.overall_impression:
        st.markdown(f"> 这轮面试看下来，我的第一印象是——{report.overall_impression}")

    col1, col2 = st.columns([1, 3])
    col1.metric("总分", f"{report.total_score} / 100")
    with col2:
        st.caption("五维表现")
        for name, score in report.dimensions.items():
            st.progress(score / 10, text=f"{name} {score}/10")

    if report.question_comments:
        st.subheader("逐题点评")
        for index, item in enumerate(report.question_comments, start=1):
            with st.container(border=True):
                st.markdown(f"**第 {index} 题：{item.get('question', '')}**")
                st.markdown(item.get("comment", ""))

    if report.growth_advice:
        st.subheader("接下来可以这样练")
        for index, item in enumerate(report.growth_advice, start=1):
            st.markdown(f"{index}. {item}")

    if report.closing:
        st.markdown(f"> {report.closing}")
