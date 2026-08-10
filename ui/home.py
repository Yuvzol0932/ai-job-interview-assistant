"""首页：作品介绍与三步引导。"""

import streamlit as st


def render(client) -> None:
    st.title("把每一次练习，都变成下一次面试的底气。")
    st.caption("校园求职 · 面试练习室 ｜ 三步走完求职备战：诊断简历 → 模拟面试 → 拿到面试官手记。")

    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("求职闭环", "3 步")
    metric2.metric("岗位方向", "7+ 类")
    metric3.metric("面试评分", "5 维度")

    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.markdown("### ① 简历诊断")
            st.markdown("上传或粘贴简历，AI 先问清缺失信息，再给出专属优化方案。")
    with col2:
        with st.container(border=True):
            st.markdown("### ② 模拟面试")
            st.markdown("选择岗位方向，AI 像真实面试官一样逐题提问，还会追问细节。")
    with col3:
        with st.container(border=True):
            st.markdown("### ③ 面试复盘")
            st.markdown("以面试官手记的形式，给出点评、建议和下一步行动。")

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
