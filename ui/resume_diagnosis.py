"""简历诊断页。"""

import streamlit as st

from services.resume_diagnosis import DiagnosisError, diagnose_resume
from services.resume_parser import ResumeParseError, parse_resume_file, parse_resume_text


def render(client) -> None:
    st.title("📄 简历诊断")
    st.caption("粘贴或上传简历，AI 会给出整体评价、优势、不足、修改建议和优化示例。")

    with st.form("resume_form"):
        source = st.radio("简历来源", ["粘贴文本", "上传文件"], horizontal=True)
        if source == "粘贴文本":
            text = st.text_area(
                "简历内容",
                height=260,
                placeholder="把简历全文粘贴到这里…",
            )
            uploaded = None
        else:
            text = ""
            uploaded = st.file_uploader("上传简历（支持 PDF 或 Word .docx）", type=["pdf", "docx"])
        target_job = st.text_input("目标岗位（选填）", placeholder="例如：产品经理、市场营销…")
        submitted = st.form_submit_button("开始诊断", type="primary")

    if submitted:
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
                st.warning("简历内容较短，诊断结果可能不够准确，建议补充完整后再诊断。")

            st.session_state["resume_content"] = resume.content
            with st.status("AI 正在诊断你的简历…", expanded=True) as status:
                box = st.empty()
                parts = []

                def on_token(token: str) -> None:
                    parts.append(token)
                    box.markdown("".join(parts))

                result = diagnose_resume(client, resume, target_job, on_token=on_token)
            status.update(label="诊断完成", state="complete", expanded=False)
            _render_result(result)
        except (ResumeParseError, DiagnosisError) as exc:
            st.error(str(exc))
        except Exception as exc:  # 兜底：不让界面崩溃
            st.error(f"发生未知错误：{exc}")


def _render_result(result) -> None:
    st.divider()
    st.metric("简历综合评分", f"{result.score} / 100")
    st.subheader("整体评价")
    st.write(result.overall_evaluation)

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
