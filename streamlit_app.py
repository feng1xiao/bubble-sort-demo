import streamlit as st
import time
import plotly.graph_objects as go
import math

st.set_page_config(page_title="冒泡排序虚拟仿真", layout="wide")

# 全局样式
st.markdown("""
<style>
    html, body, [class*="css"] {
        font-size: 18px !important;
        line-height: 1.6 !important;
    }
    h1 { font-size: 34px !important; margin: 0.5rem 0 !important; }
    h2 { font-size: 24px !important; margin: 0.5rem 0 !important; }
    h3 { font-size: 20px !important; margin: 0.4rem 0 !important; }
    .stTextInput input { height: 48px !important; font-size: 20px !important; }
    .stSlider label { font-size: 19px !important; }
    .stButton button { height: 46px !important; font-size: 18px !important; }
    .stApp { background: linear-gradient(135deg, #f0f9ff 0%, #dfe7fd 100%); }
    hr { margin: 0.7rem 0 !important; }
</style>
""", unsafe_allow_html=True)

left_col, right_col = st.columns([1.1, 1.3])

# ====================== 左侧 ======================
with left_col:
    st.title("📘 冒泡排序 全程教程")
    st.markdown("---")
    st.subheader("🔍 冒泡排序定义")
    st.success("""
**冒泡排序（Bubble Sort）**
重复比较相邻元素，顺序错误则交换，较大元素逐步“沉”到末尾，像气泡上浮一样。
    """)
    st.markdown("---")
    st.subheader("📝 排序过程")
    st.info("""
1. 从头开始，相邻两两比较
2. 前 > 后 → 交换
3. 每轮结束，最大元素归位
4. 对剩余元素重复
5. 无交换 → 完成
    """)
    st.markdown("---")
    st.subheader("🎯 颜色说明")
    st.markdown("""
🟦 蓝色：待比较左
🟣 紫色：待比较右
🟢 绿色：已排序（永久）
🔴 红色：交换中移动
⚫ 灰色：未比较
✅ 全绿：完成
    """)
    st.markdown("---")
    st.subheader("🧾 仿真实验报告")
    report_box = st.empty()

# ====================== 右侧 ======================
with right_col:
    st.title("🎈 冒泡排序仿真")
    st.subheader("输入数字（英文逗号分隔）：")
    # ✅ 修复空 label 警告
    user_input = st.text_input(
        "输入数字",
        value="5,3,8,4,2",
        label_visibility="collapsed"
    )

    try:
        arr = [int(x.strip()) for x in user_input.split(",")]
    except:
        arr = [5, 3, 8, 4, 2]
    n = len(arr)
    if n < 2:
        st.stop()

    # 生成步骤（不变）
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
        # ✅ 修复空 label 警告
        speed = st.slider(
            "速度",
            min_value=0.03,
            max_value=0.3,
            value=0.08,
            label_visibility="collapsed"
        )

    st.markdown("---")
    # 🔥 唯一占位符
    ani_plt = st.empty()

    st.markdown("---")
    st.subheader("📊 实时数据")
    d1,d2,d3 = st.columns(3)
    sim_round = d1.empty()
    sim_compare = d2.empty()
    sim_swap = d3.empty()
    tip_text = st.empty()

    # ======================
    # 🔥 核心：只建1次Figure，原地更新
    # ======================
    def init_figure(arr_initial):
        fig = go.Figure()
        # 气泡（底层）
        fig.add_trace(go.Scatter(
            x=list(range(n)), y=arr_initial, mode="markers",
            marker=dict(size=72, color=["#EEEEEE"]*n),
            showlegend=False
        ))
        # 数字文本（上层）
        fig.add_trace(go.Scatter(
            x=list(range(n)), y=arr_initial, mode="text",
            text=[str(v) for v in arr_initial],
            textfont=dict(size=28, color="black"),
            showlegend=False
        ))
        # 交换浮动文本（顶层，初始隐藏）
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode="text",
            textfont=dict(size=32, color="red"),
            showlegend=False
        ))
        # 布局固定
        fig.update_layout(
            height=360,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickvals=list(range(n))),
            yaxis=dict(visible=False, range=[min(arr)-2, max(arr)+3]),
            margin=dict(l=10,r=10,t=10,b=10),
            # 🔥 关键：平滑过渡
            transition=dict(duration=100, easing="cubic-in-out")
        )
        return fig

    # 初始化一次图
    if "fig" not in st.session_state or st.session_state.get("last_arr") != arr:
        st.session_state.fig = init_figure(arr)
    fig = st.session_state.fig

    # ======================
    # 🔥 单帧更新（不重建）
    # ======================
    def update_frame(arr_cur, ever_green, mode, i, j, progress=0):
        n = len(arr_cur)
        colors = []
        for x in range(n):
            if mode == "done":
                colors.append("#2E8B57")
            elif x in ever_green:
                colors.append("#32CD32")
            elif x == i:
                colors.append("#42A5F5")
            elif x == j:
                colors.append("#9C27B0")
            else:
                colors.append("#EEEEEE")

        # 1. 更新气泡颜色、位置
        fig.data[0].x = list(range(n))
        fig.data[0].y = arr_cur
        fig.data[0].marker.color = colors

        # 2. 更新静态文字
        fig.data[1].x = list(range(n))
        fig.data[1].y = arr_cur
        fig.data[1].text = [str(v) for v in arr_cur]

        # 3. 交换动画：浮动红文（流畅）
        if mode == "flying":
            val_i = arr_cur[i]
            val_j = arr_cur[j]
            y_i = arr_cur[i]
            y_j = arr_cur[j]
            cx = (i + j) / 2
            cy = max(y_i, y_j) + 1.0
            t = progress
            # 贝塞尔曲线
            x1 = (1-t)**2*i + 2*(1-t)*t*cx + t**2*j
            fy1 = (1-t)**2*y_i + 2*(1-t)*t*cy + t**2*y_j
            x2 = (1-t)**2*j + 2*(1-t)*t*cx + t**2*i
            fy2 = (1-t)**2*y_j + 2*(1-t)*t*cy + t**2*y_i
            fig.data[2].x = [x1, x2]
            fig.data[2].y = [fy1, fy2]
            fig.data[2].text = [str(val_i), str(val_j)]
        else:
            # 隐藏浮动文字
            fig.data[2].x = [None]
            fig.data[2].y = [None]
            fig.data[2].text = []

        return fig

    # ======================
    # 主循环（无闪）
    # ======================
    if st.session_state.playing and idx <= max_idx:
        step = steps[idx]
        mode, i, j, arr_cur, eg, rnd, cmp, swp = step[:8]
        progress = step[8] if mode == "flying" else 0

        # 数据面板
        sim_round.metric("轮次", rnd)
        sim_compare.metric("比较", cmp)
        sim_swap.metric("交换", swp)

        # 报告
        report_box.markdown(f"""
        初始：`{st.session_state.last_arr}`<br>
        当前：`{arr_cur}`<br>
        轮次：{rnd} 比较：{cmp} 交换：{swp}<br>
        时间复杂度：O(n²)
        """, unsafe_allow_html=True)

        # 🔥 原地更新图（不重建）
        fig = update_frame(arr_cur, eg, mode, i, j, progress)
        ani_plt.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # 提示
        if mode == "compare":
            tip_text.info(f"比较：{arr_cur[i]} ↔ {arr_cur[j]}")
        elif mode == "flying":
            tip_text.warning("交换中...")
        elif mode == "no_swap":
            tip_text.success("顺序正确")
        elif mode == "round_end":
            tip_text.success(f"第{rnd}轮完成")
        elif mode == "done":
            tip_text.success("🎉 排序完成！")
            st.session_state.playing = False

        # 延时（更流畅）
        delay = speed
        if mode == "compare":
            delay *= 2.5
        elif mode == "no_swap":
            delay *= 1.5
        elif mode == "round_end":
            delay *= 2.0
        time.sleep(delay)

        # 步进
        st.session_state.idx = min(idx + 1, max_idx)
        st.rerun()

    else:
        # 静止帧
        step = steps[idx]
        mode, i, j, arr_cur, eg, rnd, cmp, swp = step[:8]
        sim_round.metric("轮次", rnd)
        sim_compare.metric("比较", cmp)
        sim_swap.metric("交换", swp)
        report_box.markdown(f"""
        初始：`{st.session_state.last_arr}`<br>
        当前：`{arr_cur}`<br>
        轮次：{rnd} 比较：{cmp} 交换：{swp}<br>
        时间复杂度：O(n²)
        """, unsafe_allow_html=True)
        fig = update_frame(arr_cur, eg, mode, i, j)
        ani_plt.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
