import streamlit as st
import random
import time

st.set_page_config(page_title="0-9 加減法速算練習", page_icon="🧮", layout="centered")

st.title("🧮 0-9 加減法速算練習")
st.markdown("**每15題自動統計一次**｜按 **S** 開始下一輪｜輸入答案後按 Enter 或點提交")

# ==================== 初始化 ====================
for key in ["mode", "total_score", "total_questions", "round_score", "round_questions",
            "round_start_time", "start_time", "end_time", "show_round_summary"]:
    if key not in st.session_state:
        st.session_state[key] = None if key in ["mode", "start_time", "end_time", "round_start_time"] else 0

if "a" not in st.session_state: st.session_state.a = 0
if "b" not in st.session_state: st.session_state.b = 0
if "correct" not in st.session_state: st.session_state.correct = 0
if "is_add" not in st.session_state: st.session_state.is_add = True

def new_question():
    st.session_state.a = random.randint(0, 9)
    st.session_state.b = random.randint(0, 9)
    st.session_state.is_add = random.choice([True, False])
    if st.session_state.is_add:
        st.session_state.correct = st.session_state.a + st.session_state.b
    else:
        if st.session_state.a < st.session_state.b:
            st.session_state.a, st.session_state.b = st.session_state.b, st.session_state.a
        st.session_state.correct = st.session_state.a - st.session_state.b

# ==================== 模式選擇 ====================
if st.session_state.mode is None:
    st.subheader("請選擇練習模式")
    c1, c2 = st.columns(2)
    if c1.button("普通模式（無限練習）", use_container_width=True):
        st.session_state.mode = "normal"
        st.session_state.start_time = time.time()
        st.session_state.round_start_time = time.time()
        new_question()
        st.rerun()
    if c2.button("計時模式", use_container_width=True):
        st.session_state.mode = "timed"
        st.rerun()

elif st.session_state.mode == "timed" and st.session_state.start_time is None:
    minutes = st.slider("計時長度（秒）", 30, 180, 60, 30)
    if st.button("開始計時挑戰！", type="primary"):
        st.session_state.start_time = time.time()
        st.session_state.end_time = st.session_state.start_time + minutes
        st.session_state.round_start_time = time.time()
        new_question()
        st.rerun()

# ==================== 主遊戲 ====================
else:
    if st.session_state.mode == "timed":
        remaining = max(0, int(st.session_state.end_time - time.time()))
        st.progress(remaining / (st.session_state.end_time - st.session_state.start_time))
        st.caption(f"⏰ 剩餘時間：**{remaining}** 秒")

    st.info(f"本輪已答：**{st.session_state.round_questions} / 15** 題　｜　總答題：**{st.session_state.total_questions}** 題")

    if not st.session_state.show_round_summary:
        st.subheader(f"第 {st.session_state.total_questions + 1} 題")
        op = "+" if st.session_state.is_add else "-"
        st.markdown(f"<h1 style='text-align:center; color:#FF4B4B;'>{st.session_state.a} {op} {st.session_state.b} = ?</h1>", unsafe_allow_html=True)

        with st.form("answer_form", clear_on_submit=True):
            answer = st.text_input("你的答案", key="current_answer", label_visibility="collapsed")
            submitted = st.form_submit_button("提交答案", type="primary", use_container_width=True)

            if submitted:
                try:
                    user_ans = int(answer.strip())
                    st.session_state.total_questions += 1
                    st.session_state.round_questions += 1

                    if user_ans == st.session_state.correct:
                        st.success("✅ 答對了！太棒了！")
                        st.session_state.total_score += 1
                        st.session_state.round_score += 1
                    else:
                        st.error(f"❌ 答錯了！正確答案是 **{st.session_state.correct}**")

                    if st.session_state.round_questions >= 15:
                        st.session_state.show_round_summary = True
                    else:
                        new_question()
                    st.rerun()
                except:
                    st.warning("請輸入數字！")

    # ==================== 15題統計畫面 ====================
    else:
        round_time = time.time() - st.session_state.round_start_time
        round_acc = round(st.session_state.round_score / 15 * 100, 1)
        round_ppm = round(st.session_state.round_score / (round_time / 60), 1) if round_time > 0 else 0

        st.success("🎉 **第15題完成！本輪統計**")
        c1, c2, c3 = st.columns(3)
        c1.metric("本輪用時", f"{round(round_time, 1)} 秒")
        c2.metric("本輪正確率", f"{round_acc}%", f"{st.session_state.round_score}/15")
        c3.metric("本輪速度", f"{round_ppm} 題/分鐘")

        st.divider()
        total_acc = round(st.session_state.total_score / st.session_state.total_questions * 100, 1) if st.session_state.total_questions > 0 else 0
        total_ppm = round(st.session_state.total_score / ((time.time() - st.session_state.start_time)/60), 1) if (time.time() - st.session_state.start_time) > 0 else 0
        st.metric("總正確率", f"{total_acc}%", f"{st.session_state.total_score}/{st.session_state.total_questions}")
        st.metric("總平均速度", f"{total_ppm} 題/分鐘")

        if st.button("🚀 按 S 開始下一輪", type="primary", use_container_width=True):
            st.session_state.round_score = 0
            st.session_state.round_questions = 0
            st.session_state.round_start_time = time.time()
            st.session_state.show_round_summary = False
            new_question()
            st.rerun()

    # 計時結束
    if st.session_state.mode == "timed" and time.time() >= st.session_state.end_time:
        st.balloons()
        st.error("⏰ 時間到！練習結束！")
        st.stop()

    if st.button("結束全部練習", type="secondary"):
        st.balloons()
        final_acc = round(st.session_state.total_score / st.session_state.total_questions * 100, 1) if st.session_state.total_questions > 0 else 0
        st.success(f"🎉 練習結束！總正確率 **{final_acc}%**（{st.session_state.total_score}/{st.session_state.total_questions} 題）")
        st.stop()

# 產生第一題
if st.session_state.mode and st.session_state.total_questions == 0 and st.session_state.a == 0:
    new_question()
