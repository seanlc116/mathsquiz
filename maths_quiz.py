import streamlit as st
import random
import time

st.set_page_config(page_title="0-9 加減法速算練習", page_icon="🧮", layout="centered")

st.title("🧮 0-9 加減法速算練習")
st.markdown("**每15題會自動統計一次**，按 **S** 開始下一輪！")

# 初始化所有狀態
if "mode" not in st.session_state:
    st.session_state.mode = None
if "total_score" not in st.session_state:
    st.session_state.total_score = 0
if "total_questions" not in st.session_state:
    st.session_state.total_questions = 0
if "round_score" not in st.session_state:
    st.session_state.round_score = 0
if "round_questions" not in st.session_state:
    st.session_state.round_questions = 0
if "round_start_time" not in st.session_state:
    st.session_state.round_start_time = None
if "start_time" not in st.session_state:      # 整體開始時間
    st.session_state.start_time = None
if "end_time" not in st.session_state:
    st.session_state.end_time = None
if "a" not in st.session_state:
    st.session_state.a = 0
if "b" not in st.session_state:
    st.session_state.b = 0
if "correct" not in st.session_state:
    st.session_state.correct = 0
if "is_add" not in st.session_state:
    st.session_state.is_add = True
if "show_round_summary" not in st.session_state:
    st.session_state.show_round_summary = False

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

# 模式選擇畫面
if st.session_state.mode is None:
    st.subheader("請選擇練習模式")
    col1, col2 = st.columns(2)
    if col1.button("普通模式（無限練習）", use_container_width=True):
        st.session_state.mode = "normal"
        st.session_state.start_time = time.time()
        st.session_state.round_start_time = time.time()
        new_question()
        st.rerun()
    if col2.button("計時模式", use_container_width=True):
        st.session_state.mode = "timed"
        st.rerun()

# 計時模式時間選擇
elif st.session_state.mode == "timed" and st.session_state.start_time is None:
    minutes = st.slider("請選擇計時長度（秒）", 30, 180, 60, 30)
    if st.button("開始計時挑戰！", type="primary"):
        st.session_state.start_time = time.time()
        st.session_state.end_time = st.session_state.start_time + minutes
        st.session_state.round_start_time = time.time()
        new_question()
        st.rerun()

# 主遊戲畫面
else:
    # 計時模式顯示倒數
    if st.session_state.mode == "timed" and st.session_state.start_time:
        remaining = max(0, int(st.session_state.end_time - time.time()))
        st.progress(remaining / (st.session_state.end_time - st.session_state.start_time))
        st.caption(f"⏰ 剩餘時間：**{remaining}** 秒")

    # 顯示本輪與總計
    st.info(f"本輪已答：**{st.session_state.round_questions} / 15** 題　｜　總答題：**{st.session_state.total_questions}** 題")

    # 顯示題目
    if not st.session_state.show_round_summary:
        st.subheader(f"第 {st.session_state.total_questions + 1} 題")
        op = "+" if st.session_state.is_add else "-"
        st.markdown(f"<h2 style='text-align:center; color:#FF6B6B; font-size:3rem;'>{st.session_state.a} {op} {st.session_state.b} = ?</h2>", unsafe_allow_html=True)
        
        answer = st.text_input("你的答案（輸入後按 Enter）", key="answer_input", label_visibility="collapsed")
        
        if st.button("提交答案", type="primary", use_container_width=True) or (answer and st.session_state.get("answer_input") != ""):
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
                
                # 檢查是否滿15題
                if st.session_state.round_questions >= 15:
                    st.session_state.show_round_summary = True
                else:
                    new_question()
                
                st.rerun()
            except:
                st.warning("請輸入數字！")

    # === 每15題的統計畫面 ===
    else:
        round_elapsed = time.time() - st.session_state.round_start_time
        round_accuracy = round(st.session_state.round_score / 15 * 100, 1) if st.session_state.round_questions > 0 else 0
        round_ppm = round(st.session_state.round_score / (round_elapsed / 60), 1) if round_elapsed > 0 else 0

        st.success("🎉 **第15題完成！本輪統計如下：**")
        col1, col2, col3 = st.columns(3)
        col1.metric("本輪用時", f"{round(round_elapsed, 1)} 秒")
        col2.metric("本輪正確率", f"{round_accuracy}%", f"{st.session_state.round_score}/15")
        col3.metric("本輪速度", f"{round_ppm} 題/分鐘")

        st.markdown("---")
        st.subheader("總成績（累計所有輪）")
        total_accuracy = round(st.session_state.total_score / st.session_state.total_questions * 100, 1) if st.session_state.total_questions > 0 else 0
        total_ppm = round(st.session_state.total_score / ((time.time() - st.session_state.start_time)/60), 1) if (time.time() - st.session_state.start_time) > 0 else 0
        
        st.metric("總正確率", f"{total_accuracy}%", f"{st.session_state.total_score}/{st.session_state.total_questions} 題")
        st.metric("總平均速度", f"{total_ppm} 題/分鐘")

        st.markdown("### 👇 準備好了嗎？")
        if st.button("🚀 按 S 開始下一輪", type="primary", use_container_width=True):
            # 重置本輪資料
            st.session_state.round_score = 0
            st.session_state.round_questions = 0
            st.session_state.round_start_time = time.time()
            st.session_state.show_round_summary = False
            new_question()
            st.rerun()

    # 計時模式時間到自動結束
    if st.session_state.mode == "timed" and time.time() >= st.session_state.end_time:
        st.balloons()
        st.error("⏰ 時間到！練習結束！")
        st.stop()

    # 結束練習按鈕
    if st.button("結束全部練習並查看最終成績", type="secondary"):
        st.balloons()
        final_accuracy = round(st.session_state.total_score / st.session_state.total_questions * 100, 1) if st.session_state.total_questions > 0 else 0
        st.success(f"🎉 練習結束！總正確率 {final_accuracy}%（{st.session_state.total_score}/{st.session_state.total_questions} 題）")
        st.stop()

# 產生第一題
if st.session_state.mode and st.session_state.a == 0 and st.session_state.total_questions == 0:
    new_question()
