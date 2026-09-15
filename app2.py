import datetime
import json
import random
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="초등 5학년 주간 일정 & 저녁/주말 루틴",
    page_icon="📅",
    layout="wide",
)

# 2. CSS 구조 개편: 바탕화면(흰색) vs 큰 네모 박스(불투명 파스텔 블루/슬레이트)
st.markdown(
    """
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    html, body, [class*="css"] {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif !important;
    }
    
    /* 1. 바탕 화면 전체: 완전한 순백색 고정 */
    .stApp, .main, [data-testid="stMainBlockContainer"], .block-container {
        background-color: #ffffff !important;
        color: #1e293b;
    }
    
    .main .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1180px;
    }

    /* 2. 큰 네모 박스 껍데기: 조금 더 진하고 명확한 파스텔 블루/슬레이트 (#e2e8f0) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #e2e8f0 !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
        padding: 20px 20px 24px 20px !important;
        margin-bottom: 18px !important;
    }

    /* 3. [핵심] 큰 네모 박스 내부 알맹이: 투명 속성 제거 후 불투명 색상 강제 지정 */
    div[data-testid="stVerticalBlockBorderWrapper"] > div,
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"] {
        background-color: #e2e8f0 !important;
    }

    /* 4. 가로 라인 및 높이 수평 맞춤 */
    [data-testid="stColumn"] > div {
        height: 100%;
    }
    [data-testid="stColumn"] [data-testid="stVerticalBlockBorderWrapper"] {
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .banner-blue {
        background-color: #eff6ff;
        border: 1px solid #bfdbfe;
        color: #1e3a8a;
        border-radius: 16px;
        padding: 12px 18px;
        font-size: 13px;
        margin-bottom: 16px;
        line-height: 1.5;
    }

    .metric-card-tw {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 16px;
        padding: 14px 16px;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.02);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .metric-title-tw {
        font-size: 11px;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-val-tw {
        font-size: 24px;
        font-weight: 900;
        line-height: 1.1;
        margin-top: 4px;
        margin-bottom: 4px;
    }
    .metric-sub-tw {
        font-size: 11px;
        color: #64748b;
    }

    .banner-ai-grad {
        background: linear-gradient(to right, #4f46e5, #7c3aed, #ec4899);
        border-radius: 16px;
        padding: 20px 24px;
        color: white;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2);
    }

    .tl-item-box {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 12px;
        padding: 14px 14px;
        height: 100%;
        margin-bottom: 4px;
    }

    .stButton>button {
        border-radius: 10px;
        font-weight: 700;
    }
</style>
""",
    unsafe_allow_html=True,
)

# 3. PIN 번호 인증 시스템 (1306 설정)
SET_PIN = "1306"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown(
        """
        <div style="max-width: 380px; margin: 80px auto; padding: 36px 28px; background: white; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); text-align: center; border: 1px solid #e2e8f0;">
            <div style="font-size: 40px; margin-bottom: 10px;">🔒</div>
            <h2 style="font-weight: 800; color: #0f172a; margin-bottom: 6px; font-size: 20px;">인증 코드 입력</h2>
            <p style="font-size: 12px; color: #64748b; margin-bottom: 22px;">스마트 루틴에 접근하려면 PIN을 입력하세요.</p>
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
            label_visibility="collapsed",
        )
        if st.button("2단계 인증 확인", use_container_width=True):
            if pin_input == SET_PIN:
                st.session_state.authenticated = True
                st.success("인증 성공!")
                st.rerun()
            else:
                st.error("PIN 번호가 일치하지 않습니다. 다시 입력해 주세요.")
    st.stop()

# 4. 구글 시트 연동 설정
SHEET_ID = "1x5A3X2lGb5SFpHE5qspuetmdOsWMiP_mfnWY0ZqD6rc"
SHEET_CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=data"
)
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbxrG7rYb5WXHcXkbd20QsiWywCNM7GWbW7KVll2n88gP15kHVsCfAdF_Tcr7Uhc53eqRw/exec"

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

            w_chk, wk_chk, hist = None, None, []
            if pd.notna(chk_raw) and chk_raw:
                chk_data = json.loads(chk_raw)
                w_chk = chk_data.get("weekday", None)
                wk_chk = chk_data.get("weekend", None)
                hist = chk_data.get("history", [])

            return stk_cnt, goal, sch, eve, wk, w_chk, wk_chk, hist
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
        [],
    )


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


# 5. API 키 설정 (gemini-3.6-flash 모델 및 timeout 60초)
api_key = st.secrets.get("GEMINI_API_KEY", "")


def call_gemini_api(prompt):
    if not api_key:
        return "Secrets에 GEMINI_API_KEY가 설정되어 있지 않습니다."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(
            url, headers=headers, data=json.dumps(payload), timeout=60
        )
        res_json = response.json()

        if response.status_code == 200:
            return res_json["candidates"][0]["content"]["parts"][0]["text"]
        else:
            err_msg = res_json.get("error", {}).get("message", "알 수 없는 오류")
            return f"API 오류 ({response.status_code}): {err_msg}"
    except requests.exceptions.Timeout:
        return "⏳ AI 응답 시간이 초과되었습니다. 잠시 후 버튼을 다시 눌러주세요!"
    except Exception as e:
        return f"통신 오류 발생: {e}"


# 6. 세션 상태 초기화 & 구글 시트 전체 동기화
(
    init_stk,
    init_goal,
    init_sch,
    init_eve,
    init_wk,
    init_w_chk,
    init_wk_chk,
    init_hist,
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

if "history_log" not in st.session_state:
    st.session_state.history_log = init_hist

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

# 7. 상단 헤더
days_kor = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
today_idx = datetime.date.today().weekday()
today_name = days_kor[today_idx]
today_str = datetime.date.today().strftime("%Y-%m-%d")

h_col1, h_col2 = st.columns([8, 1])
with h_col1:
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 2px;">
            <span style="font-size: 26px;">📅</span>
            <h2 style="margin:0; font-weight:800; color:#0f172a; font-size: 20px;">초등 5학년 주간 일정 & 저녁/주말 루틴</h2>
        </div>
        <div style="font-size: 12px; color: #64748b; font-weight: 500;">
            <span style="background: #dbeafe; color: #1e40af; padding: 2px 6px; border-radius: 4px; font-weight: 700;">오늘: {today_str} ({today_name})</span>
            &nbsp;수면 22:00 전 • 아침 최태성 한국사 • 저녁 70분 스퍼트
        </div>
        """,
        unsafe_allow_html=True,
    )
with h_col2:
    if st.button("🔒 잠금"):
        st.session_state.authenticated = False
        st.rerun()

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

# 8. 메인 탭 구성
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
    st.markdown(
        """
        <div class="banner-blue">
            💡 <b>맞춤형 스마트 루틴 대시보드:</b> 학원 동선, 70분 저녁 집중 학습, 주말 야외활동 및 독서 루틴이 통합 저장됩니다. Gemini AI 학습 코치가 함께합니다!
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected_day = st.radio(
        "요일 선택:",
        days_kor,
        index=today_idx,
        horizontal=True,
        key="dash_day_radio",
        label_visibility="collapsed",
    )

    is_weekend = selected_day in ["토요일", "일요일"]

    st.markdown(
        "<div style='margin-top: 6px;'></div>", unsafe_allow_html=True
    )
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)

    with m_col1:
        st.markdown(
            """
            <div class="metric-card-tw">
                <span class="metric-title-tw">권장 수면 시간</span>
                <div class="metric-val-tw" style="color:#4f46e5;">8.5시간</div>
                <div class="metric-sub-tw" style="display:flex; justify-content:space-between;">
                    <span>21:20 샤워 ➡️ 22:00 취침</span>
                    <span>22:00~06:30</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m_col2:
        val_txt = "90분" if is_weekend else "70분"
        sub_txt = (
            "수학+영어+독서 완주"
            if is_weekend
            else "수학30분+영어15분+국어15분"
        )
        time_txt = "07:00~08:30" if is_weekend else "20:10~21:20"
        title_txt = (
            "주말 모닝 집중 학습" if is_weekend else "평일 저녁 집중 학습"
        )
        st.markdown(
            f"""
            <div class="metric-card-tw">
                <span class="metric-title-tw">{title_txt}</span>
                <div class="metric-val-tw" style="color:#2563eb;">{val_txt}</div>
                <div class="metric-sub-tw" style="display:flex; justify-content:space-between;">
                    <span>{sub_txt}</span>
                    <span>{time_txt}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m_col3:
        st.markdown(
            """
            <div class="metric-card-tw">
                <span class="metric-title-tw">주말 야외/신체 활동</span>
                <div class="metric-val-tw" style="color:#d97706;">2.5시간</div>
                <div class="metric-sub-tw" style="display:flex; justify-content:space-between;">
                    <span>아빠와 야구 & 야외활동</span>
                    <span>오후 13:00~</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m_col4:
        st.markdown(
            """
            <div class="metric-card-tw">
                <span class="metric-title-tw">주말 게임 시간 관리</span>
                <div class="metric-val-tw" style="color:#059669;">3시간</div>
                <div class="metric-sub-tw" style="display:flex; justify-content:space-between;">
                    <span>오전 1차 + 해질녘 2차</span>
                    <span>1.5h × 2회 쪼개기</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        "<div style='margin-top: 12px;'></div>", unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)

    with c1:
        with st.container(border=True):
            st.markdown(
                f"""
                <h3 style="margin:0; font-size:15px; font-weight:800; color:#0f172a;">📊 {'평일' if not is_weekend else selected_day} 하루 시간 배분 비율</h3>
                <div style="font-size:11px; color:#64748b; margin-top:2px; margin-bottom:4px;">학업, 수면, 휴식, 이동의 균형 시각화</div>
                """,
                unsafe_allow_html=True,
            )

            if is_weekend:
                df_pie = pd.DataFrame({
                    "항목": [
                        "수면 (8.5시간)",
                        "모닝학습 & 독서 (2.5시간)",
                        "야외활동 & 게임 (5.5시간)",
                        "식사 & 여유 (7.5시간)",
                    ],
                    "시간": [8.5, 2.5, 5.5, 7.5],
                })
            else:
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
                hole=0.55,
                color_discrete_sequence=[
                    "#6366f1",
                    "#3b82f6",
                    "#f59e0b",
                    "#10b981",
                ],
            )
            fig_pie.update_traces(
                textposition="inside",
                textinfo="percent",
                marker=dict(line=dict(color="#ffffff", width=2)),
            )
            fig_pie.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                height=210,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.28,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=10, color="#64748b"),
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        with st.container(border=True):
            st.markdown(
                """
                <h3 style="margin:0; font-size:15px; font-weight:800; color:#0f172a;">🎯 저녁 70분 몰입 학습 과목 구성</h3>
                <div style="font-size:11px; color:#64748b; margin-top:2px; margin-bottom:4px;">15~30분 단위 숏 스퍼트로 지루함 없는 구성</div>
                """,
                unsafe_allow_html=True,
            )
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
                df_bar,
                x="과목",
                y="시간(분)",
                color="과목",
                text="시간(분)",
                color_discrete_sequence=[
                    "#3b82f6",
                    "#8b5cf6",
                    "#ec4899",
                    "#64748b",
                ],
            )
            fig_bar.update_traces(
                textposition="outside",
                marker_line_width=0,
                width=0.45,
            )
            fig_bar.update_layout(
                margin=dict(t=20, b=10, l=10, r=10),
                height=210,
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(
                    showgrid=False,
                    tickfont=dict(size=10, color="#1e293b"),
                    title=None,
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor="#cbd5e1",
                    tickfont=dict(size=10, color="#94a3b8"),
                    title=None,
                    range=[0, 38],
                ),
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    with st.container(border=True):
        st.markdown(
            """
            <h3 style="margin:0; font-size:15px; font-weight:800; color:#0f172a; margin-bottom:12px;">⚡ 하루 핵심 타임라인 한눈에 보기</h3>
            """,
            unsafe_allow_html=True,
        )

        t_cols = st.columns(4)
        with t_cols[0]:
            st.markdown(
                """
                <div class="tl-item-box">
                    <div style="font-size:11px; font-weight:700; color:#2563eb;">🌅 06:30 ~ 08:30 [아침]</div>
                    <div style="font-size:12px; font-weight:700; color:#0f172a; margin:3px 0;">기상 & 한국사 강의 시청</div>
                    <div style="font-size:10px; color:#64748b;">할아버지 댁 이동(07:20) 후 아침 식사 ➡️ 08:22 등교</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with t_cols[1]:
            st.markdown(
                """
                <div class="tl-item-box">
                    <div style="font-size:11px; font-weight:700; color:#059669;">🏫 08:30 ~ 18:30 [방과후]</div>
                    <div style="font-size:12px; font-weight:700; color:#0f172a; margin:3px 0;">학교 수업 & 학원 동선</div>
                    <div style="font-size:10px; color:#64748b;">수학/피아노/미술 픽업 ➡️ 17:30 합기도(도보3분)</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with t_cols[2]:
            st.markdown(
                """
                <div class="tl-item-box">
                    <div style="font-size:11px; font-weight:700; color:#d97706;">🚘 18:30 ~ 20:10 [귀가&식사]</div>
                    <div style="font-size:12px; font-weight:700; color:#0f172a; margin:3px 0;">부모님 픽업 & 저녁 식사</div>
                    <div style="font-size:10px; color:#64748b;">18:40 픽업 ➡️ 19:15 집 도착 ➡️ 가족 저녁 식사</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with t_cols[3]:
            st.markdown(
                """
                <div class="tl-item-box">
                    <div style="font-size:11px; font-weight:700; color:#4f46e5;">🌙 20:10 ~ 22:10 [저녁&취침]</div>
                    <div style="font-size:12px; font-weight:700; color:#0f172a; margin:3px 0;">70분 학습 & 22시 전 취침</div>
                    <div style="font-size:10px; color:#64748b;">20:10 학습 ➡️ 21:20 샤워 ➡️ 22:00~22:10 취침</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown(
            "<div style='margin-bottom:4px;'></div>", unsafe_allow_html=True
        )

# ==========================================
# TAB 2: 요일별 학원
# ==========================================
with tab2:
    st.markdown(
        """
        <div class="banner-blue">
            🎒 <b>방과 후 학원 동선:</b> 합기도는 매일 17:30(도보 3분), 수요일은 피아노와 수학이 같은 건물 옆 호실로 연속 수강됩니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

    edit_weekday = st.toggle("✏️ 일정 수정 모드 켜기/끄기", key="tog_weekday")

    day_choice = st.radio(
        "요일 선택:",
        ["월요일", "화요일", "수요일", "목요일", "금요일"],
        horizontal=True,
        label_visibility="collapsed",
    )
    items = st.session_state.schedules[day_choice]

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

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
            st.success("저장되었습니다! 구글 시트에 자동 연동됩니다.")
            st.rerun()
    else:
        with st.container(border=True):
            st.markdown(
                f"""
                <h3 style="margin-top:0; font-weight:800; color:#0f172a; font-size:16px; margin-bottom:12px;">{day_choice} 일정 상세 보기</h3>
                """,
                unsafe_allow_html=True,
            )
            for item in items:
                st.markdown(
                    f"""
                    <div style="display:flex; justify-content:space-between; align-items:center; padding: 12px 16px; background-color:#ffffff; border-radius:12px; margin-bottom:8px; border:1px solid #cbd5e1;">
                        <div style="display:flex; align-items:center; gap:12px;">
                            <span style="font-size:12px; font-weight:700; color:#64748b;">⏰ {item['time']}</span>
                            <span style="font-size:14px; font-weight:700; color:#1e293b;">{item['name']}</span>
                        </div>
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="font-size:11px; color:#64748b;">{item['detail']}</span>
                            <span style="background:#e2e8f0; color:#475569; font-size:10px; font-weight:700; padding:2px 6px; border-radius:6px;">{item['badge']}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

# ==========================================
# TAB 3: 저녁 루틴
# ==========================================
with tab3:
    st.markdown(
        """
        <div class="banner-blue">
            🌙 <b>저녁 루틴 모드 선택:</b> 퇴근 및 저녁 준비 상태에 따라 Plan A(평소)와 Plan B(유연)를 선택하세요.
        </div>
        """,
        unsafe_allow_html=True,
    )

    edit_evening = st.toggle("✏️ 저녁 루틴 수정 모드 켜기/끄기", key="tog_evening")
    plan_mode = st.radio(
        "루틴 모드 선택:",
        ["Plan A (평소 루틴)", "Plan B (유연 루틴)"],
        horizontal=True,
        label_visibility="collapsed",
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
        with st.container(border=True):
            st.markdown(
                f"""
                <h3 style="margin-top:0; font-weight:800; color:#0f172a; font-size:16px; margin-bottom:12px;">🟢 {plan_key} 상세 단계</h3>
                """,
                unsafe_allow_html=True,
            )
            for idx, (t, n, d) in enumerate(
                st.session_state.evening_plans[plan_key]
            ):
                st.markdown(
                    f"""
                    <div style="padding: 12px 16px; background-color:#ffffff; border-radius:12px; margin-bottom:8px; border:1px solid #cbd5e1;">
                        <div style="display:flex; align-items:center; gap:10px;">
                            <span style="font-size:11px; font-weight:700; color:#ef4444; background:#fee2e2; padding:2px 6px; border-radius:6px;">{t}</span>
                            <span style="font-size:14px; font-weight:700; color:#1e293b;">{n}</span>
                        </div>
                        <div style="font-size:11px; color:#64748b; margin-top:4px;">{d}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

# ==========================================
# TAB 4: 주말 일과
# ==========================================
with tab4:
    st.markdown(
        """
        <div class="banner-blue">
            ☀️ <b>주말 타임라인:</b> 알찬 아침 모닝 90분 공부 및 아빠와 야외 신체활동 중심 구성입니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

    edit_weekend = st.toggle("✏️ 주말 일정 수정 모드 켜기/끄기", key="tog_weekend")
    weekend_choice = st.radio(
        "주말 요일 선택:",
        ["토요일 타임라인", "일요일 타임라인 (예배 포함)"],
        horizontal=True,
        label_visibility="collapsed",
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
            st.success("저장되었습니다!")
            st.rerun()
    else:
        with st.container(border=True):
            st.markdown(
                f"""
                <h3 style="margin-top:0; font-weight:800; color:#0f172a; font-size:16px; margin-bottom:12px;">🗓️ {wk_key} 상세 일정</h3>
                """,
                unsafe_allow_html=True,
            )
            for t, n, d in st.session_state.weekend_plans[wk_key]:
                st.markdown(
                    f"""
                    <div style="display:flex; justify-content:space-between; align-items:center; padding: 12px 16px; background-color:#ffffff; border-radius:12px; margin-bottom:8px; border:1px solid #cbd5e1;">
                        <div style="display:flex; align-items:center; gap:12px;">
                            <span style="font-size:12px; font-weight:700; color:#d97706;">⏰ {t}</span>
                            <span style="font-size:14px; font-weight:700; color:#1e293b;">{n}</span>
                        </div>
                        <span style="font-size:11px; color:#64748b;">{d}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

# ==========================================
# TAB 5: 체크 & 기록
# ==========================================
with tab5:
    st.markdown(
        """
        <div class="banner-blue">
            ✅ <b>스마트 일일 루틴 체크리스트:</b> 체크 상태 변경 시 구글 시트에 즉시 반영되며, 최근 7일 동안의 누적 실천 기록이 자동 보관됩니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

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
                "history": st.session_state.history_log,
            }
            save_sheet_data(checklist=chk_payload)
            st.success("체크리스트 문구가 구글 시트에 저장되었습니다!")
            st.rerun()
    else:
        col_w, col_wk = st.columns(2)
        with col_w:
            with st.container(border=True):
                st.markdown(
                    """
                    <h3 style="margin-top:0; font-weight:800; color:#0f172a; font-size:15px; margin-bottom:12px;">📅 평일 필수 미션</h3>
                    """,
                    unsafe_allow_html=True,
                )
                for key, (
                    text,
                    val,
                ) in st.session_state.checklist_weekday.items():
                    checked = st.checkbox(text, value=val, key=f"check_{key}")
                    if checked != val:
                        st.session_state.checklist_weekday[key] = (
                            text,
                            checked,
                        )
                        w_cnt = sum(
                            1
                            for _, v in st.session_state.checklist_weekday.values()
                            if v
                        )
                        today_m = today_str[5:]
                        hist = [
                            h
                            for h in st.session_state.history_log
                            if h.get("date") != today_m
                        ]
                        hist.insert(
                            0, {"date": today_m, "count": w_cnt, "total": 5}
                        )
                        st.session_state.history_log = hist[:7]

                        chk_payload = {
                            "weekday": st.session_state.checklist_weekday,
                            "weekend": st.session_state.checklist_weekend,
                            "history": st.session_state.history_log,
                        }
                        save_sheet_data(checklist=chk_payload)

        with col_wk:
            with st.container(border=True):
                st.markdown(
                    """
                    <h3 style="margin-top:0; font-weight:800; color:#0f172a; font-size:15px; margin-bottom:12px;">☀️ 주말 필수 미션</h3>
                    """,
                    unsafe_allow_html=True,
                )
                for key, (
                    text,
                    val,
                ) in st.session_state.checklist_weekend.items():
                    checked = st.checkbox(text, value=val, key=f"check_{key}")
                    if checked != val:
                        st.session_state.checklist_weekend[key] = (
                            text,
                            checked,
                        )
                        wk_cnt = sum(
                            1
                            for _, v in st.session_state.checklist_weekend.values()
                            if v
                        )
                        today_m = today_str[5:]
                        hist = [
                            h
                            for h in st.session_state.history_log
                            if h.get("date") != today_m
                        ]
                        hist.insert(
                            0, {"date": today_m, "count": wk_cnt, "total": 5}
                        )
                        st.session_state.history_log = hist[:7]

                        chk_payload = {
                            "weekday": st.session_state.checklist_weekday,
                            "weekend": st.session_state.checklist_weekend,
                            "history": st.session_state.history_log,
                        }
                        save_sheet_data(checklist=chk_payload)

        # 7일간 누적 실천 로그 카드
        with st.container(border=True):
            st.markdown(
                """
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #cbd5e1; padding-bottom:8px; margin-bottom:14px;">
                    <h3 style="margin:0; font-size:15px; font-weight:800; color:#0f172a;">📈 최근 7일 실천 기록 (누적 달성 로그)</h3>
                    <span style="font-size:11px; color:#64748b;">구글 시트에 자동 영구 보관됩니다</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            logs = st.session_state.history_log[:7]
            if not logs:
                st.markdown(
                    """
                    <div style="text-align:center; padding:20px; font-size:12px; color:#94a3b8;">
                        아직 저장된 과거 기록이 없습니다. 위 체크리스트를 클릭해 보세요!
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                h_cols = st.columns(7)
                for idx in range(7):
                    with h_cols[idx]:
                        if idx < len(logs):
                            lg = logs[idx]
                            c_val = lg.get("count", 0)
                            tot_val = lg.get("total", 5)
                            dt_val = lg.get("date", "-")
                            is_success = c_val >= 4

                            bg_style = (
                                "background-color:#eff6ff; border:1px solid"
                                " #bfdbfe; color:#1e40af;"
                                if is_success
                                else "background-color:#ffffff; border:1px solid"
                                " #cbd5e1; color:#475569;"
                            )

                            st.markdown(
                                f"""
                                <div style="{bg_style} border-radius:12px; padding:10px 4px; text-align:center; margin-bottom:4px;">
                                    <div style="font-size:10px; font-weight:700;">{dt_val}</div>
                                    <div style="font-size:16px; font-weight:900; margin:4px 0;">{c_val} / {tot_val}</div>
                                    <div style="font-size:10px; font-weight:700;">{"🎉 완수" if is_success else "참 잘했어요"}</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                        else:
                            st.markdown(
                                """
                                <div style="background-color:#ffffff; border:1px dashed #cbd5e1; border-radius:12px; padding:10px 4px; text-align:center; color:#94a3b8; margin-bottom:4px;">
                                    <div style="font-size:10px;">대기</div>
                                    <div style="font-size:16px; font-weight:700; margin:4px 0;">-</div>
                                    <div style="font-size:10px;">-</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
            st.markdown(
                "<div style='margin-bottom:4px;'></div>", unsafe_allow_html=True
            )

# ==========================================
# TAB 6: AI 코치 & 퀴즈
# ==========================================
with tab6:
    st.markdown(
        """
        <div class="banner-ai-grad">
            <div style="font-size:11px; font-weight:800; opacity:0.9; margin-bottom:4px; text-transform:uppercase; letter-spacing:0.05em;">GEMINI AI ENGINE POWERED</div>
            <h2 style="margin:0; font-weight:900; font-size:20px;">✨ 초등 5학년 Gemini AI 스마트 학습 코치</h2>
            <p style="margin-top:4px; margin-bottom:0; font-size:12px; opacity:0.95;">AI가 퀴즈 생성, 음성 응원 칭찬, 칭찬 스티커 생성, 그리고 역사/과학 궁금증 답변까지 도웁니다!</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1행: 퀴즈 생성기 & 음성 응원
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        with st.container(border=True):
            st.markdown(
                """
                <div>
                    <h3 style="margin-top:0; font-weight:800; color:#0f172a; font-size:15px;">🧠 초등 5학년 1분 AI 퀴즈 생성기</h3>
                    <p style="font-size:11px; color:#64748b; margin-bottom:12px;">아침 시청 복습이나 저녁 공부 시작 전, 재미있는 1분 퀴즈로 뇌를 세워보세요!</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            
            subject = st.selectbox(
                "과목 선택",
                [
                    "📜 한국사 퀴즈 (전 범위 다채로운 기출 유형)",
                    "🔬 초등 과학교과 (전 범위 탐구 유형)",
                    "🔤 초등 필수 영단어 & 표현",
                ],
                key="grid_subject",
                label_visibility="visible",
            )
            
            if st.button("✨ 퀴즈 생성", key="btn_g_quiz", use_container_width=True):
                st.session_state.quiz_click_count += 1
                idx = st.session_state.quiz_click_count
                with st.spinner("알맞은 퀴즈를 생성하는 중입니다..."):
                    prompt = (
                        f"당신은 친절한 AI 튜터입니다. '{subject}' 과목에 대해 초등"
                        f" 5학년 수준의 {idx}번째 모의 문제 1개를 무작위 출제하세요."
                        " 특정 시대나 단원에 치우치지 말고 전 범위에서 흥미로운"
                        " 문제를 골라주세요.\n\n[조건]\n- 4지선다형 객관식 문제로"
                        " 만드세요.\n- 💡 해설 부분은 '에릭 학생, 이 문제는 ~"
                        " 때문이야!'처럼 눈높이에 맞춰 다정하고 쉽게 설명해"
                        " 주세요.\n\n[출력 형식]\n[문제] ➡️ [보기 1,2,3,4] ➡️ 💡"
                        " [친절한 해설] ➡️ 🔒 [정답]"
                    )
                    res_text = call_gemini_api(prompt)
                    st.success(f"회차 #{idx} 퀴즈 생성 완료!")
                    st.markdown(res_text)

    with row1_col2:
        with st.container(border=True):
            st.markdown(
                """
                <div>
                    <h3 style="margin-top:0; font-weight:800; color:#0f172a; font-size:15px;">🔊 AI 멘토 음성 응원 메시지 (TTS)</h3>
                    <p style="font-size:11px; color:#64748b; margin-bottom:12px;">상황과 기분에 맞게 선택해 보세요! 매일 다른 칭찬과 응원 멘트가 전해집니다.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            sit_target = st.selectbox(
                "상황 선택",
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
                key="grid_sit",
                label_visibility="visible",
            )

            if st.button(
                "🎙️ AI 응원 음성 들려주기",
                key="btn_g_voice",
                use_container_width=True,
            ):
                with st.spinner("AI 멘토가 응원 메시지를 작성 중입니다..."):
                    prompt = (
                        f"학생 '에릭'의 현재 상황: '{sit_target}'. 이 상황에 맞게"
                        " 학생 이름 '에릭'을 부르고 50자~100자 사이로 따스하고"
                        " 다정한 응원 문구를 완성해줘."
                    )
                    msg_text = call_gemini_api(prompt)

                    st.balloons()
                    st.info(f"💬 **AI 멘토의 응원:**\n\n{msg_text}")

                    rate_val, pitch_val = 1.0, 1.05
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

    # 2행: 스티커 카운터 & 질의응답
    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        with st.container(border=True):
            current_cnt = len(st.session_state.stickers)
            pct_val = int(current_cnt / 30 * 100)
            st.markdown(
                f"""
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3 style="margin:0; font-weight:800; color:#0f172a; font-size:15px;">
                        🎨 AI 미션 달성 칭찬 스티커 카운터 <span style="color:#ec4899; font-weight:900; font-size:14px;">({current_cnt}/30개, {pct_val}%)</span>
                    </h3>
                    <span style="font-size:10px; background:#fce7f3; color:#be185d; font-weight:700; padding:2px 6px; border-radius:4px;">하루 1장 제한</span>
                </div>
                <p style="font-size:11px; color:#64748b; margin-top:4px; margin-bottom:12px;">오늘 미션을 성공했을 때 칭찬 스티커 카드를 생성하여 내 스티커북(30개판)에 저장합니다!</p>
                """,
                unsafe_allow_html=True,
            )

            if st.button(
                "🎲 스티커 그리기", key="btn_g_sticker", use_container_width=True
            ):
                if st.session_state.last_sticker_date == today_str:
                    st.warning("⚠️ 오늘의 칭찬 스티커는 이미 획득하셨습니다!")
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

            if st.session_state.latest_draw_sticker:
                lstk = st.session_state.latest_draw_sticker
                st.markdown(
                    f"""
                    <div style="text-align:center; padding: 18px 16px; background: linear-gradient(135deg, #fef9c3, #fef08a); border: 1px solid #fde047; border-radius:14px; margin-top: 10px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.03);">
                        <div style="font-size: 32px; line-height: 1.1;">{lstk['icon']}</div>
                        <div style="font-size: 13px; font-weight: 800; color: #854d0e; margin-top: 4px;">"{lstk['msg']}"</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # 🎯 달성 보상 목표 입력 부분
            c_label, c_in, c_btn = st.columns([1.8, 3.4, 1.0])
            with c_label:
                st.markdown(
                    "<div style='font-size:12px; font-weight:700; color:#334155; height:38px; display:flex; align-items:center;'>🎯 달성 보상 목표 :</div>",
                    unsafe_allow_html=True,
                )
            with c_in:
                new_goal_val = st.text_input(
                    "보상 목표",
                    value=st.session_state.reward_goal,
                    key="input_reward_goal",
                    label_visibility="collapsed",
                )
            with c_btn:
                if st.button("📌", key="btn_save_goal", use_container_width=True):
                    st.session_state.reward_goal = new_goal_val
                    save_sheet_data(reward_goal=new_goal_val)
                    st.success("완료!")
                    st.rerun()

    with row2_col2:
        with st.container(border=True):
            st.markdown(
                """
                <h3 style="margin-top:0; font-weight:800; color:#0f172a; font-size:15px;">🔍 AI 탐구 & 호기심 질의응답 (구글 검색 연동)</h3>
                <p style="font-size:11px; color:#64748b; margin-top:4px; margin-bottom:12px;">역사, 과학, 수학 개념 등 궁금한 점을 최신 정보로 정확하게 답변해 줍니다.</p>
                """,
                unsafe_allow_html=True,
            )
            q_input = st.text_input(
                "질문 입력",
                "조선 시대 임진왜란 때 이순신 장군 3대 대첩이 뭐야?",
                key="grid_q_in",
                label_visibility="visible",
            )

            if st.button("🟢 질문하기", key="btn_g_q", use_container_width=True):
                with st.spinner("눈높이에 맞춰 정리하는 중입니다..."):
                    prompt = (
                        "당신은 초등학생 대상 지식 백과 튜터입니다. 질문:"
                        f" '{q_input}'.\n이해하기 쉽게 1) 핵심 요약 2) 상세 설명 3)"
                        " 💡 기억할 점 3단계 구조로 정리해 주세요."
                    )
                    res_text = call_gemini_api(prompt)
                    st.success("답변 완료!")
                    st.markdown(res_text)

    # 3행: 내 칭찬 스티커북 (30개 모음판)
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <h3 style="margin:0; font-size:14px; font-weight:800; color:#0f172a;">🏆 내 칭찬 스티커북 ({len(st.session_state.stickers)} / 30개 모음)</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        total_stickers = 30
        cols_per_row = 10
        for row_idx in range(0, total_stickers, cols_per_row):
            row_cols = st.columns(cols_per_row)
            for c_idx in range(cols_per_row):
                i = row_idx + c_idx
                if i < total_stickers:
                    with row_cols[c_idx]:
                        if i < len(st.session_state.stickers):
                            stk = st.session_state.stickers[i]
                            st.markdown(
                                f"""
                                <div style="height:54px; display:flex; flex-direction:column; align-items:center; justify-content:center; border:1px solid #f472b6; border-radius:8px; background-color:#fff5f5; margin-bottom:4px;">
                                    <div style="font-size:16px;">{stk['icon']}</div>
                                    <div style="font-size:7px; color:#be185d; font-weight:bold; margin-top:1px; text-align:center;">{stk['msg'][:5]}..</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                        else:
                            st.markdown(
                                f"""
                                <div style="height:54px; display:flex; align-items:center; justify-content:center; border:1px dashed #cbd5e1; border-radius:8px; color:#94a3b8; font-size:11px; margin-bottom:4px; background-color:#ffffff;">
                                    {i+1}
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
