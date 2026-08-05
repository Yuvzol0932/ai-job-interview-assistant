"""首页：作品介绍与三步引导。"""

import streamlit as st


def render(client) -> None:
    st.title("🎯 AI 求职面试助手")
    st.markdown(
        "面向校园求职场景的智能应用，帮你**投递前发现问题、面试前实战练习**。"
        "三步完成求职备战：诊断简历 → 模拟面试 → 查看报告。"
    )

    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("求职闭环", "3 步")
    metric2.metric("岗位方向", "7+ 类")
    metric3.metric("面试评分", "5 维度")

    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.markdown("### ① 简历诊断")
            st.markdown("粘贴或上传简历，AI 找出问题、补全缺失信息并给出优化示例。")
    with col2:
        with st.container(border=True):
            st.markdown("### ② 模拟面试")
            st.markdown("选择岗位方向，AI 像真实面试官一样逐题提问、可追问细节。")
    with col3:
        with st.container(border=True):
            st.markdown("### ③ 面试报告")
            st.markdown("五个维度打分 + 参考回答 + 提升建议，报告本地保存可回看。")

    st.divider()
    st.markdown("### 适合谁用")
    st.markdown(
        "- 正在准备校招、实习面试的同学\n"
        "- 简历投出去没有回音、不知道问题出在哪的同学\n"
        "- 想提前熟悉面试节奏、练习表达的同学"
    )
    if client.mock:
        st.info("当前为**模拟演示模式**（未配置 API 密钥），所有结果均为演示数据；配置密钥后即可接入真实模型。")
    else:
        st.success(f"已连接真实模型：{client.config.provider} / {client.config.model}")
