import streamlit as st
import json
import requests
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# ==========================================
# 1. 페이지 설정 및 세션 초기화
# ==========================================
st.set_page_config(page_title="에릭이의 습관 달력 & AI 루틴", page_icon="📅", layout="wide")

if "sticker_count" not in st.session_state:
    st.session_state.sticker_count = 0
if "reward_goal" not in st.session_state:
    st.session_state.reward_goal = "사나고 카페 가기"
if "quiz_cache" not in st.session_state:
    st.session_state.quiz_cache = None
if "cheer_cache" not in st.session_state:
    st.session_state.cheer_cache = None

# ==========================================
# 2. 커스텀 CSS 스타일링
# ==========================================
st.markdown("""
<style>
    .card-box {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #e9ecef;
    }
    .sticker-title {
        font-size: 1.15rem;
        font-weight: bold;
        color: #212529;
    }
    .sticker-badge {
        background-color: #ffe3e3;
        color: #e03131;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: bold;
    }
    .goal-label {
        font-weight: bold;
        color: #343a40;
        line-height: 40px;
        white-space: nowrap;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. Google Sheets 연동
# ==========================================
@st.cache_resource
def init_gsheets():
    try:
        creds_dict = json.loads(st.secrets["GCP_SERVICE_ACCOUNT"])
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(st.secrets["SPREADSHEET_KEY"]).sheet1
        return sheet
    except Exception:
        return None

sheet = init_gsheets()

if sheet and "gsheets_loaded" not in st.session_state:
    try:
        val = sheet.acell("B1").value
        st.session_state.sticker_count = int(val) if val else 0
        goal_val = sheet.acell("B2").value
        if goal_val:
            st.session_state.reward_goal = goal_val
        st.session_state.gsheets_loaded = True
    except Exception:
        pass

# ==========================================
# 4. Gemini API 호출 (gemini-3.1-flash-lite)
# ==========================================
api_key = st.secrets.get("GEMINI_API_KEY", "")

def call_gemini_api(prompt):
    if not api_key:
        return "Secrets에 GEMINI_API_KEY가 설정되어 있지 않습니다."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
        if response.status_code == 200:
            res_json = response.json()
            return res_json["candidates"][0]["content"]["parts"][0]["text"]
        elif response.status_code == 429:
            return "⚠️ 현재 요청량이 많아 일시적으로 대기 중입니다. 잠시 후 다시 시도해 주세요."
        else:
            return f"오류가 발생했습니다. (코드: {response.status_code})"
    except Exception as e:
        return f"통신 중 오류 발생: {str(e)}"

# ==========================================
# 5. 메인 앱 화면 렌더링
# ==========================================

st.title("📅 에릭이의 하루 습관 & AI 루틴")

# --- 1. 주간 시간표 섹션 ---
st.subheader("🎒 초등학교 5학년 주간 시간표")
timetable_data = {
    "교시 / 시간": ["1교시 (09:00~09:40)", "2교시 (09:50~10:30)", "3교시 (10:40~11:20)", "4교시 (11:30~12:10)", "점심시간 (12:10~13:00)", "5교시 (13:00~13:40)", "6교시 (13:50~14:30)"],
    "월요일": ["국어", "수학", "사회", "과학", "🍱 점심식사", "체육", "영어"],
    "화요일": ["수학", "국어", "음악", "미술", "🍱 점심식사", "미술", "자율"],
    "수요일": ["국어", "사회", "과학", "수학", "🍱 점심식사", "동아리", "-"],
    "목요일": ["영어", "수학", "국어", "체육", "🍱 점심식사", "사회", "도덕"],
    "금요일": ["과학", "국어", "수학", "음악", "🍱 점심식사", "영어", "학급회의"]
}
st.table(timetable_data)

# --- 2. 저녁 & 주말 루틴 체크리스트 ---
st.divider()
st.subheader("✅ 저녁 & 주말 루틴 체크리스트")

c_routine1, c_routine2 = st.columns(2)
with c_routine1:
    st.write("🌙 **평일 저녁 루틴**")
    st.checkbox("📚 학교 숙제 및 알림장 확인하기", key="chk_r1")
    st.checkbox("🎒 내일 책가방 및 준비물 미리 챙기기", key="chk_r2")
    st.checkbox("🪥 저녁 양치질 및 씻기", key="chk_r3")
    st.checkbox("🛌 10시 전에 잠자리에 들기", key="chk_r4")

with c_routine2:
    st.write("☀️ **주말 루틴**")
    st.checkbox("📖 주말 독서 30분 이상 하기", key="chk_r5")
    st.checkbox("🧹 내 방 책상 및 정돈하기", key="chk_r6")
    st.checkbox("🏃‍♂️ 야외 운동 또는 산책하기", key="chk_r7")
    st.checkbox("🎨 나만의 자유 여가 시간 보내기", key="chk_r8")

# --- 3. AI 칭찬 스티커 카운터 섹션 ---
st.divider()
with st.container():
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    
    col_title, col_top_btns = st.columns([3, 1])
    
    with col_title:
        percent = int((st.session_state.sticker_count / 30) * 100)
        st.markdown(
            f'<div class="sticker-title">🎨 AI 미션 달성 칭찬 스티커 카운터 '
            f'<span style="color:#e64980;">({st.session_state.sticker_count}/30개, {percent}%)</span></div>', 
            unsafe_allow_html=True
        )
        st.caption("오늘 미션을 성공했을 때 칭찬 스티커 카드를 생성하여 내 스티커북(30개판)에 저장합니다!")
        
    with col_top_btns:
        st.markdown('<div style="text-align: right;"><span class="sticker-badge">하루 1장 제한</span></div>', unsafe_allow_html=True)
        st.write("")
        if st.button("🔄 스티커 초기화", key="reset_sticker_btn", use_container_width=True):
            st.session_state.sticker_count = 0
            if sheet:
                try:
                    sheet.update_acell("B1", 0)
                except Exception:
                    pass
            st.toast("스티커가 0개로 초기화되었습니다!")
            st.rerun()

    st.write("")
    
    if st.button("🎲 스티커 그리러 가기", key="draw_sticker_main", use_container_width=True):
        if st.session_state.sticker_count < 30:
            st.session_state.sticker_count += 1
            if sheet:
                try:
                    sheet.update_acell("B1", st.session_state.sticker_count)
                except Exception:
                    pass
            st.toast(f"🎉 축하합니다! 스티커를 받았습니다. (현재 {st.session_state.sticker_count}개)")
            st.rerun()
        else:
            st.warning("이미 30개 스티커를 모두 모았습니다! 보상을 획득하세요!")

    st.write("")
    
    c_label, c_input, c_save = st.columns([1.2, 3.8, 0.6], vertical_alignment="center")
    
    with c_label:
        st.markdown('<div class="goal-label">🎯 달성 보상 목표 :</div>', unsafe_allow_html=True)
        
    with c_input:
        new_goal = st.text_input(
            "달성 보상 목표", 
            value=st.session_state.reward_goal, 
            label_visibility="collapsed",
            key="reward_goal_input"
        )
        
    with c_save:
        if st.button("📌", key="save_goal_btn", use_container_width=True):
            st.session_state.reward_goal = new_goal
            if sheet:
                try:
                    sheet.update_acell("B2", new_goal)
                except Exception:
                    pass
            st.toast("목표가 저장되었습니다!")

    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. AI 퀴즈 & 코칭 섹션 ---
st.divider()
st.subheader("💡 AI 에릭이 맞춤 코칭 & 퀴즈")

tab1, tab2 = st.tabs(["📝 오늘의 퀴즈 풀기", "📣 AI 음성 응원 메시지"])

with tab1:
    col_q1, col_q2 = st.columns([1, 3])
    with col_q1:
        if st.button("🎲 상식 퀴즈 생성", key="gen_quiz_btn", use_container_width=True):
            with st.spinner("퀴즈를 생성하고 있습니다..."):
                prompt = "초등학교 5학년 수준의 흥미로운 단답형 상식 퀴즈 1개와 정답, 간단한 해설을 한국어로 작성해줘."
                st.session_state.quiz_cache = call_gemini_api(prompt)
                
    with col_q2:
        if st.session_state.quiz_cache:
            st.info(st.session_state.quiz_cache)
        else:
            st.write("버튼을 눌러 오늘의 퀴즈를 불러오세요.")

with tab2:
    col_c1, col_c2 = st.columns([1, 3])
    with col_c1:
        if st.button("✨ 칭찬 한마디 받기", key="gen_cheer_btn", use_container_width=True):
            with st.spinner("응원 메시지 생성 중..."):
                prompt = "오늘 하루도 열심히 공부하고 루틴을 지킨 초등학교 5학년 에릭이에게 해줄 따뜻하고 유쾌한 칭찬 메시지 2줄을 써줘."
                st.session_state.cheer_cache = call_gemini_api(prompt)
                
    with col_c2:
        if st.session_state.cheer_cache:
            st.success(st.session_state.cheer_cache)
        else:
            st.write("버튼을 누르면 따뜻한 칭찬 한마디가 나옵니다.")
