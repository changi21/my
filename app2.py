import streamlit as st
import datetime
import requests
import json
import pandas as pd
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(
    page_title="초등 5학년 스마트 루틴 & AI 코치",
    page_icon="📅",
    layout="wide"
)

# 2. API 키 가져오기
api_key = st.secrets.get("GEMINI_API_KEY", "")

# 3. 세션 상태 (메모리 저장소) 초기화
if "checklist_weekday" not in st.session_state:
    st.session_state.checklist_weekday = {
        "w1": ("🌅 아침 뇌 깨우기: 06:50 최태성 한국사 시청 또는 스트레칭", False),
        "w2": ("🏫 학원 미션: 학원 수강 및 안전한 이동 (도보/차량)", False),
        "w3": ("⚡ 70분 몰입 학습: 수학(30분)+영어(15분)+국어 어휘(15분) 완수", False),
        "w4": ("🎒 내일 준비: 21:10 책상 정돈 및 책가방 미리 챙기기", False),
        "w5": ("🛌 취침 골든타임: 21:20 샤워 ➡️ 22:00~22:10 소등 및 눕기", False),
    }

if "checklist_weekend" not in st.session_state:
    st.session_state.checklist_weekend = {
        "wk1": ("📝 주말 모닝 공부: 기상 직후 90분 학습 (수학+영어+독서) 완수", False),
        "wk2": ("⚾ 아빠와 야구: 13:00~15:30 햇빛 쬐며 신체활동 다녀오기", False),
        "wk3": ("🎮 게임 약속 준수: 3시간 쪼개기 규칙 (1.5시간 × 2회) 지키기", False),
        "wk4": ("📖 밤 몰입 독서: 20:00~21:00 부모님 운동 시간 동안 1시간 독서", False),
        "wk5": ("🌙 주말 취침 리듬 유지: 22:00~22:10 이전에 제자리에 눕기", False),
    }

if "stickers" not in st.session_state:
    st.session_state.stickers = []

if "reward_goal" not in st.session_state:
    st.session_state.reward_goal = "아빠와 프로야구 직관 가기 & 갖고 싶던 선물!"

# 4. 상단 헤더
today_str = datetime.date.today().strftime("%Y년 %m월 %d일")
st.title("📅 초등 5학년 주간 일정표 & AI 대시보드")
st.caption(f"📅 **오늘 날짜:** {today_str} | 수면 22:00 전 • 아침 최태성 한국사 시청 • 저녁 70분 스퍼트")

# 5. 메인 탭 구성 (Streamlit 전용 탭 사용으로 클릭 100% 작동)
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 대시보드", 
    "🎒 요일별 학원", 
    "🌙 저녁 루틴", 
    "☀️ 주말 일과", 
    "✅ 체크 & 기록", 
    "✨ AI 코치 & 퀴즈"
])

# ==========================================
# TAB 1: 대시보드
# ==========================================
with tab1:
    st.info("💡 **맞춤형 스마트 루틴 대시보드:** 학원 동선, 70분 저녁 집중 학습, 주말 야외활동 및 독서 루틴이 통합 관리됩니다.")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="권장 수면 시간", value="8.5시간", delta="22:00 ~ 06:30")
        st.caption("21:20 샤워 ➡️ 22:00 취침")
    with col2:
        st.metric(label="평일 저녁 집중 학습", value="70분", delta="20:10 ~ 21:20")
        st.caption("수학 30분 + 영어 15분 + 국어 15분")
    with col3:
        st.metric(label="주말 야외/신체 활동", value="2.5시간", delta="오후 13:00~")
        st.caption("아빠와 야구 & 야외활동")
    with col4:
        st.metric(label="주말 게임 시간 관리", value="3시간", delta="1.5h × 2회 쪼개기")
        st.caption("오전 1차 + 해질녘 2차")

    st.divider()

    # 차트 시각화 (Plotly 라이브러리로 Streamlit 안에서 완벽 렌더링)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📊 평일 하루 시간 배분 비율")
        df_pie = pd.DataFrame({
            "항목": ["수면 (8.5시간)", "학교/학원 (8시간)", "여유/이동/식사 (6.3시간)", "저녁몰입학습 (1.1시간)"],
            "시간": [8.5, 8.0, 6.3, 1.1]
        })
        fig_pie = px.pie(df_pie, values="시간", names="항목", color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        st.subheader("🎯 저녁 70분 몰입 학습 과목 구성")
        df_bar = pd.DataFrame({
            "과목": ["수학 (학원숙제)", "영어 (단어+학습지)", "국어 (어휘/독해)", "마무리 (가방/책상)"],
            "시간(분)": [30, 15, 15, 10]
        })
        fig_bar = px.bar(df_bar, x="과목", y="시간(분)", color="과목", text="시간(분)")
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()
    st.subheader("⚡ 하루 핵심 타임라인 한눈에 보기")
    t1, t2, t3, t4 = st.columns(4)
    with t1:
        st.success("🌅 **06:30 ~ 08:30 [아침]**\n\n기상 & 한국사 강의 시청\n\n할아버지 댁 이동 후 식사 ➡️ 08:22 등교")
    with t2:
        st.info("🏫 **08:30 ~ 18:30 [방과후]**\n\n학교 수업 & 학원 동선\n\n수학/피아노/미술 픽업 ➡️ 17:30 합기도")
    with t3:
        st.warning("🚘 **18:30 ~ 20:10 [귀가&식사]**\n\n부모님 픽업 & 저녁 식사\n\n18:40 픽업 ➡️ 19:15 집 도착 후 식사")
    with t4:
        st.error("🌙 **20:10 ~ 22:10 [저녁&취침]**\n\n70분 학습 & 22시 전 취침\n\n20:10 학습 ➡️ 21:20 샤워 ➡️ 22:00 취침")

# ==========================================
# TAB 2: 요일별 학원
# ==========================================
with tab2:
    st.subheader("🎒 방과 후 요일별 학원 일정 & 이동 동선")
    
    day_choice = st.radio("요일을 선택하세요:", ["월요일", "화요일", "수요일", "목요일", "금요일"], horizontal=True)
    
    schedules = {
        "월요일": [
            ("14:00 ~ 15:00", "하교 & 할아버지 댁 휴식", "학교 수업 종료 후 이동", "휴식"),
            ("15:00 ~ 17:00", "📐 수학학원", "픽업 차량 이용 이동", "학원"),
            ("17:00 ~ 17:30", "할아버지 댁 이동 & 간식", "휴식 및 합기도 준비", "이동"),
            ("17:30 ~ 18:30", "🥋 합기도 학원", "할아버지 댁에서 도보 3분", "운동"),
            ("18:30 ~ 19:15", "🚘 하원 픽업 & 집 이동", "18:40 픽업 ➡️ 19:15 집 도착", "픽업")
        ],
        "화요일": [
            ("14:00 ~ 15:00", "🎹 피아노 학원", "픽업 차량 이용 이동", "학원"),
            ("15:00 ~ 17:30", "🏠 할아버지 댁 여유시간", "💡 독서, 학교/학원 숙제 일부 사전 해결", "여유시간"),
            ("17:30 ~ 18:30", "🥋 합기도 학원", "할아버지 댁에서 도보 3분", "운동"),
            ("18:30 ~ 19:15", "🚘 하원 픽업 & 집 이동", "18:40 픽업 ➡️ 19:15 집 도착", "픽업")
        ],
        "수요일": [
            ("14:00 ~ 15:00", "🎹 피아노 학원", "픽업 차량 이용 이동", "학원"),
            ("15:00 ~ 17:00", "📐 수학 학원", "💡 피아노 학원 바로 옆 호실로 즉시 이동", "바로연결"),
            ("17:00 ~ 17:30", "할아버지 댁 이동", "잠시 휴식 후 이동", "휴식"),
            ("17:30 ~ 18:30", "🥋 합기도 학원", "할아버지 댁에서 도보 3분", "운동"),
            ("18:30 ~ 19:15", "🚘 하원 픽업 & 집 이동", "18:40 픽업 ➡️ 19:15 집 도착", "픽업")
        ],
        "목요일": [
            ("14:00 ~ 15:00", "🎹 피아노 학원", "픽업 차량 이용 이동", "학원"),
            ("15:00 ~ 17:30", "🏠 할아버지 댁 여유시간", "💡 독서, 역사 책 읽기 및 숙제 해결", "여유시간"),
            ("17:30 ~ 18:30", "🥋 합기도 학원", "할아버지 댁에서 도보 3분", "운동"),
            ("18:30 ~ 19:15", "🚘 하원 픽업 & 집 이동", "18:40 픽업 ➡️ 19:15 집 도착", "픽업")
        ],
        "금요일": [
            ("14:00 ~ 16:00", "🎨 미술 학원", "픽업 차량 이용 이동", "학원"),
            ("16:00 ~ 17:30", "🏠 할아버지 댁 휴식 & 간식", "자유시간 및 독서", "휴식"),
            ("17:30 ~ 18:30", "🥋 합기도 학원", "할아버지 댁에서 도보 3분", "운동"),
            ("18:30 ~ 19:15", "🚘 하원 픽업 & 집 이동", "18:40 픽업 ➡️ 19:15 집 도착", "픽업")
        ]
    }

    st.write(f"### 🗓️ {day_choice} 상세 일정")
    for time_str, name, detail, badge in schedules[day_choice]:
        st.markdown(f"- **`{time_str}` | {name}** : {detail} `[{badge}]`")

# ==========================================
# TAB 3: 저녁 루틴
# ==========================================
with tab3:
    st.subheader("🌙 저녁 시간대 루틴 시뮤레이션")
    plan_mode = st.radio("루틴 모드를 선택하세요:", ["Plan A (평소 루틴)", "Plan B (유연 루틴)"], horizontal=True)

    if "Plan A" in plan_mode:
        st.success("🟢 **Plan A: 저녁 준비가 바로 되는 평소 루틴**")
        st.write("1. **19:15 ~ 19:30** - 귀가 및 정돈 (손 씻기, 알림장/가방 정리)")
        st.write("2. **19:30 ~ 20:10** - 온 가족 저녁 식사 및 대화")
        st.write("3. **20:10 ~ 21:20** - ⚡ **자기주도 70분 몰입 학습** (수학 30m ➡️ 영어 15m ➡️ 국어 15m ➡️ 책가방 10m)")
        st.write("4. **21:20 ~ 21:50** - 🚿 샤워 및 취침 준비")
        st.write("5. **21:50 ~ 22:10** - 🛌 잠자리 취침 완료")
    else:
        st.warning("🟡 **Plan B: 퇴근이 늦거나 저녁 준비가 길어지는 유연 루틴**")
        st.write("1. **19:15 ~ 19:40** - 자기 관리 시간 (가방 정리 및 할 일 체크)")
        st.write("2. **19:40 ~ 20:10** - 📖 **선(先) 집중 학습 30분** (영어 단어 & 국어 독해 1장 먼저 작성)")
        st.write("3. **20:10 ~ 20:50** - 저녁 식사 및 식탁 정돈")
        st.write("4. **20:50 ~ 21:20** - 📐 **메인 학습 30분** (수학 문제집 마저 풀기)")
        st.write("5. **21:20 ~ 22:10** - 🚿 샤워 후 22:00 전후 취침")

# ==========================================
# TAB 4: 주말 일과
# ==========================================
with tab4:
    st.subheader("☀️ 주말 알찬 타임라인 (토/일)")
    weekend_choice = st.radio("주말 요일 선택:", ["토요일 타임라인", "일요일 타임라인 (예배 포함)"], horizontal=True)

    st.info("💡 **주말 원칙:** 기상 직후 모닝 90분 학습 완주 ➡️ 게임은 1.5시간씩 2회 쪼개기 ➡️ 밤 8시 몰입 독서!")
    
    if "토요일" in weekend_choice:
        st.write("- **06:30 ~ 07:00** : 기상 및 아침 뇌 깨우기")
        st.write("- **07:00 ~ 08:30** : 📝 **[주말 모닝 학습] 90분 몰입 완주** (수학+영어+독서)")
        st.write("- **08:30 ~ 09:00** : 🍚 온 가족 아침 식사")
        st.write("- **10:00 ~ 12:00** : 🎮 게임 & 자유시간 1차 (120분)")
        st.write("- **13:00 ~ 15:30** : ⚾ **[신체활동] 아빠와 야구 다녀오기**")
        st.write("- **16:30 ~ 18:00** : 🎮 게임 & 자유시간 2차 (90분)")
        st.write("- **20:00 ~ 21:00** : 📖 밤 몰입 독서 1시간 (부모님 운동 시간)")
        st.write("- **21:20 ~ 22:10** : 🚿 샤워 및 취침")
    else:
        st.write("- **06:30 ~ 07:00** : 기상 및 아침 뇌 깨우기")
        st.write("- **07:00 ~ 08:30** : 📝 **[주말 모닝 학습] 90분 몰입 완주**")
        st.write("- **09:00 ~ 10:00** : 🙏 가족 인터넷 예배 드리기")
        st.write("- **10:00 ~ 12:00** : 🎮 게임 & 자유시간 1차 (120분)")
        st.write("- **13:00 ~ 15:30** : ⚾ 야외활동 / 주말 외출")
        st.write("- **16:30 ~ 18:00** : 🎮 게임 & 자유시간 2차 (90분)")
        st.write("- **20:00 ~ 21:00** : 📖 밤 몰입 독서 1시간")
        st.write("- **21:20 ~ 22:10** : 🚿 샤워 및 취침")

# ==========================================
# TAB 5: 체크 & 기록
# ==========================================
with tab5:
    st.subheader("✅ 일일 실천 체크리스트")
    col_w, col_wk = st.columns(2)

    with col_w:
        st.write("### 📅 평일 필수 미션")
        for key, (text, val) in st.session_state.checklist_weekday.items():
            checked = st.checkbox(text, value=val, key=f"check_{key}")
            st.session_state.checklist_weekday[key] = (text, checked)
            
    with col_wk:
        st.write("### ☀️ 주말 필수 미션")
        for key, (text, val) in st.session_state.checklist_weekend.items():
            checked = st.checkbox(text, value=val, key=f"check_{key}")
            st.session_state.checklist_weekend[key] = (text, checked)

    w_count = sum(1 for _, val in st.session_state.checklist_weekday.values() if val)
    wk_count = sum(1 for _, val in st.session_state.checklist_weekend.values() if val)
    
    st.divider()
    st.write(f"🎉 **오늘의 미션 달성 상태:** 평일 ({w_count}/5 완료) | 주말 ({wk_count}/5 완료)")

# ==========================================
# TAB 6: AI 코치 & 퀴즈 (Gemini API 연동)
# ==========================================
with tab6:
    st.subheader("✨ Gemini AI 스마트 학습 코치")
    
    ai_tool = st.radio("원하는 AI 기능을 선택하세요:", ["🧠 1분 AI 퀴즈", "🔊 AI 응원 멘트", "🎨 칭찬 스티커 생성", "🔍 AI 궁금증 질의응답"], horizontal=True)

    if "1분 AI 퀴즈" in ai_tool:
        subject = st.selectbox("퀴즈 과목 선택:", ["📜 한국사능력검정시험 (한능검 기본)", "🔬 초등 5학년 과학", "🔤 초등 필수 영단어"])
        if st.button("✨ AI 퀴즈 생성하기"):
            if not api_key:
                st.error("Secrets에 GEMINI_API_KEY가 설정되어 있지 않습니다.")
            else:
                with st.spinner("Gemini가 퀴즈를 출제 중입니다..."):
                    try:
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
                        payload = {"contents": [{"parts": [{"text": f"{subject} 주제로 초등 5학년 맞춤 4지선다형 퀴즈 1개와 정답/해설을 만들어줘."}]}]}
                        res = requests.post(url, json=payload).json()
                        quiz_ans = res['candidates'][0]['content']['parts'][0]['text']
                        st.success("퀴즈 생성 완료!")
                        st.write(quiz_ans)
                    except Exception as e:
                        st.error(f"AI 호출 중 오류가 발생했습니다: {e}")

    elif "AI 응원 멘트" in ai_tool:
        sit = st.selectbox("현재 상황 선택:", ["🌅 아침 등교 전", "🌙 저녁 70분 공부 완수 후", "⚾ 주말 운동 완수 후"])
        if st.button("🎙️ AI 응원 메시지 받기"):
            if not api_key:
                st.error("Secrets에 GEMINI_API_KEY가 설정되어 있지 않습니다.")
            else:
                with st.spinner("AI 멘토가 응원 멘트를 작성 중입니다..."):
                    try:
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
                        payload = {"contents": [{"parts": [{"text": f"초등 5학년 학생이 '{sit}' 상황이야. 따뜻하고 에너지를 주는 응원 메시지 3줄을 작성해줘."}]}]}
                        res = requests.post(url, json=payload).json()
                        cheer_msg = res['candidates'][0]['content']['parts'][0]['text']
                        st.balloons()
                        st.info(cheer_msg)
                    except Exception as e:
                        st.error(f"오류 발생: {e}")

    elif "칭찬 스티커 생성" in ai_tool:
        prompt_input = st.text_input("스티커 주제 입력:", "한국사 탐험가 로봇과 야구하는 초등학생 캐릭터")
        if st.button("🖼️ 칭찬 스티커 발행"):
            st.session_state.stickers.append(prompt_input)
            st.success(f"🎉 '{prompt_input}' 스티커가 칭찬 스티커북에 추가되었습니다!")
        
        st.write("---")
        st.write(f"🏆 **내 칭찬 스티커북 ({len(st.session_state.stickers)}/30개 모음)**")
        st.caption(f"🎯 목표: {st.session_state.reward_goal}")
        st.write(st.session_state.stickers)

    elif "AI 궁금증 질의응답" in ai_tool:
        q_input = st.text_input("궁금한 역사/과학 질문을 적어보세요:", "이순신 장군의 3대 대첩이 뭐야?")
        if st.button("🔍 AI에게 질문하기"):
            if not api_key:
                st.error("Secrets에 GEMINI_API_KEY가 설정되어 있지 않습니다.")
            else:
                with st.spinner("백과사전을 탐색하는 중입니다..."):
                    try:
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
                        payload = {"contents": [{"parts": [{"text": f"초등 5학년 눈높이에 맞춰 쉬운 언어로 친절하게 답변해줘: {q_input}"}]}]}
                        res = requests.post(url, json=payload).json()
                        answer = res['candidates'][0]['content']['parts'][0]['text']
                        st.success("AI 답변 완료!")
                        st.write(answer)
                    except Exception as e:
                        st.error(f"오류 발생: {e}")
