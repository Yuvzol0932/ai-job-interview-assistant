"""AI 求职面试助手——应用入口（界面层）。"""

from pathlib import Path

import streamlit as st

from llm.client import LLMClient
from llm.config import LLMConfig
from ui import home, interview, report_view, resume_diagnosis

st.set_page_config(page_title="AI 求职面试助手", page_icon="🎯", layout="wide")


def _load_css() -> None:
    css_path = Path(__file__).resolve().parent / "assets" / "style.css"
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def get_client() -> LLMClient:
    if "llm_client" not in st.session_state:
        config = LLMConfig.from_env()
        st.session_state["llm_client"] = LLMClient(config)
        st.session_state["llm_mock"] = config.mock
    return st.session_state["llm_client"]


client = get_client()
_load_css()

with st.sidebar:
    st.title("🎯 AI 求职面试助手")
    if st.session_state["llm_mock"]:
        st.warning("当前为模拟演示模式（未配置 API 密钥），结果均为演示数据。")
    else:
        st.success(f"已连接真实模型：{client.config.provider} / {client.config.model}")
    page = st.radio("功能导航", ["首页", "简历诊断", "模拟面试", "面试复盘"])

if page == "首页":
    home.render(client)
elif page == "简历诊断":
    resume_diagnosis.render(client)
elif page == "模拟面试":
    interview.render(client)
else:
    report_view.render(client)
