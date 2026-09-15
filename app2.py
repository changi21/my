import datetime
import json
import random
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="스마트 루틴 & AI 대시보드",
    page_icon="📅",
    layout="wide",
)

# 2. PIN 번호 인증 시스템 (1306 설정)
SET_PIN = "1306"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown(
        """
        <style>
        .pin-box {
            max-width: 450px;
            margin: 60px auto;
            padding: 40px 30px;
            background: linear-gradient(145deg, #1e293b, #0f172a);
            border-radius: 24px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.4);
            border: 1px solid #334155;
            text-align: center;
            color: #f8fafc;
        }
        .pin-icon { font-size: 54px; margin-bottom: 10px; }
        .pin-title { font-size: 24px; font-weight: 700; color: #38bdf8; margin-bottom: 8px; }
        .pin-sub { font-size: 13px; color: #94a3b8; margin-bottom: 25px; }
        </style>
        <div class="pin-box">
            <div class="pin-icon">🔒</div>
            <div class="pin-title">스마트 루틴 & AI 대시보드</div>
            <div class="pin-sub">보안된 개인 루틴에 접근하려면 PIN 4자리를 입력하세요.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        pin_input = st.text_input(
            "🔑 PIN 번호 4자리 입력",
            type="password",
            max_chars=4,
            key="pin_in",
            help="설정된 4자리 보안 비밀번호를 입력해 주세요.",
        )
        if st.button("🔓 인증하고 접속하기", use_container_width=True):
            if pin_input == SET_PIN:
                st.session_state.authenticated = True
                st.success("인증 성공!")
                st.rerun()
            else:
                st.error("PIN 번호가 일치하지 않습니다. 다시 입력해 주세요.")
    st.stop()

# 3. 구글 시트 연동 설정
SHEET_ID = "1x5A3X2lGb5SFpHE5qspuetmdOsWMiP_mfnWY0ZqD6rc"
SHEET_CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=data"
)
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbxrG7rYb5WXHcXkbd20QsiWywCNM7GWbW7KVll2n88gP15kHVsCfAdF_Tcr7Uhc53eqRw/exec"

# 기본 일정 데이터 구조 정의
DEFAULT_SCHEDULES = {
    "월요일": [
        {
            "time": "14:00 ~ 15:00",
            "name": "하교 & 할아버지 댁 휴식",
            "detail": "학교 수업 종료 후 이동",
            "badge": "휴식",
        },
        {
            "time": "15:00 ~ 17:00",
            "name": "📐 수학학원",
            "detail": "픽업 차량 이용 이동",
            "badge": "학원",
        },
        {
            "time": "17:00 ~ 17:30",
            "name": "할아버지 댁 이동 & 간식",
            "detail": "휴식 및 합기도 준비",
            "badge": "이동",
        },
        {
            "time": "17:30 ~ 18:30",
            "name": "🥋 합기도 학원",
            "detail": "할아버지 댁에서 도보 3분",
            "badge": "운동",
        },
        {
            "time": "18:30 ~ 19:15",
            "name": "🚘 하원 픽업 & 집 이동",
            "detail": "18:40 픽업 ➡️ 19:15 집 도착",
            "badge": "픽업",
        },
    ],
    "화요일": [
        {
            "time": "14:00 ~ 15:00",
            "name": "🎹 피아노 학원",
            "detail": "픽업 차량 이용 이동",
            "badge": "학원",
        },
        {
            "time": "15:00 ~ 17:30",
            "name": "🏠 할아버지 댁 여유시간",
            "detail": "💡 독서, 학교/학원 숙제 사전 해결",
            "badge": "여유시간",
        },
        {
            "time": "17:30 ~ 18:30",
            "name": "🥋 합기도 학원",
            "detail": "할아버지 댁에서 도보 3분",
            "badge": "운동",
        },
        {
            "time": "18:30 ~ 19:15",
            "name": "🚘 하원 픽업 & 집 이동",
            "detail": "18:40 픽업 ➡️ 19:15 집 도착",
            "badge": "픽업",
        },
    ],
    "수요일": [
        {
            "time": "14:00 ~ 15:00",
            "name": "🎹 피아노 학원",
            "detail": "픽업 차량 이용 이동",
            "badge": "학원",
        },
        {
            "time": "15:00 ~ 17:00",
            "name": "📐 수학 학원",
            "detail": "💡 피아노 학원 바로 옆 호실로 즉시 이동",
            "badge": "바로연결",
        },
        {
            "time": "17:00 ~ 17:30",
            "name": "할아버지 댁 이동",
            "detail": "잠시 휴식 후 이동",
            "badge": "휴식",
        },
        {
            "time": "17:30 ~ 18:30",
            "name": "🥋 합기도 학원",
            "detail": "할아버지 댁에서 도보 3분",
            "badge": "운동",
        },
        {
            "time": "18:30 ~ 19:15",
            "name": "🚘 하원 픽업 & 집 이동",
            "detail": "18:40 픽업 ➡️ 19:15 집 도착",
            "badge": "픽업",
        },
    ],
    "목요일": [
        {
            "time": "14:00 ~ 15:00",
            "name": "🎹 피아노 학원",
            "detail": "픽업 차량 이용 이동",
            "badge": "학원",
        },
        {
            "time": "15:00 ~ 17:30",
            "name": "🏠 할아버지 댁 여유시간",
            "detail": "💡 독서, 역사 책 읽기 및 숙제 해결",
            "badge": "여유시간",
        },
        {
            "time": "17:30 ~ 18:30",
            "name": "🥋 합기도 학원",
            "detail": "할아버지 댁에서 도보 3분",
            "badge": "운동",
        },
        {
            "time": "18:30 ~ 19:15",
            "name": "🚘 하원 픽업 & 집 이동",
            "detail": "18:40 픽업 ➡️ 19:15 집 도착",
            "badge": "픽업",
        },
    ],
    "금요일": [
        {
            "time": "14:00 ~ 16:00",
            "name": "🎨 미술 학원",
            "detail": "픽업 차량 이용 이동",
            "badge": "학원",
        },
        {
            "time": "16:00 ~ 17:30",
            "name": "🏠 할아버지 댁 휴식 & 간식",
            "detail": "자유시간 및 독서",
            "badge": "휴식",
        },
        {
            "time": "17:30 ~ 18:30",
            "name": "🥋 합기도 학원",
            "detail": "할아버지 댁에서 도보 3분",
            "badge": "운동",
        },
        {
            "time": "18:30 ~ 19:15",
            "name": "🚘 하원 픽업 & 집 이동",
            "detail": "18:40 픽업 ➡️ 19:15 집 도착",
            "badge": "픽업",
        },
    ],
}

DEFAULT_EVENING = {
    "Plan A": [
        ("19:15 ~ 19:30", "귀가 및 정돈", "손 씻기, 알림장/가방 정리"),
        ("19:30 ~ 20:10", "저녁 식사", "온 가족 식사 및 대화"),
        (
            "20:10 ~ 21:20",
            "⚡ 자기주도 몰입 학습 (70분)",
            "수학(30m) ➡️ 영어(15m) ➡️ 국어/어휘(15m) ➡️ 내일가방(10m)",
        ),
        ("21:20 ~ 21:50", "🚿 샤워 & 취침 준비", "21:20 샤워 들어가기 및 소등 준비"),
        ("21:50 ~ 22:10", "🛌 잠자리 취침 완료", "22:00 ~ 22:10 사이 취침"),
    ],
    "Plan B": [
        (
            "19:15 ~ 19:40",
            "자기 관리 시간",
            "부모님 저녁 준비 동안 손 씻기 및 할 일 체크",
        ),
        (
            "19:40 ~ 20:10",
            "📖 선(先) 집중 학습 (30분)",
            "영어 단어 + 독해 1장 먼저 끝내기",
        ),
        ("20:10 ~ 20:50", "저녁 식사", "식사 및 식탁 정돈"),
        (
            "20:50 ~ 21:20",
            "📐 메인 학습: 수학 & 마무리",
            "수학 숙제 마무리 & 책가방 챙기기",
        ),
        ("21:20 ~ 22:10", "🚿 샤워 및 취침", "21:20 샤워 ➡️ 22:00 전후 취침"),
    ],
}

DEFAULT_WEEKEND = {
    "토요일": [
        ("06:30 ~ 07:00", "기상 및 아침 뇌 깨우기", "6시 30분~7시 사이 기상"),
        (
            "07:00 ~ 08:30",
            "📝 [주말 모닝 학습] 90분 몰입 완주",
            "수학+영어+독서",
        ),
        ("08:30 ~ 09:00", "🍚 아침 식사 및 정돈", "온 가족 아침 식사"),
        ("10:00 ~ 12:00", "🎮 게임 & 자유시간 1차 (120분)", "학습 완주 후 자유시간"),
        ("13:00 ~ 15:30", "⚾ [신체활동] 아빠와 야구", "햇빛 쬐며 신체 발달"),
        ("16:30 ~ 18:00", "🎮 게임 & 자유시간 2차 (90분)", "게임 시간 쪼개기 수칙"),
        ("20:00 ~ 21:00", "📖 밤 몰입 독서 1시간", "부모님 운동 시간 동안 독서"),
        ("21:20 ~ 22:10", "🚿 샤워 및 취침", "22:00 전후 취침"),
    ],
    "일요일": [
        ("06:30 ~ 07:00", "기상 및 아침 뇌 깨우기", "6시 30분~7시 사이 기상"),
        ("07:00 ~ 08:30", "📝 [주말 모닝 학습] 90분 몰입 완주", "수학+영어+독서"),
        ("09:00 ~ 10:00", "🙏 인터넷 예배", "가족 인터넷 예배 드리기"),
        ("10:00 ~ 12:00", "🎮 게임 & 자유시간 1차 (120분)", "자유시간"),
        ("13:00 ~ 15:30", "⚾ 야외활동 / 주말 외출", "야외활동"),
        ("16:30 ~ 18:00", "🎮 게임 & 자유시간 2차 (90분)", "게임 마감"),
        ("20:00 ~ 21:00", "📖 밤 몰입 독서 1시간", "차분한 독서 시간"),
        ("21:20 ~ 22:10", "🚿 샤워 및 취침", "월요일 준비 및 취침"),
    ],
}


# 구글 시트 전체 데이터 불러오기 (Read)
def load_all_sheet_data():
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        if not df.empty:
            row = df.iloc[0]
            stk_cnt = int(row.get("stickers_count", 0))
            goal = str(
                row.get(
                    "reward_goal",
                    "아빠와 프로야구 직관 가기 & 갖고 싶던 선물!",
                )
            )

            sch_raw = row.get("schedules_json", None)
            eve_raw = row.get("evening_json", None)
            wk_raw = row.get("weekend_json", None)
            chk_raw = row.get("checklist_json", None)

            sch = (
                json.loads(sch_raw)
                if pd.notna(sch_raw) and sch_raw
                else DEFAULT_SCHEDULES
            )
            eve = (
                json.loads(eve_raw)
                if pd.notna(eve_raw) and eve_raw
                else DEFAULT_EVENING
            )
            wk = (
                json.loads(wk_raw)
                if pd.notna(wk_raw) and wk_raw
                else DEFAULT_WEEKEND
            )

            if pd.notna(chk_raw) and chk_raw:
                chk_data = json.loads(chk_raw)
                w_chk = chk_data.get("weekday", None)
                wk_chk = chk_data.get("weekend", None)
            else:
                w_chk, wk_chk = None, None

            return stk_cnt, goal, sch, eve, wk, w_chk, wk_chk
    except Exception:
        pass
    return (
        0,
        "아빠와 프로야구 직관 가기 & 갖고 싶던 선물!",
        DEFAULT_SCHEDULES,
        DEFAULT_EVENING,
        DEFAULT_WEEKEND,
        None,
        None,
    )


# 구글 시트 데이터 전송 (Write)
def save_sheet_data(
    stickers_count=None,
    reward_goal=None,
    schedules=None,
    evening=None,
    weekend=None,
    checklist=None,
):
    params = {}
    if stickers_count is not None:
        params["stickers"] = stickers_count
    if reward_goal is not None:
        params["goal"] = reward_goal
    if schedules is not None:
        params["schedules"] = json.dumps(schedules, ensure_ascii=False)
    if evening is not None:
        params["evening"] = json.dumps(evening, ensure_ascii=False)
    if weekend is not None:
        params["weekend"] = json.dumps(weekend, ensure_ascii=False)
    if checklist is not None:
        params["checklist"] = json.dumps(checklist, ensure_ascii=False)

    try:
        requests.get(WEB_APP_URL, params=params, timeout=5)
    except Exception:
        pass


# 4. API 키 가져오기 & Gemini 호출
api_key = st.secrets.get("GEMINI_API_KEY", "")


def call_gemini_api(prompt):
    if not api_key:
        return "Secrets에 GEMINI_API_KEY가 설정되어 있지 않습니다."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(
            url, headers=headers, data=json.dumps(payload), timeout=15
        )
        res_json = response.json()

        if response.status_code == 200:
            return res_json["candidates"][0]["content"]["parts"][0]["text"]
        else:
            err_msg = res_json.get("error", {}).get("message", "알 수 없는 오류")
            return f"API 오류 ({response.status_code}): {err_msg}"
    except Exception as e:
        return f"통신 오류 발생: {e}"


# 5. 세션 상태 초기화 & 구글 시트 전체 동기화
(
    init_stk,
    init_goal,
    init_sch,
    init_eve,
    init_wk,
    init_w_chk,
    init_wk_chk,
) = load_all_sheet_data()

if "stickers" not in st.session_state:
    st.session_state.stickers = [
        {"icon": "🏆", "msg": "목표 완수!", "date": ""} for _ in range(init_stk)
    ]

if "reward_goal" not in st.session_state:
    st.session_state.reward_goal = init_goal

if "schedules" not in st.session_state:
    st.session_state.schedules = init_sch

if "evening_plans" not in st.session_state:
    st.session_state.evening_plans = init_eve

if "weekend_plans" not in st.session_state:
    st.session_state.weekend_plans = init_wk

if "checklist_weekday" not in st.session_state:
    st.session_state.checklist_weekday = init_w_chk if init_w_chk else {
        "w1": (
            "🌅 아침 뇌 깨우기: 06:50 최태성 한국사 시청 또는 스트레칭",
            False,
        ),
        "w2": ("🏫 학원 미션: 학원 수강 및 안전한 이동 (도보/차량)", False),
        "w3": (
            "⚡ 70분 몰입 학습: 수학(30분)+영어(15분)+국어 어휘(15분) 완수",
            False,
        ),
        "w4": (
            "🎒 내일 준비: 21:10 책상 정돈 및 책가방 미리 챙기기",
            False,
        ),
        "w5": (
            "🛌 취침 골든타임: 21:20 샤워 ➡️ 22:00~22:10 소등 및 눕기",
            False,
        ),
    }

if "checklist_weekend" not in st.session_state:
    st.session_state.checklist_weekend = (
        init_wk_chk
        if init_wk_chk
        else {
            "wk1": (
                "📝 주말 모닝 공부: 기상 직후 90분 학습 (수학+영어+독서)"
                " 완수",
                False,
            ),
            "wk2": (
                "⚾ 아빠와 야구: 13:00~15:30 햇빛 쬐며 신체활동 다녀오기",
                False,
            ),
            "wk3": (
                "🎮 게임 약속 준수: 3시간 쪼개기 규칙 (1.5시간 × 2회) 지키기",
                False,
            ),
            "wk4": (
                "📖 밤 몰입 독서: 20:00~21:00 부모님 운동 시간 동안 1시간 독서",
                False,
            ),
            "wk5": (
                "🌙 주말 취침 리듬 유지: 22:00~22:10 이전에 제자리에 눕기",
                False,
            ),
        }
    )

if "quiz_click_count" not in st.session_state:
    st.session_state.quiz_click_count = 0

if "last_sticker_date" not in st.session_state:
    st.session_state.last_sticker_date = ""

if "latest_draw_sticker" not in st.session_state:
    st.session_state.latest_draw_sticker = None

STICKER_ICONS = [
    "🏆",
    "⭐",
    "🥇",
    "🎯",
    "🚀",
    "👑",
    "🔥",
    "💎",
    "🎨",
    "⚾",
    "🥋",
    "📖",
    "🧠",
    "⚡",
    "🌟",
    "🦁",
    "🐯",
    "🦄",
    "🦅",
    "🥊",
    "🎮",
    "🧩",
    "💡",
    "🎓",
    "🍀",
    "🌈",
    "🎖️",
    "🎗️",
    "🏅",
    "✨",
]
STICKER_MSG = [
    "오늘도 목표 완수! 정말 대단해!",
    "꾸준함이 너의 최고의 무기야!",
    "끝까지 해내는 네가 진짜 영웅!",
    "매일매일 성장하는 모습이 멋져!",
    "오늘의 저녁 스퍼트 최고였어!",
    "어려운 퀴즈도 척척 풀다니 최고!",
    "차근차근 실력이 쌓이고 있어!",
    "약속을 지키는 네가 최고야!",
    "지치지 않고 완수한 스스로를 칭찬해!",
    "내일 더 멋지게 날아오르자!",
]

# 6. 상단 헤더 & 로그아웃
days_kor = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
today_idx = datetime.date.today().weekday()
today_name = days_kor[today_idx]
today_str = datetime.date.today().strftime("%Y년 %m월 %d일")

h_col1, h_col2 = st.columns([8, 1])
with h_col1:
    st.title("📅 주간 일정표 & AI 대시보드")
    st.caption(
        f"📅 **오늘 날짜:** {today_str} ({today_name}) | 수면 22:00 전 • 아침 최태성"
        " 한국사 시청 • 저녁 70분 스퍼트"
    )
with h_col2:
    if st.button("🔒 잠금"):
        st.session_state.authenticated = False
        st.rerun()

# 7. 메인 탭 구성
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 대시보드",
    "🎒 요일별 학원",
    "🌙 저녁 루틴",
    "☀️ 주말 일과",
    "✅ 체크 & 기록",
    "✨ AI 코치 & 퀴즈",
])

# ==========================================
# TAB 1: 대시보드
# ==========================================
with tab1:
    selected_day = st.radio(
        "요일을 선택하세요:",
        days_kor,
        index=today_idx,
        horizontal=True,
        key="dash_day_radio",
    )

    is_weekend = selected_day in ["토요일", "일요일"]

    if is_weekend:
        st.info(
            f"💡 **[{selected_day} 주말 루틴 대시보드]** 주말 모닝 90분 몰입"
            " 학습, 아빠와 신체활동, 게임 3시간 쪼개기 규칙이 적용됩니다."
        )

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                label="권장 수면 시간", value="8.5시간", delta="22:00 ~ 06:30"
            )
            st.caption("21:20 샤워 ➡️ 22:00 취침")
        with col2:
            st.metric(
                label="주말 모닝 학습", value="90분", delta="07:00 ~ 08:30"
            )
            st.caption("수학 + 영어 + 독서 완주")
        with col3:
            st.metric(
                label="야외 / 신체활동",
                value="2.5시간",
                delta="13:00 ~ 15:30",
            )
            st.caption("아빠와 야구 & 햇빛 쬐기")
        with col4:
            st.metric(
                label="게임 시간 관리",
                value="3시간",
                delta="1.5h × 2회 쪼개기",
            )
            st.caption("오전 1차 + 해질녘 2차")

        st.divider()

        c1, c2 = st.columns(2)
        with c1:
            st.subheader(f"📊 {selected_day} 시간 배분 비율")
            df_pie = pd.DataFrame({
                "항목": [
                    "수면 (8.5시간)",
                    "모닝학습 & 독서 (2.5시간)",
                    "야외활동 & 게임 (5.5시간)",
                    "식사 & 여유 (7.5시간)",
                ],
                "시간": [8.5, 2.5, 5.5, 7.5],
            })
            fig_pie = px.pie(
                df_pie,
                values="시간",
                names="항목",
                color_discrete_sequence=px.colors.qualitative.Set3,
            )
            fig_pie.update_traces(
                textposition="inside", textinfo="percent+label"
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with c2:
            st.subheader(f"🎯 {selected_day} 주요 활동 시간 구성")
            df_bar = pd.DataFrame({
                "활동": [
                    "모닝 학습",
                    "게임 1차",
                    "야외/야구",
                    "게임 2차",
                    "밤 독서",
                ],
                "시간(분)": [90, 120, 150, 90, 60],
            })
            fig_bar = px.bar(
                df_bar,
                x="활동",
                y="시간(분)",
                color="활동",
                text="시간(분)",
                color_discrete_sequence=px.colors.qualitative.Bold,
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        st.divider()
        st.subheader(f"⚡ {selected_day} 실시간 타임라인")

        wk_items = st.session_state.weekend_plans.get(selected_day, [])
        cols = st.columns(min(len(wk_items), 4))
        for idx, (t, n, d) in enumerate(wk_items[:4]):
            with cols[idx]:
                st.success(f"**`{t}`**\n\n**{n}**\n\n{d}")

    else:
        st.info(
            f"💡 **[{selected_day} 평일 루틴 대시보드]** 학교/학원 동선 및 저녁"
            " 70분 몰입 학습 루틴이 적용됩니다."
        )

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                label="권장 수면 시간", value="8.5시간", delta="22:00 ~ 06:30"
            )
            st.caption("21:20 샤워 ➡️ 22:00 취침")
        with col2:
            st.metric(
                label="저녁 집중 학습", value="70분", delta="20:10 ~ 21:20"
            )
            st.caption("수학 30분 + 영어 15분 + 국어 15분")
        with col3:
            sch_list = st.session_state.schedules.get(selected_day, [])
            st.metric(
                label=f"{selected_day} 일정 개수",
                value=f"{len(sch_list)}개",
                delta="학원 및 동선",
            )
            st.caption("요일별 학원 탭 연동")
        with col4:
            st.metric(
                label="목표 취침 시간", value="22:00 전", delta="소등 준비"
            )
            st.caption("수면 골든타임 준수")

        st.divider()

        c1, c2 = st.columns(2)
        with c1:
            st.subheader(f"📊 {selected_day} 평일 시간 배분 비율")
            df_pie = pd.DataFrame({
                "항목": [
                    "수면 (8.5시간)",
                    "학교/학원 (8시간)",
                    "여유/이동/식사 (6.3시간)",
                    "저녁몰입학습 (1.1시간)",
                ],
                "시간": [8.5, 8.0, 6.3, 1.1],
            })
            fig_pie = px.pie(
                df_pie,
                values="시간",
                names="항목",
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig_pie.update_traces(
                textposition="inside", textinfo="percent+label"
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with c2:
            st.subheader("🎯 저녁 70분 몰입 학습 과목 구성")
            df_bar = pd.DataFrame({
                "과목": [
                    "수학 (학원숙제)",
                    "영어 (단어+학습지)",
                    "국어 (어휘/독해)",
                    "마무리 (가방/책상)",
                ],
                "시간(분)": [30, 15, 15, 10],
            })
            fig_bar = px.bar(
                df_bar, x="과목", y="시간(분)", color="과목", text="시간(분)"
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        st.divider()
        st.subheader(
            f"⚡ {selected_day} 학원 & 이동 동선 타임라인 (수정 내용 자동 반영)"
        )

        day_scheds = st.session_state.schedules.get(selected_day, [])
        if day_scheds:
            cols = st.columns(len(day_scheds))
            for idx, item in enumerate(day_scheds):
                with cols[idx]:
                    st.info(
                        f"**`{item['time']}`**\n\n**{item['name']}**\n\n{item['detail']}\n\n`[{item['badge']}]`"
                    )
        else:
            st.write("등록된 학원 일정이 없습니다.")

# ==========================================
# TAB 2: 요일별 학원 (수정 시 구글 시트 자동 저장)
# ==========================================
with tab2:
    st.subheader("🎒 방과 후 요일별 학원 일정 & 이동 동선")
    edit_weekday = st.toggle("✏️ 일정 수정 모드 켜기/끄기", key="tog_weekday")

    day_choice = st.radio(
        "요일을 선택하세요:",
        ["월요일", "화요일", "수요일", "목요일", "금요일"],
        horizontal=True,
    )
    items = st.session_state.schedules[day_choice]

    if edit_weekday:
        st.warning(
            f"✏️ **{day_choice} 수정을 완료한 후 '수정 내용 저장' 버튼을"
            " 누르세요.**"
        )
        new_items = []
        for idx, item in enumerate(items):
            c1, c2, c3 = st.columns([2, 3, 4])
            with c1:
                t_val = st.text_input(
                    f"시간 #{idx+1}", item["time"], key=f"t_{day_choice}_{idx}"
                )
            with c2:
                n_val = st.text_input(
                    f"활동명 #{idx+1}",
                    item["name"],
                    key=f"n_{day_choice}_{idx}",
                )
            with c3:
                d_val = st.text_input(
                    f"상세설명 #{idx+1}",
                    item["detail"],
                    key=f"d_{day_choice}_{idx}",
                )
            new_items.append({
                "time": t_val,
                "name": n_val,
                "detail": d_val,
                "badge": item.get("badge", "일정"),
            })

        if st.button(f"💾 {day_choice} 수정 내용 저장"):
            st.session_state.schedules[day_choice] = new_items
            save_sheet_data(schedules=st.session_state.schedules)
            st.success(
                "저장되었습니다! 구글 시트와 대시보드에 자동 연동됩니다."
            )
            st.rerun()
    else:
        st.write(f"### 🗓️ {day_choice} 상세 일정")
        for item in items:
            st.markdown(
                f"- **`{item['time']}` | {item['name']}** : {item['detail']}"
                f" `[{item['badge']}]`"
            )

# ==========================================
# TAB 3: 저녁 루틴 (수정 시 구글 시트 자동 저장)
# ==========================================
with tab3:
    st.subheader("🌙 저녁 시간대 루틴 시뮬레이션")
    edit_evening = st.toggle("✏️ 저녁 루틴 수정 모드 켜기/끄기", key="tog_evening")
    plan_mode = st.radio(
        "루틴 모드를 선택하세요:",
        ["Plan A (평소 루틴)", "Plan B (유연 루틴)"],
        horizontal=True,
    )
    plan_key = "Plan A" if "Plan A" in plan_mode else "Plan B"

    if edit_evening:
        st.warning(
            f"✏️ **{plan_key} 루틴 내용을 수정 후 저장 버튼을 누르세요.**"
        )
        new_plan = []
        for idx, (t, n, d) in enumerate(
            st.session_state.evening_plans[plan_key]
        ):
            c1, c2, c3 = st.columns([2, 3, 4])
            with c1:
                t_val = st.text_input(
                    f"시간 #{idx+1}", t, key=f"et_{plan_key}_{idx}"
                )
            with c2:
                n_val = st.text_input(
                    f"제목 #{idx+1}", n, key=f"en_{plan_key}_{idx}"
                )
            with c3:
                d_val = st.text_input(
                    f"상세 #{idx+1}", d, key=f"ed_{plan_key}_{idx}"
                )
            new_plan.append((t_val, n_val, d_val))

        if st.button(f"💾 {plan_key} 수정 내용 저장"):
            st.session_state.evening_plans[plan_key] = new_plan
            save_sheet_data(evening=st.session_state.evening_plans)
            st.success("구글 시트에 성공적으로 저장되었습니다!")
            st.rerun()
    else:
        st.write(f"### 🟢 {plan_key} 상세 단계")
        for idx, (t, n, d) in enumerate(
            st.session_state.evening_plans[plan_key]
        ):
            st.write(f"{idx+1}. **`{t}` | {n}** - {d}")

# ==========================================
# TAB 4: 주말 일과 (수정 시 구글 시트 자동 저장)
# ==========================================
with tab4:
    st.subheader("☀️ 주말 알찬 타임라인 (토/일)")
    edit_weekend = st.toggle("✏️ 주말 일정 수정 모드 켜기/끄기", key="tog_weekend")
    weekend_choice = st.radio(
        "주말 요일 선택:",
        ["토요일 타임라인", "일요일 타임라인 (예배 포함)"],
        horizontal=True,
    )
    wk_key = "토요일" if "토요일" in weekend_choice else "일요일"

    if edit_weekend:
        st.warning(
            f"✏️ **{wk_key} 수정을 완료한 후 '수정 내용 저장' 버튼을"
            " 누르세요.**"
        )
        new_wk_plan = []
        for idx, (t, n, d) in enumerate(
            st.session_state.weekend_plans[wk_key]
        ):
            c1, c2, c3 = st.columns([2, 3, 4])
            with c1:
                t_val = st.text_input(
                    f"시간 #{idx+1}", t, key=f"wt_{wk_key}_{idx}"
                )
            with c2:
                n_val = st.text_input(
                    f"할 일 #{idx+1}", n, key=f"wn_{wk_key}_{idx}"
                )
            with c3:
                d_val = st.text_input(
                    f"비고 #{idx+1}", d, key=f"wd_{wk_key}_{idx}"
                )
            new_wk_plan.append((t_val, n_val, d_val))

        if st.button(f"💾 {wk_key} 수정 내용 저장"):
            st.session_state.weekend_plans[wk_key] = new_wk_plan
            save_sheet_data(weekend=st.session_state.weekend_plans)
            st.success(
                "저장되었습니다! 구글 시트와 대시보드에 자동 반영됩니다."
            )
            st.rerun()
    else:
        st.write(f"### 🗓️ {wk_key} 상세 일정")
        for t, n, d in st.session_state.weekend_plans[wk_key]:
            st.write(f"- **`{t}` | {n}** ({d})")

# ==========================================
# TAB 5: 체크 & 기록 (수정 시 구글 시트 자동 저장)
# ==========================================
with tab5:
    st.subheader("✅ 일일 실천 체크리스트")
    edit_chk = st.toggle("✏️ 미션 문구 수정 모드 켜기/끄기", key="tog_chk")

    if edit_chk:
        st.warning(
            "✏️ **체크리스트 미션 문구를 자유롭게 수정한 뒤 저장 버튼을"
            " 누르세요.**"
        )
        col_ew, col_ewk = st.columns(2)

        with col_ew:
            st.write("### 📅 평일 미션 문구 수정")
            new_w_chk = {}
            for k, (txt, val) in st.session_state.checklist_weekday.items():
                ntxt = st.text_input(f"평일 미션 {k}", txt, key=f"etxt_w_{k}")
                new_w_chk[k] = (ntxt, val)

        with col_ewk:
            st.write("### ☀️ 주말 미션 문구 수정")
            new_wk_chk = {}
            for k, (txt, val) in st.session_state.checklist_weekend.items():
                ntxt = st.text_input(f"주말 미션 {k}", txt, key=f"etxt_wk_{k}")
                new_wk_chk[k] = (ntxt, val)

        if st.button("💾 체크리스트 문구 저장"):
            st.session_state.checklist_weekday = new_w_chk
            st.session_state.checklist_weekend = new_wk_chk
            chk_payload = {
                "weekday": new_w_chk,
                "weekend": new_wk_chk,
            }
            save_sheet_data(checklist=chk_payload)
            st.success("체크리스트 문구가 구글 시트에 저장되었습니다!")
            st.rerun()
    else:
        col_w, col_wk = st.columns(2)
        with col_w:
            st.write("### 📅 평일 필수 미션")
            for key, (
                text,
                val,
            ) in st.session_state.checklist_weekday.items():
                checked = st.checkbox(text, value=val, key=f"check_{key}")
                st.session_state.checklist_weekday[key] = (text, checked)

        with col_wk:
            st.write("### ☀️ 주말 필수 미션")
            for key, (
                text,
                val,
            ) in st.session_state.checklist_weekend.items():
                checked = st.checkbox(text, value=val, key=f"check_{key}")
                st.session_state.checklist_weekend[key] = (text, checked)

        w_count = sum(
            1 for _, val in st.session_state.checklist_weekday.values() if val
        )
        wk_count = sum(
            1 for _, val in st.session_state.checklist_weekend.values() if val
        )

        st.divider()
        st.write(
            f"🎉 **오늘의 미션 달성 상태:** 평일 ({w_count}/5 완료) | 주말"
            f" ({wk_count}/5 완료)"
        )

# ==========================================
# TAB 6: AI 코치 & 퀴즈
# ==========================================
with tab6:
    st.subheader("✨ Gemini AI 스마트 학습 코치")

    ai_tool = st.radio(
        "원하는 AI 기능을 선택하세요:",
        [
            "🧠 1분 AI 퀴즈 (실전 모의 퀴즈)",
            "🔊 AI 응원 멘트 (10가지 상황)",
            "🎨 칭찬 스티커 (1일 1개 & 보상목표)",
            "🔍 AI 궁금증 질의응답",
        ],
        horizontal=True,
    )

    # 1. 1분 AI 퀴즈
    if "1분 AI 퀴즈" in ai_tool:
        subject = st.radio(
            "퀴즈 과목을 선택하세요:",
            [
                "📜 한국사능력검정시험 (한능검 유형 반영 실전 모의 퀴즈)",
                "🔬 초등 과학교과",
                "🔤 초등 필수 영단어 & 표현",
            ],
            horizontal=True,
        )

        if st.button("✨ 다음 문제 출제하기"):
            st.session_state.quiz_click_count += 1
            idx = st.session_state.quiz_click_count

            with st.spinner("알맞은 퀴즈를 생성하는 중입니다..."):
                prompt = (
                    f"당신은 친절한 AI 튜터입니다. {subject} 주제에 대해 한능검"
                    f" 기출 유형 및 교과 과정 스타일의 {idx}번째 모의 문제 1개를"
                    " 출제하세요.\n\n[조건]\n- 4지선다형 객관식 문제로"
                    " 만드세요.\n- 💡 해설 부분은 딱딱한 시험 문제집 말투가"
                    " 아니라, '에릭 학생, 이 문제는 ~ 때문이야!'처럼 눈높이에"
                    " 맞춰 다정하고 이해하기 쉽게 부드러운 말투로 설명해"
                    " 주세요.\n\n[출력 형식]\n[문제] ➡️ [보기 1,2,3,4] ➡️ 💡"
                    " [친절한 해설] ➡️ 🔒 [정답]"
                )
                res_text = call_gemini_api(prompt)
                st.success(f"회차 #{idx} 퀴즈 생성 완료!")
                st.markdown(res_text)

    # 2. AI 응원 멘트
    elif "AI 응원 멘트" in ai_tool:
        sit_target = st.radio(
            "💬 현재 상황이나 기분을 선택하세요 (10가지):",
            [
                "🌅 1. 아침 일찍 일어나 기상 미션을 완수했을 때",
                "🏫 2. 방과 후 학원 3곳을 모두 무사히 다녀왔을 때",
                "⚡ 3. 저녁 70분 몰입 학습(수학+영어+국어)을 다 끝냈을 때",
                "⚾ 4. 주말 아빠와 야구/운동 활동을 완수했을 때",
                "📖 5. 밤 1시간 몰입 독서를 마쳤을 때",
                "😊 6. 기분이 아주 좋고 자신감이 넘칠 때",
                "🌧️ 7. 공부나 문제 풀이가 잘 안되어 속상할 때",
                "😴 8. 하루 일과가 끝나고 너무 피곤하고 지칠 때",
                "🔥 9. 시험이나 퀴즈를 앞두고 의욕을 다질 때",
                "🛌 10. 밤 22시 전 샤워 후 잠자리에 누울 때",
            ],
            key="single_sit_radio",
        )

        st.divider()
        voice_style = st.radio(
            "🗣️ 목소리 톤을 선택하세요:",
            [
                "🌸 상냥하고 다정한 선생님 (보통 톤)",
                "🔥 신나고 활기찬 친구 (높고 빠른 톤)",
                "🐻 든든하고 따뜻한 멘토 (낮고 부드러운 톤)",
            ],
            horizontal=True,
        )

        if st.button("🎙️ AI 응원 메시지 생성 & 음성 재생"):
            with st.spinner("AI 멘토가 응원 메시지를 작성 중입니다..."):
                prompt = (
                    f"학생 '에릭'의 현재 상황: '{sit_target}'. 이 상황에 맞게"
                    " 학생의 이름을 '에릭'으로 부르거나 자연스럽게 잇고, '[학생"
                    " 이름]'이나 'OO야' 같은 템플릿 문구를 절대 사용하지"
                    " 마세요. 50자~100자 사이로 따스하고 다정한 응원 문구를"
                    " 완성해줘."
                )
                msg_text = call_gemini_api(prompt)

                st.balloons()
                st.info(f"💬 **AI 멘토의 응원:**\n\n{msg_text}")

                if "신나고 활기찬" in voice_style:
                    rate_val = 1.15
                    pitch_val = 1.3
                elif "든든하고 따뜻한" in voice_style:
                    rate_val = 0.9
                    pitch_val = 0.8
                else:
                    rate_val = 1.0
                    pitch_val = 1.05

                clean_text = msg_text.replace("\n", " ").replace('"', "'")

                tts_script = f"""
                <script>
                    window.speechSynthesis.cancel();
                    var msg = new SpeechSynthesisUtterance("{clean_text}");
                    msg.lang = 'ko-KR';
                    msg.rate = {rate_val};
                    msg.pitch = {pitch_val};
                    window.speechSynthesis.speak(msg);
                </script>
                """
                st.components.v1.html(tts_script, height=0)

    # 3. 칭찬 스티커
    elif "칭찬 스티커" in ai_tool:
        st.write("### 🏆 칭찬 스티커 & 보상 스티커북")

        reward_in = st.text_input(
            "🎯 30개 스티커 완성 시 받고 싶은 보상을 적어보세요:",
            value=st.session_state.reward_goal,
        )
        if reward_in != st.session_state.reward_goal:
            st.session_state.reward_goal = reward_in
            save_sheet_data(reward_goal=reward_in)

        st.caption(
            f"📅 오늘 날짜: {today_str} | 스티커는 하루에 1개씩만 획득할 수"
            " 있습니다."
        )

        btn_c1, btn_c2 = st.columns([3, 1])
        with btn_c1:
            if st.button("🎲 오늘의 칭찬 스티커 뽑기!"):
                if st.session_state.last_sticker_date == today_str:
                    st.warning(
                        "⚠️ 오늘의 칭찬 스티커는 이미 획득하셨습니다! 내일 미션을"
                        " 완수하고 또 도전해 보세요."
                    )
                else:
                    rand_icon = random.choice(STICKER_ICONS)
                    rand_msg = random.choice(STICKER_MSG)
                    sticker_item = {
                        "icon": rand_icon,
                        "msg": rand_msg,
                        "date": today_str,
                    }
                    st.session_state.stickers.append(sticker_item)
                    st.session_state.last_sticker_date = today_str
                    st.session_state.latest_draw_sticker = sticker_item

                    save_sheet_data(
                        stickers_count=len(st.session_state.stickers)
                    )
                    st.balloons()

        with btn_c2:
            if st.button("🔄 스티커판 초기화"):
                st.session_state.stickers = []
                st.session_state.latest_draw_sticker = None
                save_sheet_data(stickers_count=0)
                st.success("스티커판이 0개로 리셋되었습니다!")
                st.rerun()

        if st.session_state.latest_draw_sticker:
            lstk = st.session_state.latest_draw_sticker
            st.markdown(
                f"""
                <div style="text-align:center; padding: 20px; background: linear-gradient(135deg, #fbcfe8, #e0e7ff); border-radius:20px; border:3px solid #ec4899; margin-bottom: 20px;">
                    <div style="font-size: 70px; margin-bottom: 5px;">{lstk['icon']}</div>
                    <div style="font-size: 18px; font-weight: bold; color: #831843;">🎉 축하합니다! 스티커를 획득했어요!</div>
                    <div style="font-size: 14px; color: #4338ca; font-weight: bold; margin-top: 4px;">"{lstk['msg']}"</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.divider()
        st.write(
            f"🏆 **내 칭찬 스티커북 ({len(st.session_state.stickers)}/30개 모음)**"
        )

        if len(st.session_state.stickers) >= 30:
            st.balloons()
            st.success(
                f"🎉 **축하합니다! 스티커 30개를 모두 모았습니다!**\n\n🎁 **보상"
                f" 획득:** {st.session_state.reward_goal}"
            )

        st.info(f"🎁 **30개 완수 보상:** {st.session_state.reward_goal}")

        cols = st.columns(6)
        for i in range(30):
            col = cols[i % 6]
            with col:
                if i < len(st.session_state.stickers):
                    stk = st.session_state.stickers[i]
                    st.markdown(
                        f"""
                        <div style="height:80px; display:flex; flex-direction:column; align-items:center; justify-content:center; border:2px solid #ec4899; border-radius:12px; padding:6px; background-color:#fdf2f8; margin-bottom:10px; box-sizing:border-box;">
                            <div style="font-size:24px; line-height:1.2;">{stk['icon']}</div>
                            <div style="font-size:9px; color:#be185d; font-weight:bold; margin-top:4px; text-align:center; word-break:keep-all;">{stk['msg']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"""
                        <div style="height:80px; display:flex; align-items:center; justify-content:center; border:1px dashed #cbd5e1; border-radius:12px; color:#94a3b8; font-size:14px; margin-bottom:10px; box-sizing:border-box; background-color:#ffffff;">
                            {i+1}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    # 4. AI 궁금증 질의응답
    elif "AI 궁금증 질의응답" in ai_tool:
        q_input = st.text_input(
            "궁금한 역사/과학 질문을 적어보세요:",
            "이순신 장군의 3대 대첩이 뭐야?",
        )

        if st.button("🔍 AI 백과에 질문하기"):
            with st.spinner("눈높이에 맞춰 정리하는 중입니다..."):
                prompt = (
                    "당신은 학생 대상의 지식 백과 튜터입니다. 질문:"
                    f" '{q_input}'.\n\n[주의사항]\n- 만약 질문이 실시간 시사"
                    " 뉴스나 현재 정치인/대통령 등 시점에 따라 변하는 내용일"
                    " 경우, 학습 데이터 시점 한계로 인해 실시간 변동될 수"
                    " 있다는 점을 부드럽게 밝히고 가장 신뢰성 있는 역사/기본"
                    " 개념 위주로 설명하세요.\n\n[출력 구조]\n이해하기 쉽게\n1)"
                    " 핵심 요약\n2) 상세 설명\n3) 💡 기억할 점 3단계 구조로"
                    " 깔끔하게 정리해 주세요."
                )
                res_text = call_gemini_api(prompt)
                st.success("답변 완료!")
                st.markdown(res_text)
