"""界面层共用小组件。"""

import streamlit as st


def render_thinking(label: str) -> None:
    """渲染一条带流动光效的思考动画条与灵动文字。"""
    st.markdown(
        (
            '<div class="thinking-wrap">'
            f'<div class="thinking-label">{label}</div>'
            '<div class="thinking-bar"></div>'
            "</div>"
        ),
        unsafe_allow_html=True,
    )
