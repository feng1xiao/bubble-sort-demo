
import streamlit as st
import time
import plotly.graph_objects as go
import math

st.set_page_config(page_title="冒泡排序虚拟仿真", layout="wide")

# 全局字体偏大，清晰
st.markdown("""
<style>
    html, body, [class*="css"] {
        font-size: 18px !important;
        line-height: 1.6 !important;
    }
    h1 {
        font-size: 34px !important;
        margin: 0.5rem 0 !important;
    }
    h2 {
        font-size: 24px !important;
        margin: 0.5rem 0 !important;
    }
    h3 {
        font-size: 20px !important;
        margin: 0.4rem 0 !important;
    }

    /* 输入框数字变大 */
    .stTextInput input {
        height: 48px !important;
        font-size: 20px !important;
    }

    /* 速度文字变大 */
    .stSlider label {
        font-size: 19px !important;
    }

    .stButton button {
        height: 46px !important;
        font-size: 18px !important;
    }

    .stApp {
        background: linear-gradient(135deg, #f0f9ff 0%, #dfe7fd 100%);
    }
    hr {
        margin: 0.7rem 0 !important;
    }
</style>
""", unsafe_allow_html=True)

left_col, right_col = st.columns([1.1, 1.3])

# ====================== 左侧：教程 + 最下方放实验报告 ======================
with left_col:
    st.title("📘 冒泡排序 全程教程")
    st.markdown("---")

    st.subheader("🔍 冒泡排序定义")
    st.success("""
**冒泡排序（Bubble Sort）**
是一种最简单的交换排序算法，重复比较相邻两个元素，若顺序错误则交换，较大元素会逐步“沉”到末尾，像气泡上浮一样，故名冒泡排序。
    """)

    st.markdown("---")
    st.subheader("📝 排序过程详解")
    st.info("""
从第一个元素开始，逐个比较相邻两个元素  
如果前一个 > 后一个，则交换位置  
每一轮结束，最大元素沉到最后  
对剩余元素重复上述过程  
无交换发生 → 排序完成
    """)

    st.markdown("---")
    st.subheader("🎯 动画颜色说明")
    st.markdown("""
🟦 蓝色：第一个待比较数字  
🟣 紫色：第二个待比较数字  
🟢 绿色：已确定，变绿后永远保持  
🔴 红色：交换过程中移动的数字  
⚫ 黑色：正常静态数字  
✅ 最终全部绿色：排序完成
    """)

    # ====================== 报告移到这里（左侧最下方）======================
    st.markdown("---")
    st.subheader("🧾 仿真实验报告")
    report_box = st.empty()

# ====================== 右侧：输入 + 控制 + 动画 + 实时数据 ======================
with right_col:
    st.title("🎈 冒泡排序仿真")
    st.subheader("输入数字（英文逗号分隔）：")
    user_input = st.text_input(
        "输入数字",
        value="5,3,8,4,2",
        label_visibility="collapsed"  # 隐藏 label，界面不变
    )

    try:
        arr = [int(x.strip()) for x in user_input.split(",")]
    except:
        arr = [5, 3, 8, 4, 2]
    n = len(arr)
    if n < 2:
        st.stop()

    def generate_steps(arr):
        a = arr.copy()
        steps = []
        ever_green = set()
        round_cnt = compare_cnt = swap_cnt = 0
        for round_num in range(n-1):
            round_cnt += 1
            for j in range(n - round_num - 1):
                compare_cnt += 1
                steps.append(("compare", j, j+1, a.copy(), list(ever_green), round_cnt, compare_cnt, swap_cnt))
                if a[j] > a[j+1]:
                    for k in range(12):
                        steps.append(("flying", j, j+1, a.copy(), list(ever_green), round_cnt, compare_cnt, swap_cnt, k/11))
                    a[j], a[j+1] = a[j+1], a[j]
                    swap_cnt += 1
                steps.append(("no_swap", j, j+1, a.copy(), list(ever_green), round_cnt, compare_cnt, swap_cnt))
            ever_green.add(n-1-round_num)
            steps.append(("round_end", -1,-1,a.copy(),list(ever_green),round_cnt,compare_cnt,swap_cnt))
        steps.append(("done", -1,-1,a.copy(),list(range(n)),round_cnt,compare_cnt,swap_cnt))
        return steps

    if "steps" not in st.session_state or st.session_state.get("last_arr") != arr:
        st.session_state.steps = generate_steps(arr)
        st.session_state.idx = 0
        st.session_state.playing = False
        st.session_state.last_arr = arr

    steps = st.session_state.steps
    max_idx = len(steps)-1
    idx = st.session_state.idx

    # 控制按钮
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        if st.button("▶ 播放"): st.session_state.playing=True
    with c2:
        if st.button("⏸ 暂停"): st.session_state.playing=False
    with c3:
        if st.button("🔄 重置"):
            st.session_state.idx=0
            st.session_state.playing=False
    with c4:
        speed = st.slider(
            "速度",
            min_value=0.05,
            max_value=0.3,
            value=0.12,
            label_visibility="collapsed"
        )

    st.markdown("---")
    # 动画
    ani_plt = st.empty()

    st.markdown("---")
    st.subheader("📊 实时仿真数据")
    d1,d2,d3 = st.columns(3)
    sim_round = d1.empty()
    sim_compare = d2.empty()
    sim_swap = d3.empty()

    tip_text = st.empty()

    def draw_frame(arr_cur, ever_green, mode, i, j, progress=0):
        fig = go.Figure()
        for x in range(n):
            num = arr_cur[x]
            y = num
            if mode == "done":
                col = "#2E8B57"
            elif x in ever_green:
                col = "#32CD32"
            elif x == i:
                col = "#42A5F5"
            elif x == j:
                col = "#9C27B0"
            else:
                col = "#EEEEEE"

            fig.add_trace(go.Scatter(
                x=[x], y=[y], mode="markers",
                marker=dict(size=72, color=col),
                showlegend=False
            ))
            if mode == "flying" and (x == i or x == j):
                pass
            else:
                fig.add_trace(go.Scatter(
                    x=[x], y=[y], mode="text",
                    text=str(num), textfont=dict(size=28, color="black"),
                    showlegend=False
                ))

        if mode == "flying":
            val_i = arr_cur[i]
            val_j = arr_cur[j]
            y_i = arr_cur[i]
            y_j = arr_cur[j]
            cx = (i + j) / 2
            cy = max(y_i, y_j) + 0.8
            t = progress
            x1 = (1-t)**2*i + 2*(1-t)*t*cx + t**2*j
            fy1 = (1-t)**2*y_i + 2*(1-t)*t*cy + t**2*y_j
            x2 = (1-t)**2*j + 2*(1-t)*t*cx + t**2*i
            fy2 = (1-t)**2*y_j + 2*(1-t)*t*cy + t**2*y_i
            fig.add_trace(go.Scatter(x=[x1], y=[fy1], mode="text", text=str(val_i), textfont=dict(size=30, color="red"), showlegend=False))
            fig.add_trace(go.Scatter(x=[x2], y=[fy2], mode="text", text=str(val_j), textfont=dict(size=30, color="red"), showlegend=False))

        fig.update_layout(
            height=330, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickvals=list(range(n))),
            yaxis=dict(visible=False, range=[min(arr)-2, max(arr)+3]),
            margin=dict(l=10,r=10,t=10,b=10)
        )
        return fig

    if st.session_state.playing and idx <= max_idx:
        step = steps[idx]
        mode, i, j, arr_cur, eg, rnd, cmp, swp = step[:8]
        progress = step[8] if mode == "flying" else 0

        sim_round.metric("轮次", rnd)
        sim_compare.metric("比较次数", cmp)
        sim_swap.metric("交换次数", swp)

        # 报告显示在左侧下方
        report_box.markdown(f"""
        初始数组：`{st.session_state.last_arr}`<br>
        当前数组：`{arr_cur}`<br>
        轮次：{rnd} 比较：{cmp} 交换：{swp}<br>
        时间复杂度：O(n²)
        """, unsafe_allow_html=True)

        fig = draw_frame(arr_cur, eg, mode, i, j, progress)
        ani_plt.plotly_chart(fig, use_container_width=True)

        if mode == "compare":
            tip_text.info(f"比较：{arr_cur[i]} ↔ {arr_cur[j]}")
            time.sleep(speed * 2)
        elif mode == "flying":
            tip_text.warning("交换中...")
            time.sleep(speed)
        elif mode == "no_swap":
            tip_text.success("顺序正确")
            time.sleep(speed * 1.2)
        elif mode == "round_end":
            tip_text.success("本轮完成")
            time.sleep(speed * 1.5)
        elif mode == "done":
            tip_text.success("🎉 排序完成！")
            st.session_state.playing = False

        st.session_state.idx += 1
        if st.session_state.idx > max_idx:
            st.session_state.idx = max_idx
        st.rerun()

    else:
        step = steps[idx]
        mode, i, j, arr_cur, eg, rnd, cmp, swp = step[:8]
        sim_round.metric("轮次", rnd)
        sim_compare.metric("比较次数", cmp)
        sim_swap.metric("交换次数", swp)

        report_box.markdown(f"""
        初始数组：`{st.session_state.last_arr}`<br>
        当前数组：`{arr_cur}`<br>
        轮次：{rnd} 比较：{cmp} 交换：{swp}<br>
        时间复杂度：O(n²)
        """, unsafe_allow_html=True)

        fig = draw_frame(arr_cur, eg, mode, i, j)
        ani_plt.plotly_chart(fig, use_container_width=True)
