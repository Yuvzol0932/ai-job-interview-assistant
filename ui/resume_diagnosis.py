"""简历诊断页：上传 → AI 询问缺失信息 → 生成专属优化方案。"""

import streamlit as st

from models.resume import ResumeData
from services.resume_clarification import (
    ClarificationError,
    generate_clarification_items,
    merge_profile,
)
from services.resume_diagnosis import DiagnosisError, diagnose_resume
from services.resume_parser import ResumeParseError, parse_resume_file, parse_resume_text

_DIAG_KEYS = [
    "diag_resume",
    "diag_clarify",
    "diag_done",
    "diag_result",
    "diag_target_job",
    "diag_target_location",
    "diag_market_notes",
]


def render(client) -> None:
    st.title("📄 简历诊断")
    st.caption("粘贴或上传简历 → AI 先找出没写清楚的地方 → 你补充后生成专属优化方案。")

    if "diag_resume" not in st.session_state:
        _render_upload(client)
    elif st.session_state.get("diag_done"):
        _render_result()
    else:
        _render_clarification(client)


def _reset() -> None:
    for key in _DIAG_KEYS:
        st.session_state.pop(key, None)


def _render_upload(client) -> None:
    with st.form("resume_upload"):
        source = st.radio("简历来源", ["粘贴文本", "上传文件"], horizontal=True)
        if source == "粘贴文本":
            text = st.text_area("简历内容", height=240, placeholder="把简历全文粘贴到这里…")
            uploaded = None
        else:
            text = ""
            uploaded = st.file_uploader("上传简历（支持 PDF 或 Word .docx）", type=["pdf", "docx"])
        target_job = st.text_input("目标岗位（选填）", placeholder="例如：产品经理、市场营销…")
        target_location = st.text_input("期望工作地点（选填）", placeholder="例如：青岛、杭州…")
        market_notes = st.text_area(
            "当地市场补充说明（选填）",
            height=80,
            placeholder="例如：了解到本地该岗位普遍要求会数据分析…",
        )
        analyze = st.form_submit_button("分析简历缺失信息", type="primary")
        skip = st.form_submit_button("跳过询问，直接诊断")

    if not (analyze or skip):
        return

    try:
        if source == "粘贴文本":
            resume = parse_resume_text(text)
        else:
            if uploaded is None:
                st.error("请先上传简历文件。")
                return
            resume = parse_resume_file(uploaded.name, uploaded.getvalue())
        if resume.is_empty:
            st.error("简历内容为空，请粘贴文本或上传文件。")
            return
        if resume.too_short:
            st.warning("简历内容较短，建议补充完整后再诊断。")
        st.session_state["diag_resume"] = resume
        st.session_state["diag_target_job"] = target_job.strip()
        st.session_state["diag_target_location"] = target_location.strip()
        st.session_state["diag_market_notes"] = market_notes.strip()
        st.session_state["resume_content"] = resume.content
    except ResumeParseError as exc:
        st.error(str(exc))
        return

    if skip:
        st.session_state["diag_clarify"] = []
        _run_diagnosis(client)
        return

    try:
        with st.spinner("AI 正在分析简历缺失信息…"):
            items = generate_clarification_items(client, resume.content)
        st.session_state["diag_clarify"] = items
        st.rerun()
    except ClarificationError as exc:
        st.error(str(exc))
        st.session_state["diag_clarify"] = []
        if st.button("直接诊断"):
            _run_diagnosis(client)


def _render_clarification(client) -> None:
    items = st.session_state.get("diag_clarify", [])
    st.markdown("### 简历里还差这些信息")
    st.caption("能填的填一下，不确定的可以留空跳过；填写内容只用于本次简历优化。")

    if items:
        for index, item in enumerate(items):
            item.answer = st.text_input(
                item.question,
                value=item.answer,
                placeholder=item.hint or "可不填",
                key=f"clarify_{index}",
            )

    market_notes = st.text_area(
        "当地市场补充说明（选填）",
        value=st.session_state.get("diag_market_notes", ""),
        height=80,
        key="clarify_market",
    )
    st.session_state["diag_market_notes"] = market_notes.strip()

    col1, col2, col3 = st.columns(3)
    if col1.button("确认并生成优化方案", type="primary"):
        _run_diagnosis(client)
    if col2.button("全部跳过，直接诊断"):
        for item in items:
            item.answer = ""
        _run_diagnosis(client)
    if col3.button("重新上传简历"):
        _reset()
        st.rerun()


def _run_diagnosis(client) -> None:
    resume = st.session_state["diag_resume"]
    items = st.session_state.get("diag_clarify", [])
    market_notes = st.session_state.get("diag_market_notes", "")
    _, combined = merge_profile(resume.content, items, market_notes)
    merged = ResumeData(
        content=combined,
        source_type=resume.source_type,
        filename=resume.filename,
    )
    try:
        with st.status("AI 正在生成专属优化方案…", expanded=True) as status:
            box = st.empty()
            parts = []

            def on_token(token: str) -> None:
                parts.append(token)
                box.markdown("".join(parts))

            result = diagnose_resume(
                client,
                merged,
                target_job=st.session_state.get("diag_target_job", ""),
                target_location=st.session_state.get("diag_target_location", ""),
                market_notes=market_notes,
                on_token=on_token,
            )
        status.update(label="优化方案生成完成", state="complete", expanded=False)
        st.session_state["diag_result"] = result
        st.session_state["diag_done"] = True
        st.rerun()
    except DiagnosisError as exc:
        st.error(str(exc))


def _render_result() -> None:
    result = st.session_state.get("diag_result")
    if result is None:
        st.info("暂无诊断结果。")
        return

    st.divider()
    st.metric("简历综合评分", f"{result.score} / 100")

    st.subheader("整体评价")
    st.write(result.overall_evaluation)

    if result.top_priorities:
        st.subheader("🔝 最优先修改建议")
        for index, item in enumerate(result.top_priorities, start=1):
            st.markdown(f"{index}. {item}")

    if result.requirement_table:
        st.subheader("📋 岗位要求对照表")
        rows = [
            {
                "岗位要求": item["requirement"],
                "简历证据": item["evidence"],
                "证据强度": item["strength"],
                "差距说明": item["gap"],
            }
            for item in result.requirement_table
        ]
        st.dataframe(rows, use_container_width=True, hide_index=True)

    if result.market_notes:
        st.subheader("🏙️ 当地市场提示")
        st.info(result.market_notes)
        st.caption("以上为 AI 参考信息，具体以官方招聘信息为准。")

    st.subheader("✅ 优势")
    for item in result.strengths:
        st.markdown(f"- {item}")

    st.subheader("⚠️ 不足")
    for item in result.weaknesses:
        st.markdown(f"- {item}")

    st.subheader("✍️ 修改建议")
    for item in result.suggestions:
        st.markdown(f"- {item}")

    with st.expander("优化示例（改写后的片段）"):
        for index, item in enumerate(result.optimized_examples, start=1):
            st.markdown(f"**示例 {index}**\n\n{item}")

    if st.button("再来一份"):
        _reset()
        st.rerun()
