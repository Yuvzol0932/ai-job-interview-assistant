"""模拟面试页：逐题问答 + 追问机制。"""

import time

import streamlit as st

from services.interview_service import (
    InterviewError,
    finish_early,
    next_question,
    request_follow_up,
    start_interview,
    submit_follow_up_answer,
    submit_main_answer,
)
from services.job_catalog import CUSTOM_LABEL, job_labels
from services.report_service import ReportError, generate_report
from services.report_store import save_report


def render(client) -> None:
    st.title("🎤 模拟面试")
    state = st.session_state.get("interview_state")
    if state is None:
        _render_setup(client)
    elif state.status == "in_progress":
        _render_question(client, state)
    else:
        _render_finished(client, state)


def _render_setup(client) -> None:
    st.caption("选择岗位方向，AI 将像真实面试官一样逐题提问，答完还可以追问细节。")
    labels = job_labels()
    job_choice = st.selectbox("岗位方向", labels, index=0)
    custom = ""
    if job_choice == CUSTOM_LABEL:
        custom = st.text_input("请输入自定义岗位名称", placeholder="例如：跨境电商运营")

    resume_text = st.session_state.get("resume_content", "")
    use_resume = True
    if resume_text:
        use_resume = st.checkbox("带入简历诊断页的简历内容辅助出题（推荐）", value=True)

    num_questions = st.slider("题目数量", min_value=3, max_value=8, value=5)

    if st.button("开始面试", type="primary"):
        label = custom.strip() if job_choice == CUSTOM_LABEL else job_choice
        if not label:
            st.error("请先填写自定义岗位名称。")
            return
        try:
            with st.spinner("AI 正在出题…"):
                state = start_interview(
                    client,
                    label,
                    resume_text=resume_text if use_resume else "",
                    num_questions=num_questions,
                )
            st.session_state["interview_state"] = state
            st.rerun()
        except InterviewError as exc:
            st.error(str(exc))


def _render_question(client, state) -> None:
    st.caption(f"岗位：{state.job_label}")
    st.progress(
        state.answered_count / max(state.total, 1),
        text=f"已完成 {state.answered_count} / {state.total} 题",
    )

    if state.phase in ("main", "answered_main"):
        _render_main_question(client, state)
    else:
        _render_follow_up(client, state)

    if st.button("放弃本次面试"):
        st.session_state.pop("interview_state", None)
        st.rerun()


def _render_main_question(client, state) -> None:
    st.markdown(f"### 第 {state.current_index + 1} 题 / 共 {state.total} 题")
    st.markdown(state.current_question)

    if state.phase == "main":
        answer = st.text_area(
            "你的回答",
            height=160,
            key=f"main_answer_{state.current_index}",
            placeholder="请像在真实面试中一样完整作答…",
        )
        col1, col2 = st.columns([1, 1])
        if col1.button("提交答案", type="primary"):
            try:
                submit_main_answer(state, answer)
                st.rerun()
            except InterviewError as exc:
                st.error(str(exc))
        if col2.button("提前结束"):
            finish_early(state)
            st.rerun()
    else:
        st.caption("✅ 本题已作答，可选择让 AI 追问，或直接进入下一题。")
        col1, col2, col3 = st.columns([1, 1, 2])
        if col1.button("让 AI 追问", type="primary"):
            try:
                with st.spinner("AI 正在生成追问…"):
                    request_follow_up(client, state)
                st.rerun()
            except InterviewError as exc:
                st.error(str(exc))
        if col2.button("下一题"):
            try:
                next_question(state)
                st.rerun()
            except InterviewError as exc:
                st.error(str(exc))
        if col3.button("提前结束"):
            finish_early(state)
            st.rerun()


def _render_follow_up(client, state) -> None:
    st.markdown(f"### 第 {state.current_index + 1} 题 · 面试官追问")
    st.markdown(state.current_follow_up_question)

    if state.phase == "followup":
        answer = st.text_area(
            "你的回答",
            height=160,
            key=f"follow_answer_{state.current_index}",
            placeholder="针对追问作答…",
        )
        col1, col2 = st.columns([1, 1])
        if col1.button("提交追问回答", type="primary"):
            try:
                submit_follow_up_answer(state, answer)
                st.rerun()
            except InterviewError as exc:
                st.error(str(exc))
        if col2.button("提前结束"):
            finish_early(state)
            st.rerun()
    else:
        st.caption("✅ 追问已回答。")
        col1, col2 = st.columns([1, 1])
        if col1.button("下一题", type="primary"):
            try:
                next_question(state)
                st.rerun()
            except InterviewError as exc:
                st.error(str(exc))
        if col2.button("提前结束"):
            finish_early(state)
            st.rerun()


def _render_finished(client, state) -> None:
    st.success("面试已结束！")
    st.caption(
        f"岗位：{state.job_label}，共 {state.total} 题，回答 {state.answered_count} 题。"
    )

    if st.button("生成面试复盘", type="primary"):
        try:
            with st.status("正在整理这场面试…", expanded=True) as status:
                bar = st.progress(0.1, text="面试官正在翻看你的回答…")
                time.sleep(0.6)
                bar.progress(0.45, text="正在逐题点评…")
                time.sleep(0.6)
                bar.progress(0.8, text="正在写面试官手记…")
                report = generate_report(client, state)
                bar.progress(1.0, text="手记写好了")
            status.update(label="手记写好了", state="complete", expanded=False)
            save_report(report)
            st.session_state["current_report"] = report
            st.session_state.pop("interview_state", None)
            st.success("复盘已生成并保存到本地，可在「面试复盘」页查看。")
            st.rerun()
        except ReportError as exc:
            st.error(str(exc))

    if st.button("重新开始"):
        st.session_state.pop("interview_state", None)
        st.rerun()
