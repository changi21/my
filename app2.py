import streamlit as st

# Streamlit 페이지 기본 설정
st.set_page_config(
    page_title="초등 5학년 주간 일정표 & AI 대시보드",
    page_icon="📅",
    layout="wide",
)

# Streamlit Secrets에서 API 키 안전하게 가져오기
api_key = st.secrets.get("GEMINI_API_KEY", "")

# 자바스크립트 문법 오류 방지를 위해 raw text 파싱
html_code = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>초등 5학년 주간 일정표 & AI 스마트 루틴 대시보드</title>
    <!-- App Favicon & Mobile Home Screen Icon -->
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='22' fill='%233b82f6'/><text x='50%' y='55%' font-size='55' text-anchor='middle' dominant-baseline='central'>📅</text></svg>">
    <link rel="apple-touch-icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='22' fill='%233b82f6'/><text x='50%' y='55%' font-size='55' text-anchor='middle' dominant-baseline='central'>📅</text></svg>">
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Chart.js CDN -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        body {
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
            background-color: #f8fafc;
            color: #1e293b;
        }
        .chart-container {
            position: relative;
            width: 100%;
            max-width: 550px;
            margin-left: auto;
            margin-right: auto;
            height: 280px;
            max-height: 320px;
        }
        @media (min-width: 768px) {
            .chart-container {
                height: 320px;
            }
        }
        .tab-btn.active {
            background-color: #3b82f6 !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.3) !important;
        }
        .day-btn.active {
            border-color: #3b82f6 !important;
            background-color: #eff6ff !important;
            color: #1d4ed8 !important;
            font-weight: 700 !important;
        }
        .editable-input {
            border: 1px dashed #cbd5e1;
            padding: 2px 6px;
            border-radius: 4px;
            background-color: #ffffff;
        }
        .editable-input:focus {
            outline: 2px solid #3b82f6;
            border-style: solid;
        }
        .spinner-dark {
            border: 3px solid rgba(0,0,0,0.1);
            border-radius: 50%;
            border-top-color: #3b82f6;
            width: 24px;
            height: 24px;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body class="bg-slate-50 text-slate-800 antialiased min-h-screen flex flex-col">

    <!-- Top Header -->
    <header class="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
        <div class="max-w-6xl mx-auto px-4 py-3 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
            <div class="flex items-center gap-3">
                <span class="text-2xl md:text-3xl shrink-0">📅</span>
                <div class="min-w-0">
                    <div class="flex flex-wrap items-center gap-2">
                        <h1 class="text-base md:text-lg font-bold text-slate-900 tracking-tight whitespace-nowrap">
                            초등 5학년 주간 일정 & 저녁/주말 루틴
                        </h1>
                        <span class="bg-indigo-100 text-indigo-700 text-[11px] px-2.5 py-0.5 rounded-full font-extrabold border border-indigo-200 shrink-0 whitespace-nowrap">
                            ✨ AI Powered
                        </span>
                    </div>
                    <div class="text-xs text-slate-500 flex flex-wrap items-center gap-x-2 gap-y-1 mt-1">
                        <span id="current-date-badge" class="bg-blue-100 text-blue-800 px-2 py-0.5 rounded font-semibold text-[11px] shrink-0 whitespace-nowrap">오늘 날짜 계산 중...</span>
                        <span class="truncate">수면 22:00 전 • 아침 최태성 한국사 • 저녁 70분 스퍼트</span>
                    </div>
                </div>
            </div>

            <!-- Navigation Tabs & Edit Controls -->
            <div class="flex items-center gap-2 flex-wrap shrink-0">
                <nav class="flex flex-wrap gap-1 bg-slate-100 p-1 rounded-xl text-xs font-medium">
                    <button onclick="switchTab('dashboard')" id="nav-dashboard" class="tab-btn active px-2.5 py-1.5 rounded-lg transition-all whitespace-nowrap">📊 대시보드</button>
                    <button onclick="switchTab('weekday')" id="nav-weekday" class="tab-btn px-2.5 py-1.5 rounded-lg text-slate-600 hover:bg-white transition-all whitespace-nowrap">🎒 요일별 학원</button>
                    <button onclick="switchTab('evening')" id="nav-evening" class="tab-btn px-2.5 py-1.5 rounded-lg text-slate-600 hover:bg-white transition-all whitespace-nowrap">🌙 저녁 루틴</button>
                    <button onclick="switchTab('weekend')" id="nav-weekend" class="tab-btn px-2.5 py-1.5 rounded-lg text-slate-600 hover:bg-white transition-all whitespace-nowrap">☀️ 주말 일과</button>
                    <button onclick="switchTab('checklist')" id="nav-checklist" class="tab-btn px-2.5 py-1.5 rounded-lg text-slate-600 hover:bg-white transition-all whitespace-nowrap">✅ 체크 & 기록</button>
                    <button onclick="switchTab('ai')" id="nav-ai" class="tab-btn px-2.5 py-1.5 rounded-lg text-slate-600 hover:bg-white transition-all whitespace-nowrap bg-gradient-to-r hover:from-indigo-50 hover:to-purple-50">✨ AI 코치 & 퀴즈</button>
                </nav>
                <button onclick="toggleEditMode()" id="btn-edit-mode" class="text-xs px-3 py-1.5 bg-slate-200 hover:bg-slate-300 text-slate-700 font-bold rounded-xl transition-all shrink-0 whitespace-nowrap">
                    ✏️ 일정 수정
                </button>
            </div>
        </div>
    </header>

    <!-- Main Content Area -->
    <main class="max-w-6xl mx-auto px-4 py-6 flex-grow w-full">

        <!-- TAB 1: DASHBOARD OVERVIEW -->
        <section id="sec-dashboard" class="space-y-6">
            <div class="bg-blue-50 border border-blue-200 rounded-2xl p-4 text-blue-900 text-sm leading-relaxed flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                <div>
                    💡 <strong>맞춤형 스마트 루틴 대시보드:</strong> 학원 동선, 70분 저녁 집중 학습, 주말 야외활동 및 독서 루틴이 통합 저장됩니다. Gemini AI 학습 코치가 함께합니다!
                </div>
                <div id="streak-badge" class="bg-white border border-blue-300 px-3 py-1.5 rounded-xl text-xs font-bold text-indigo-700 shadow-sm shrink-0">
                    🔥 0일 연속 미션 완료 중!
                </div>
            </div>

            <!-- Key Metric Cards -->
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
                    <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">권장 수면 시간</span>
                    <div class="mt-2 flex items-baseline justify-between">
                        <span class="text-2xl font-black text-indigo-600">8.5시간</span>
                        <span class="text-xs text-slate-500">22:00~06:30</span>
                    </div>
                    <p class="text-[11px] text-slate-400 mt-1">21:20 샤워 ➡️ 22:00 취침</p>
                </div>
                <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
                    <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">평일 저녁 집중 학습</span>
                    <div class="mt-2 flex items-baseline justify-between">
                        <span class="text-2xl font-black text-blue-600">70분</span>
                        <span class="text-xs text-slate-500">20:10~21:20</span>
                    </div>
                    <p class="text-[11px] text-slate-400 mt-1">수학30분+영어15분+국어15분</p>
                </div>
                <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
                    <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">주말 야외/신체 활동</span>
                    <div class="mt-2 flex items-baseline justify-between">
                        <span class="text-2xl font-black text-amber-600">2.5시간</span>
                        <span class="text-xs text-slate-500">오후 13:00~</span>
                    </div>
                    <p class="text-[11px] text-slate-400 mt-1">아빠와 야구 & 야외활동</p>
                </div>
                <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
                    <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">주말 게임 시간 관리</span>
                    <div class="mt-2 flex items-baseline justify-between">
                        <span class="text-2xl font-black text-emerald-600">3시간</span>
                        <span class="text-xs text-slate-500">1.5h × 2회 쪼개기</span>
                    </div>
                    <p class="text-[11px] text-slate-400 mt-1">오전 1차 + 해질녘 2차</p>
                </div>
            </div>

            <!-- Charts Section -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
                    <h3 class="text-base font-bold text-slate-800 mb-1 flex items-center gap-2">
                        <span>📊</span> 평일 하루 시간 배분 비율
                    </h3>
                    <p class="text-xs text-slate-500 mb-4">학업, 수면, 휴식, 이동의 균형 시각화</p>
                    <div class="chart-container">
                        <canvas id="timePieChart"></canvas>
                    </div>
                </div>

                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
                    <h3 class="text-base font-bold text-slate-800 mb-1 flex items-center gap-2">
                        <span>🎯</span> 저녁 70분 몰입 학습 과목 구성
                    </h3>
                    <p class="text-xs text-slate-500 mb-4">15~30분 단위 숏 스퍼트로 지루함 없는 구성</p>
                    <div class="chart-container">
                        <canvas id="studyBarChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Quick Summary Timeline Cards -->
            <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
                <h3 class="text-base font-bold text-slate-800 mb-3 flex items-center gap-2">
                    <span>⚡</span> 하루 핵심 타임라인 한눈에 보기
                </h3>
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                    <div class="p-3 bg-slate-50 rounded-xl border border-slate-100">
                        <div class="text-xs font-bold text-blue-600 mb-1">🌅 06:30 ~ 08:30 [아침]</div>
                        <div class="text-xs font-semibold text-slate-800">기상 & 한국사 강의 시청</div>
                        <div class="text-[11px] text-slate-500 mt-1">할아버지 댁 이동(07:20) 후 아침 식사 ➡️ 08:22 등교</div>
                    </div>
                    <div class="p-3 bg-slate-50 rounded-xl border border-slate-100">
                        <div class="text-xs font-bold text-emerald-600 mb-1">🏫 08:30 ~ 18:30 [방과후]</div>
                        <div class="text-xs font-semibold text-slate-800">학교 수업 & 학원 동선</div>
                        <div class="text-[11px] text-slate-500 mt-1">수학/피아노/미술 픽업 ➡️ 17:30 합기도(도보3분)</div>
                    </div>
                    <div class="p-3 bg-slate-50 rounded-xl border border-slate-100">
                        <div class="text-xs font-bold text-amber-600 mb-1">🚘 18:30 ~ 20:10 [귀가&식사]</div>
                        <div class="text-xs font-semibold text-slate-800">부모님 픽업 & 저녁 식사</div>
                        <div class="text-[11px] text-slate-500 mt-1">18:40 픽업 ➡️ 19:15 집 도착 ➡️ 가족 저녁 식사</div>
                    </div>
                    <div class="p-3 bg-slate-50 rounded-xl border border-slate-100">
                        <div class="text-xs font-bold text-indigo-600 mb-1">🌙 20:10 ~ 22:10 [저녁&취침]</div>
                        <div class="text-xs font-semibold text-slate-800">70분 학습 & 22시 전 취침</div>
                        <div class="text-[11px] text-slate-500 mt-1">20:10 학습 ➡️ 21:20 샤워 ➡️ 22:00~22:10 취침</div>
                    </div>
                </div>
            </div>
        </section>

        <!-- TAB 2: WEEKDAY ACADEMIES & ROUTES -->
        <section id="sec-weekday" class="hidden space-y-6">
            <div class="bg-amber-50 border border-amber-200 rounded-2xl p-4 text-amber-900 text-sm leading-relaxed flex items-center justify-between">
                <div>🎒 <strong>방과 후 학원 동선:</strong> 합기도는 매일 17:30(도보3분), 수요일은 피아노와 수학이 같은 건물 옆 호실로 연속 수강됩니다.</div>
            </div>

            <div class="flex flex-wrap gap-2">
                <button onclick="renderDaySchedule('mon')" id="day-mon" class="day-btn active px-4 py-2 rounded-xl border border-slate-200 bg-white text-sm transition-all">월요일</button>
                <button onclick="renderDaySchedule('tue')" id="day-tue" class="day-btn px-4 py-2 rounded-xl border border-slate-200 bg-white text-sm transition-all">화요일 (★ 여유 시간)</button>
                <button onclick="renderDaySchedule('wed')" id="day-wed" class="day-btn px-4 py-2 rounded-xl border border-slate-200 bg-white text-sm transition-all">수요일 (★ 학원 연계)</button>
                <button onclick="renderDaySchedule('thu')" id="day-thu" class="day-btn px-4 py-2 rounded-xl border border-slate-200 bg-white text-sm transition-all">목요일 (★ 여유 시간)</button>
                <button onclick="renderDaySchedule('fri')" id="day-fri" class="day-btn px-4 py-2 rounded-xl border border-slate-200 bg-white text-sm transition-all">금요일</button>
            </div>

            <div id="day-schedule-card" class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4"></div>
        </section>

        <!-- TAB 3: EVENING ROUTINE SIMULATOR -->
        <section id="sec-evening" class="hidden space-y-6">
            <div class="bg-indigo-50 border border-indigo-200 rounded-2xl p-4 text-indigo-900 text-sm leading-relaxed flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                <div>🌙 <strong>저녁 루틴 모드 선택:</strong> 퇴근 및 저녁 준비 상태에 따라 Plan A(평소)와 Plan B(유연)를 선택하세요.</div>
                <div class="flex items-center gap-2 bg-white px-3 py-1.5 rounded-xl border border-indigo-200 shrink-0">
                    <span class="text-xs font-bold text-slate-600">루틴 모드:</span>
                    <button onclick="setEveningPlan('A')" id="btn-planA" class="px-2.5 py-1 rounded-lg text-xs font-bold bg-indigo-600 text-white">Plan A (평소)</button>
                    <button onclick="setEveningPlan('B')" id="btn-planB" class="px-2.5 py-1 rounded-lg text-xs font-bold bg-slate-100 text-slate-600 hover:bg-slate-200">Plan B (유연)</button>
                </div>
            </div>

            <div id="evening-plan-container" class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6"></div>
        </section>

        <!-- TAB 4: WEEKEND SCHEDULE -->
        <section id="sec-weekend" class="hidden space-y-6">
            <div class="bg-emerald-50 border border-emerald-200 rounded-2xl p-4 text-emerald-900 text-sm leading-relaxed flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                <div>☀️ <strong>주말 기본 원칙:</strong> "기상 직후 모닝 90분 공부 완주, 8시半 아침 식사, 게임 1.5h×2회 쪼개기, 밤 8시 몰입 독서!"</div>
                <div class="flex items-center gap-2 bg-white px-3 py-1.5 rounded-xl border border-emerald-200 shrink-0">
                    <button onclick="setWeekendDay('sat')" id="btn-sat" class="px-3 py-1 rounded-lg text-xs font-bold bg-emerald-600 text-white">토요일 일정</button>
                    <button onclick="setWeekendDay('sun')" id="btn-sun" class="px-3 py-1 rounded-lg text-xs font-bold bg-slate-100 text-slate-600 hover:bg-slate-200">일요일 일정 (예배 포함)</button>
                </div>
            </div>

            <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
                <div class="flex items-center justify-between border-b pb-3">
                    <h3 id="weekend-title" class="text-lg font-bold text-slate-800">🗓️ 주말 타임라인</h3>
                    <span class="text-xs font-semibold px-2.5 py-1 bg-emerald-100 text-emerald-800 rounded-full">22:00~22:10 취침 유지</span>
                </div>
                <div id="weekend-timeline-list" class="space-y-3"></div>
            </div>
        </section>

        <!-- TAB 5: CHECKLIST & CUMULATIVE HISTORY -->
        <section id="sec-checklist" class="hidden space-y-6">
            <div class="bg-purple-50 border border-purple-200 rounded-2xl p-4 text-purple-900 text-sm leading-relaxed flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                <div>✅ <strong>스마트 일일 루틴 체크리스트:</strong> 매일 자정이 지나면 체크리스트가 <strong>자동 초기화</strong>되며, 완료 실적은 기록에 남습니다.</div>
                <button onclick="forceDailyReset()" class="px-3 py-1.5 bg-purple-600 text-white text-xs font-bold rounded-xl hover:bg-purple-700 transition-all shrink-0">🔄 오늘 체크 수동 초기화</button>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
                    <div class="flex items-center justify-between border-b pb-2">
                        <h3 class="font-bold text-slate-800 flex items-center gap-2"><span>📅</span> 평일 필수 미션</h3>
                        <span class="text-xs text-purple-600 font-bold" id="weekday-count">0 / 5 완료</span>
                    </div>
                    <div id="weekday-checklist-container" class="space-y-2 text-xs"></div>
                </div>

                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
                    <div class="flex items-center justify-between border-b pb-2">
                        <h3 class="font-bold text-slate-800 flex items-center gap-2"><span>☀️</span> 주말 필수 미션</h3>
                        <span class="text-xs text-emerald-600 font-bold" id="weekend-count">0 / 5 완료</span>
                    </div>
                    <div id="weekend-checklist-container" class="space-y-2 text-xs"></div>
                </div>
            </div>

            <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
                <div class="flex items-center justify-between border-b pb-3">
                    <h3 class="text-base font-bold text-slate-800 flex items-center gap-2"><span>📈</span> 최근 7일 실천 기록 (누적 달성 로그)</h3>
                    <span id="history-total-summary" class="text-xs font-semibold text-slate-500">누적 성공 데이터 기록 중</span>
                </div>
                <div id="history-cards-container" class="grid grid-cols-2 sm:grid-cols-7 gap-3"></div>
            </div>
        </section>

        <!-- TAB 6: GEMINI AI SMART CENTER -->
        <section id="sec-ai" class="hidden space-y-6">
            <div class="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-500 rounded-2xl p-6 text-white shadow-md relative overflow-hidden">
                <div class="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                    <div>
                        <span class="bg-white/20 text-white text-xs px-3 py-1 rounded-full font-extrabold uppercase tracking-wider backdrop-blur-sm">Gemini AI Engine Powered</span>
                        <h2 class="text-2xl font-black mt-2 tracking-tight">✨ 초등 5학년 Gemini AI 스마트 학습 코치</h2>
                        <p class="text-xs text-indigo-100 mt-1 max-w-xl">AI가 퀴즈 생성, 음성 응원 칭찬, 칭찬 스티커 생성, 그리고 역사/과학 궁금증 답변까지 돕습니다!</p>
                    </div>
                    <span class="text-3xl">🤖</span>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- TOOL 1 -->
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between border-b pb-3 mb-4">
                            <h3 class="font-bold text-slate-800 flex items-center gap-2"><span>🧠</span> 초등 5학년 1분 AI 퀴즈 생성기</h3>
                            <span class="text-[11px] bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full font-semibold">gemini-3-flash-preview</span>
                        </div>
                        <p class="text-xs text-slate-500 mb-4">아침 시청 복습이나 저녁 공부 시작 전, 재미있는 1분 퀴즈로 뇌를 세워보세요!</p>
                        <div class="flex gap-2 mb-4">
                            <select id="ai-quiz-subject" class="bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs font-semibold text-slate-700 flex-grow">
                                <option value="한국사능력검정시험 (한능검 기본/초등 5학년 출제 유형)">📜 한국사능력검정시험(한능검) 실전 퀴즈</option>
                                <option value="초등 5학년 과학교과 (태양계, 날씨, 물체의 운동)">🔬 재미있는 초등 5학년 과학 퀴즈</option>
                                <option value="초등 필수 영단어 & 영어 회화">영어 단어 & 표현 퀴즈</option>
                            </select>
                            <button onclick="generateAIQuiz()" id="btn-gen-quiz" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl text-xs transition-all shrink-0">✨ 퀴즈 생성</button>
                        </div>
                        <div id="ai-quiz-result" class="bg-slate-50 border border-slate-200 rounded-xl p-4 text-xs leading-relaxed hidden min-h-[140px]"></div>
                    </div>
                </div>

                <!-- TOOL 2 -->
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between border-b pb-3 mb-4">
                            <h3 class="font-bold text-slate-800 flex items-center gap-2"><span>🔊</span> AI 멘토 음성 응원 메시지 (TTS)</h3>
                            <span class="text-[11px] bg-purple-100 text-purple-800 px-2 py-0.5 rounded-full font-semibold">gemini-2.5-flash-preview-tts</span>
                        </div>
                        <p class="text-xs text-slate-500 mb-4">상황과 기분에 맞게 선택해 보세요! 매일 매일 다른 칭찬과 응원 멘트가 전해집니다.</p>
                        <div class="grid grid-cols-2 gap-2 mb-3">
                            <div>
                                <label class="text-[11px] font-bold text-slate-600 block mb-1">상황/기분 선택:</label>
                                <select id="tts-situation" class="w-full bg-slate-50 border border-slate-300 rounded-xl px-2.5 py-1.5 text-xs text-slate-700">
                                    <option value="morning">🌅 아침 등교 전 화이팅!</option>
                                    <option value="evening">🌙 저녁 70분 공부 완수!</option>
                                    <option value="weekend">⚾ 주말 운동/야구 완수!</option>
                                    <option value="together">🔥 같이 힘내자! 의샤의샤!</option>
                                    <option value="happy">😊 기분 최고! 신나는 축하</option>
                                    <option value="comfort">🌧️ 피곤하거나 속상할 때 따뜻한 위로</option>
                                    <option value="confident">🎯 할 수 있어! 자신감 충전</option>
                                </select>
                            </div>
                            <div>
                                <label class="text-[11px] font-bold text-slate-600 block mb-1">목소리 캐릭터:</label>
                                <select id="tts-voice" class="w-full bg-slate-50 border border-slate-300 rounded-xl px-2.5 py-1.5 text-xs text-slate-700">
                                    <option value="Puck">Puck (밝고 에너지 넘치는 소년)</option>
                                    <option value="Zephyr">Zephyr (상냥하고 밝은 목소리)</option>
                                    <option value="Kore">Kore (다정하고 든든한 멘토)</option>
                                    <option value="Fenrir">Fenrir (신나는 스포티 목소리)</option>
                                </select>
                            </div>
                        </div>
                        <button onclick="generateAIVoice()" id="btn-gen-tts" class="w-full py-2.5 bg-purple-600 hover:bg-purple-700 text-white font-bold rounded-xl text-xs transition-all">🎙️ AI 응원 음성 들려주기</button>
                        <div id="tts-status" class="mt-3 text-center text-xs font-semibold text-slate-500 hidden"></div>
                    </div>
                </div>

                <!-- TOOL 3 -->
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between border-b pb-3 mb-4">
                            <h3 class="font-bold text-slate-800 flex items-center gap-2"><span>🎨</span> AI 미션 달성 칭찬 스티커 카운터</h3>
                            <span class="text-[11px] bg-pink-100 text-pink-800 px-2 py-0.5 rounded-full font-semibold">하루 1장 제한</span>
                        </div>
                        <p class="text-xs text-slate-500 mb-4">오늘 미션을 성공했을 때 칭찬 스티커 카드를 생성하여 <b>내 스티커북(30개판)</b>에 저장합니다!</p>
                        <div class="flex gap-2 mb-4">
                            <input type="text" id="sticker-prompt" value="한국사 탐험가 로봇과 야구 방망이를 든 용감한 초등학생 칭찬 캐릭터" class="bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs text-slate-800 flex-grow" placeholder="스티커 콘셉트를 입력하세요">
                            <button onclick="generateAISticker()" id="btn-gen-sticker" class="px-4 py-2 bg-pink-600 hover:bg-pink-700 text-white font-bold rounded-xl text-xs shrink-0">🖼️ 스티커 그리기</button>
                        </div>
                        <div id="sticker-result" class="bg-slate-50 border border-slate-200 rounded-xl p-3 flex items-center justify-center min-h-[140px]">
                            <span class="text-xs text-slate-400">버튼을 누르면 칭찬 스티커가 생성되어 내 스티커북에 저장됩니다.</span>
                        </div>
                        <div class="mt-4 border-t border-slate-100 pt-3">
                            <div class="bg-gradient-to-r from-pink-50 via-purple-50 to-indigo-50 p-3 rounded-xl border border-pink-200 mb-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                                <div class="flex items-center gap-1.5 min-w-0 flex-grow">
                                    <span class="text-xs font-bold text-pink-900 shrink-0">🎯 30개 달성 보상 목표:</span>
                                    <input type="text" id="reward-goal-input" onchange="updateRewardGoal(this.value)" value="아빠와 프로야구 직관 가기 & 갖고 싶던 선물!" class="editable-input text-xs font-bold text-indigo-700 bg-white border border-pink-300 rounded-lg px-2.5 py-1 flex-grow">
                                </div>
                                <div class="text-right shrink-0">
                                    <span class="text-[11px] font-extrabold text-purple-700 bg-white px-2.5 py-1 rounded-lg border border-purple-200 shadow-sm" id="reward-progress-text">0 / 30개 (0%)</span>
                                </div>
                            </div>
                            <div class="flex items-center justify-between mb-2">
                                <span class="text-xs font-bold text-pink-900">🏆 내 칭찬 스티커북 (<span id="sticker-count-badge">0</span>/30개 모음)</span>
                                <button onclick="resetStickers()" class="text-[10px] text-slate-400 hover:text-red-500 underline">스티커판 리셋</button>
                            </div>
                            <div id="sticker-gallery" class="grid grid-cols-6 sm:grid-cols-10 gap-1.5 bg-pink-50/50 p-2.5 rounded-xl border border-pink-100 min-h-[110px] items-center"></div>
                        </div>
                    </div>
                </div>

                <!-- TOOL 4 -->
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between border-b pb-3 mb-4">
                            <h3 class="font-bold text-slate-800 flex items-center gap-2"><span>🔍</span> AI 탐구 & 호기심 질의응답 (구글 검색 연동)</h3>
                            <span class="text-[11px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full font-semibold">Google Search Grounding</span>
                        </div>
                        <p class="text-xs text-slate-500 mb-4">역사, 과학, 수학 개념 등 궁금한 점을 최신 정보로 정확하게 답변해 줍니다.</p>
                        <div class="flex gap-2 mb-4">
                            <input type="text" id="search-query" value="조선 시대 임진왜란 때 이순신 장군 3대 대첩이 뭐야?" class="bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs text-slate-800 flex-grow">
                            <button onclick="searchAIQna()" id="btn-gen-search" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-xs shrink-0">🔍 질문하기</button>
                        </div>
                        <div id="search-result" class="bg-slate-50 border border-slate-200 rounded-xl p-4 text-xs leading-relaxed hidden min-h-[160px] max-h-[220px] overflow-y-auto"></div>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <footer class="bg-white border-t border-slate-200 mt-8 py-4 text-center text-xs text-slate-500">
        <p>초등 5학년 맞춤 주간 일정표 & AI 스마트 루틴 대시보드 • 데이터는 브라우저에 안전하게 저장됩니다.</p>
    </footer>

    <!-- JS Application Logic -->
    <script>
        var apiKey = "__API_KEY__";

        var DEFAULT_WEEKDAY_SCHEDULES = {
            mon: {
                title: "월요일 일정 (수학 데이)",
                items: [
                    { time: "14:00 ~ 15:00", name: "하교 & 할아버지 댁 휴식", detail: "학교 수업 종료 후 이동", badge: "휴식" },
                    { time: "15:00 ~ 17:00", name: "📐 수학학원", detail: "픽업 차량 이용 이동", badge: "학원" },
                    { time: "17:00 ~ 17:30", name: "할아버지 댁 이동 & 간식", detail: "휴식 및 합기도 준비", badge: "이동" },
                    { time: "17:30 ~ 18:30", name: "🥋 합기도 학원", detail: "할아버지 댁에서 도보 3분", badge: "운동" },
                    { time: "18:30 ~ 19:15", name: "🚘 하원 픽업 & 집 이동", detail: "18:40 픽업 ➡️ 19:15 집 도착", badge: "픽업" }
                ]
            },
            tue: {
                title: "화요일 일정 (★ 여유 시간 활용)",
                items: [
                    { time: "14:00 ~ 15:00", name: "🎹 피아노 학원", detail: "픽업 차량 이용 이동", badge: "학원" },
                    { time: "15:00 ~ 17:30", name: "🏠 할아버지 댁 여유시간", detail: "💡 독서, 학교/학원 숙제 일부 사전 해결", badge: "여유시간" },
                    { time: "17:30 ~ 18:30", name: "🥋 합기도 학원", detail: "할아버지 댁에서 도보 3분", badge: "운동" },
                    { time: "18:30 ~ 19:15", name: "🚘 하원 픽업 & 집 이동", detail: "18:40 픽업 ➡️ 19:15 집 도착", badge: "픽업" }
                ]
            },
            wed: {
                title: "수요일 일정 (★ 학원 연계 데이)",
                items: [
                    { time: "14:00 ~ 15:00", name: "🎹 피아노 학원", detail: "픽업 차량 이용 이동", badge: "학원" },
                    { time: "15:00 ~ 17:00", name: "📐 수학 학원", detail: "💡 피아노 학원 바로 옆 호실로 즉시 이동", badge: "바로연결" },
                    { time: "17:00 ~ 17:30", name: "할아버지 댁 이동", detail: "잠시 휴식 후 이동", badge: "휴식" },
                    { time: "17:30 ~ 18:30", name: "🥋 합기도 학원", detail: "할아버지 댁에서 도보 3분", badge: "운동" },
                    { time: "18:30 ~ 19:15", name: "🚘 하원 픽업 & 집 이동", detail: "18:40 픽업 ➡️ 19:15 집 도착", badge: "픽업" }
                ]
            },
            thu: {
                title: "목요일 일정 (★ 여유 시간 활용)",
                items: [
                    { time: "14:00 ~ 15:00", name: "🎹 피아노 학원", detail: "픽업 차량 이용 이동", badge: "학원" },
                    { time: "15:00 ~ 17:30", name: "🏠 할아버지 댁 여유시간", detail: "💡 독서, 역사 책 읽기 및 숙제 해결", badge: "여유시간" },
                    { time: "17:30 ~ 18:30", name: "🥋 합기도 학원", detail: "할아버지 댁에서 도보 3분", badge: "운동" },
                    { time: "18:30 ~ 19:15", name: "🚘 하원 픽업 & 집 이동", detail: "18:40 픽업 ➡️ 19:15 집 도착", badge: "픽업" }
                ]
            },
            fri: {
                title: "금요일 일정 (미술 데이)",
                items: [
                    { time: "14:00 ~ 16:00", name: "🎨 미술 학원", detail: "픽업 차량 이용 이동", badge: "학원" },
                    { time: "16:00 ~ 17:30", name: "🏠 할아버지 댁 휴식 & 간식", detail: "자유시간 및 독서", badge: "휴식" },
                    { time: "17:30 ~ 18:30", name: "🥋 합기도 학원", detail: "할아버지 댁에서 도보 3분", badge: "운동" },
                    { time: "18:30 ~ 19:15", name: "🚘 하원 픽업 & 집 이동", detail: "18:40 픽업 ➡️ 19:15 집 도착", badge: "픽업" }
                ]
            }
        };

        var DEFAULT_CHECKLIST_WEEKDAY = [
            { id: "w1", text: "아침 뇌 깨우기: 06:50 최태성 한국사 시청 또는 스트레칭", checked: false },
            { id: "w2", text: "학원 미션: 학원 수강 및 안전한 이동 (도보/차량)", checked: false },
            { id: "w3", text: "70분 몰입 학습: 수학(30분)+영어(15분)+국어 어휘(15분) 완수", checked: false },
            { id: "w4", text: "내일 준비: 21:10 책상 정돈 및 책가방 미리 챙기기", checked: false },
            { id: "w5", text: "취침 골든타임: 21:20 샤워 ➡️ 22:00~22:10 소등 및 눕기", checked: false }
        ];

        var DEFAULT_CHECKLIST_WEEKEND = [
            { id: "wk1", text: "주말 모닝 공부: 기상 직후 90분 학습 (수학+영어+독서) 완수하기", checked: false },
            { id: "wk2", text: "아빠와 야구: 13:00~15:30 햇빛 쬐며 신체활동 다녀오기", checked: false },
            { id: "wk3", text: "게임 약속 준수: 3시간 쪼개기 규칙 (1.5시간 × 2회) 지키기", checked: false },
            { id: "wk4", text: "밤 몰입 독서: 20:00~21:00 부모님 운동 시간 동안 1시간 독서", checked: false },
            { id: "wk5", text: "주말 취침 리듬 유지: 22:00~22:10 이전에 제자리에 눕기", checked: false }
        ];

        var appData = {
            schedules: JSON.parse(JSON.stringify(DEFAULT_WEEKDAY_SCHEDULES)),
            checklistWeekday: JSON.parse(JSON.stringify(DEFAULT_CHECKLIST_WEEKDAY)),
            checklistWeekend: JSON.parse(JSON.stringify(DEFAULT_CHECKLIST_WEEKEND)),
            lastDate: getTodayString(),
            historyLog: [],
            stickers: [],
            rewardGoal: "아빠와 프로야구 직관 가기 & 갖고 싶던 선물!",
            isEditMode: false,
            currentDayKey: 'mon',
            currentPlanKey: 'A',
            currentWeekendKey: 'sat'
        };

        function loadData() {
            var stored = localStorage.getItem('elem5_routine_data_v2');
            if (stored) {
                try {
                    var parsed = JSON.parse(stored);
                    appData = Object.assign({}, appData, parsed);
                } catch (e) {
                    console.error("Storage load error:", e);
                }
            }
            if (!appData.stickers) appData.stickers = [];
            if (!appData.rewardGoal) appData.rewardGoal = "아빠와 프로야구 직관 가기 & 갖고 싶던 선물!";
            checkAndResetDailyData();
        }

        function saveData() {
            localStorage.setItem('elem5_routine_data_v2', JSON.stringify(appData));
        }

        function getTodayString() {
            var today = new Date();
            var year = today.getFullYear();
            var month = String(today.getMonth() + 1).padStart(2, '0');
            var day = String(today.getDate()).padStart(2, '0');
            return year + '-' + month + '-' + day;
        }

        function checkAndResetDailyData() {
            var todayStr = getTodayString();
            var dateBadge = document.getElementById('current-date-badge');
            if (dateBadge) dateBadge.innerText = '오늘: ' + todayStr;

            if (appData.lastDate !== todayStr) {
                var prevWeekdayDone = appData.checklistWeekday.filter(function(i) { return i.checked; }).length;
                var prevWeekendDone = appData.checklistWeekend.filter(function(i) { return i.checked; }).length;
                var totalDone = Math.max(prevWeekdayDone, prevWeekendDone);

                if (appData.lastDate) {
                    appData.historyLog.unshift({
                        date: appData.lastDate,
                        count: totalDone,
                        total: 5
                    });
                    if (appData.historyLog.length > 14) appData.historyLog.pop();
                }

                appData.checklistWeekday.forEach(function(item) { item.checked = false; });
                appData.checklistWeekend.forEach(function(item) { item.checked = false; });
                appData.lastDate = todayStr;
                saveData();
            }
        }

        function forceDailyReset() {
            if (window.confirm("오늘 완료한 체크리스트를 정말 초기화하시겠습니까?")) {
                appData.checklistWeekday.forEach(function(item) { item.checked = false; });
                appData.checklistWeekend.forEach(function(item) { item.checked = false; });
                saveData();
                renderChecklists();
                updateStreakBadge();
            }
        }

        function toggleEditMode() {
            appData.isEditMode = !appData.isEditMode;
            var btn = document.getElementById('btn-edit-mode');
            if (appData.isEditMode) {
                btn.className = "text-xs px-3 py-1.5 bg-amber-500 text-white font-bold rounded-xl transition-all shadow-sm shrink-0 whitespace-nowrap";
                btn.innerText = "💾 수정 완료 및 저장";
            } else {
                btn.className = "text-xs px-3 py-1.5 bg-slate-200 hover:bg-slate-300 text-slate-700 font-bold rounded-xl transition-all shrink-0 whitespace-nowrap";
                btn.innerText = "✏️ 일정 수정";
                saveData();
            }
            renderDaySchedule(appData.currentDayKey);
            renderChecklists();
        }

        function switchTab(tabId) {
            var tabs = ['dashboard', 'weekday', 'evening', 'weekend', 'checklist', 'ai'];
            tabs.forEach(function(t) {
                var sec = document.getElementById('sec-' + t);
                var nav = document.getElementById('nav-' + t);
                if (sec) sec.classList.add('hidden');
                if (nav) {
                    nav.classList.remove('active');
                    nav.classList.add('text-slate-600');
                }
            });

            var activeSec = document.getElementById('sec-' + tabId);
            var activeNav = document.getElementById('nav-' + tabId);
            if (activeSec) activeSec.classList.remove('hidden');
            if (activeNav) {
                activeNav.classList.add('active');
                activeNav.classList.remove('text-slate-600');
            }

            if (tabId === 'checklist') renderHistoryLog();
            if (tabId === 'ai') renderStickerGallery();
        }

        function renderDaySchedule(dayKey) {
            appData.currentDayKey = dayKey;
            ['mon', 'tue', 'wed', 'thu', 'fri'].forEach(function(d) {
                var btn = document.getElementById('day-' + d);
                if (btn) {
                    btn.className = (d === dayKey) ? "day-btn active px-4 py-2 rounded-xl border border-slate-200 bg-white text-sm transition-all" : "day-btn px-4 py-2 rounded-xl border border-slate-200 bg-white text-sm transition-all";
                }
            });

            var data = appData.schedules[dayKey];
            var container = document.getElementById('day-schedule-card');
            if (!container || !data) return;

            var html = '<div class="flex items-center justify-between border-b pb-3">' +
                '<h3 class="text-lg font-bold text-slate-800">' +
                    (appData.isEditMode 
                        ? '<input type="text" value="' + escapeHtml(data.title) + '" onchange="updateDayTitle(\'' + dayKey + '\', this.value)" class="editable-input font-bold text-lg w-full">'
                        : escapeHtml(data.title)) +
                '</h3>' +
                '<span class="text-xs text-slate-500 font-medium">하교/차량 픽업 동선</span>' +
            '</div>' +
            '<div class="space-y-3">';

            data.items.forEach(function(item, index) {
                var badgeColor = "bg-slate-100 text-slate-700";
                if (item.badge === "학원") badgeColor = "bg-indigo-100 text-indigo-800";
                if (item.badge === "운동") badgeColor = "bg-red-100 text-red-800";
                if (item.badge === "여유시간") badgeColor = "bg-emerald-100 text-emerald-800 font-bold";
                if (item.badge === "바로연결") badgeColor = "bg-amber-100 text-amber-800 font-bold";

                if (appData.isEditMode) {
                    html += '<div class="p-3.5 bg-amber-50/50 rounded-xl border border-amber-200 flex flex-col gap-2 text-xs">' +
                        '<div class="flex items-center gap-2">' +
                            '<span class="font-bold">시간:</span>' +
                            '<input type="text" value="' + escapeHtml(item.time) + '" onchange="updateScheduleItem(\'' + dayKey + '\', ' + index + ', \'time\', this.value)" class="editable-input w-36">' +
                            '<span class="font-bold ml-2">활동명:</span>' +
                            '<input type="text" value="' + escapeHtml(item.name) + '" onchange="updateScheduleItem(\'' + dayKey + '\', ' + index + ', \'name\', this.value)" class="editable-input font-bold flex-grow">' +
                        '</div>' +
                        '<div class="flex items-center gap-2">' +
                            '<span class="font-bold">상세:</span>' +
                            '<input type="text" value="' + escapeHtml(item.detail) + '" onchange="updateScheduleItem(\'' + dayKey + '\', ' + index + ', \'detail\', this.value)" class="editable-input flex-grow">' +
                        '</div>' +
                    '</div>';
                } else {
                    html += '<div class="flex flex-col sm:flex-row sm:items-center justify-between p-3.5 bg-slate-50 rounded-xl hover:bg-slate-100 transition-all border border-slate-100 gap-2">' +
                        '<div class="flex items-center gap-3">' +
                            '<span class="text-xs font-bold text-slate-500 w-28 shrink-0">🕒 ' + escapeHtml(item.time) + '</span>' +
                            '<span class="text-sm font-bold text-slate-800">' + escapeHtml(item.name) + '</span>' +
                        '</div>' +
                        '<div class="flex items-center gap-2 justify-between sm:justify-end">' +
                            '<span class="text-xs text-slate-500">' + escapeHtml(item.detail) + '</span>' +
                            '<span class="text-[11px] px-2 py-0.5 rounded-md ' + badgeColor + '">' + escapeHtml(item.badge) + '</span>' +
                        '</div>' +
                    '</div>';
                }
            });

            html += '</div>';
            container.innerHTML = html;
        }

        function updateDayTitle(dayKey, value) {
            appData.schedules[dayKey].title = value;
            saveData();
        }

        function updateScheduleItem(dayKey, index, key, value) {
            appData.schedules[dayKey].items[index][key] = value;
            saveData();
        }

        var eveningPlans = {
            A: {
                title: "🟢 Plan A: 평소 루틴 (저녁 준비가 바로 되는 날)",
                items: [
                    { time: "19:15 ~ 19:30", title: "귀가 및 정돈", detail: "손 씻기, 알림장/가방 정리, 옷 갈아입기 / 저녁 준비" },
                    { time: "19:30 ~ 20:10", title: "저녁 식사", detail: "온 가족 식사 및 하루 일과 도란도란 대화" },
                    { time: "20:10 ~ 21:20", title: "⚡ 자기주도 몰입 학습 (70분)", detail: "수학(30m) ➡️ 영어(15m) ➡️ 국어/어휘(15m) ➡️ 내일가방(10m)" },
                    { time: "21:20 ~ 21:50", title: "🚿 샤워 & 취침 준비", detail: "21:20~21:30 샤워 들어가기 ➡️ 머리 말리기 및 소등 준비" },
                    { time: "21:50 ~ 22:10", title: "🛌 잠자리 취침 완료", detail: "22:00 ~ 22:10 사이 완전히 눕기 (수면 골든타임)" }
                ]
            },
            B: {
                title: "🟡 Plan B: 유연 루틴 (퇴근이 늦거나 저녁 준비가 길어지는 날)",
                items: [
                    { time: "19:15 ~ 19:40", title: "자기 관리 시간", detail: "부모님 저녁 준비 동안 손 씻기, 가방 정리, 할 일 체크" },
                    { time: "19:40 ~ 20:10", title: "📖 선(先) 집중 학습 (30분)", detail: "영어 단어 + 영어 학습지 1장 + 국어 독해 1장 미리 끝내기" },
                    { time: "20:10 ~ 20:50", title: "저녁 식사", detail: "식사 및 식탁 정돈" },
                    { time: "20:50 ~ 21:20", title: "📐 메인 학습: 수학 & 마무리 (30분)", detail: "수학 숙제 마저 마무리 & 내일 책가방 챙기기" },
                    { time: "21:20 ~ 21:50", title: "🚿 샤워 & 취침 준비", detail: "21:20~21:30 샤워 시작, 머리 말리기" },
                    { time: "21:50 ~ 22:10", title: "🛌 잠자리 취침 완료", detail: "22:00~22:10 취침 완수" }
                ]
            }
        };

        function setEveningPlan(planKey) {
            appData.currentPlanKey = planKey;
            var btnA = document.getElementById('btn-planA');
            var btnB = document.getElementById('btn-planB');

            if (planKey === 'A') {
                if (btnA) btnA.className = "px-2.5 py-1 rounded-lg text-xs font-bold bg-indigo-600 text-white";
                if (btnB) btnB.className = "px-2.5 py-1 rounded-lg text-xs font-bold bg-slate-100 text-slate-600 hover:bg-slate-200";
            } else {
                if (btnB) btnB.className = "px-2.5 py-1 rounded-lg text-xs font-bold bg-indigo-600 text-white";
                if (btnA) btnA.className = "px-2.5 py-1 rounded-lg text-xs font-bold bg-slate-100 text-slate-600 hover:bg-slate-200";
            }

            var plan = eveningPlans[planKey];
            var container = document.getElementById('evening-plan-container');
            if (!container) return;

            var html = '<div class="border-b pb-3"><h3 class="text-lg font-bold text-slate-800">' + plan.title + '</h3></div><div class="space-y-3">';
            plan.items.forEach(function(item) {
                html += '<div class="p-4 bg-slate-50 rounded-xl border border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-2">' +
                    '<div class="w-36 text-xs font-bold text-indigo-600 shrink-0">⏰ ' + item.time + '</div>' +
                    '<div class="flex-grow">' +
                        '<h4 class="text-sm font-bold text-slate-800 mb-0.5">' + item.title + '</h4>' +
                        '<p class="text-xs text-slate-600">' + item.detail + '</p>' +
                    '</div>' +
                '</div>';
            });
            html += '</div>';
            container.innerHTML = html;
        }

        var weekendData = {
            sat: {
                title: "🗓️ 토요일 알찬 타임라인",
                items: [
                    { time: "06:30 ~ 07:00", task: "기상 및 아침 뇌 깨우기", note: "6시 30분~7시 사이 기상" },
                    { time: "07:00 ~ 08:30", task: "📝 [주말 모닝 학습] 90분 몰입 완주", note: "기상 직후 바로 공부! (수학 문제집+영어+독서)" },
                    { time: "08:30 ~ 09:00", task: "🍚 아침 식사 및 정돈", note: "8시 30분~9시 사이 온 가족 아침 식사" },
                    { time: "09:00 ~ 10:00", task: "🔬 흥미 탐구 및 1차 게임 준비", note: "자유시간 및 탐구 타임" },
                    { time: "10:00 ~ 12:00", task: "🎮 게임 & 자유시간 1차 (120분)", note: "공부 먼저 끝내고 기분 좋게 자유시간" },
                    { time: "12:00 ~ 13:00", task: "🍱 점심 식사", note: "맛있는 점심 식사" },
                    { time: "13:00 ~ 15:30", task: "⚾ [신체활동] 아빠와 야구", note: "햇빛 쬐며 신체 발달 & 스트레스 해소" },
                    { time: "15:30 ~ 16:30", task: "🔬 흥미 탐구 (과학/역사)", note: "좋아하는 과학 다큐, 실험 키트, 역사 책" },
                    { time: "16:30 ~ 18:00", task: "🎮 게임 & 자유시간 2차 (90분)", note: "게임 3시간 쪼개기 법칙 완수" },
                    { time: "18:00 ~ 19:00", task: "🍖 저녁 식사", note: "가족 저녁 식사" },
                    { time: "19:00 ~ 20:00", task: "🎲 가족 화목 시간", note: "보드게임 또는 고스톱 타임" },
                    { time: "20:00 ~ 21:00", task: "📖 밤 몰입 독서 1시간", note: "부모님 운동 시간 동안 아이 차분한 독서" },
                    { time: "21:00 ~ 21:20", task: "🛋️ 자유 휴식 & 샤워 준비", note: "취침 전 마음 정돈" },
                    { time: "21:20 ~ 22:10", task: "🚿 샤워 및 취침", note: "21:20 샤워 ➡️ 22:00~22:10 취침" }
                ]
            },
            sun: {
                title: "🗓️ 일요일 알찬 타임라인 (예배 포함)",
                items: [
                    { time: "06:30 ~ 07:00", task: "기상 및 아침 뇌 깨우기", note: "평일과 동일한 수면 리듬 유지" },
                    { time: "07:00 ~ 08:30", task: "📝 [주말 모닝 학습] 90분 몰입 완주", note: "기상 직후 바로 공부! (수학 문제집+영어+독서)" },
                    { time: "08:30 ~ 09:00", task: "🍚 아침 식사 및 정돈", note: "8시 30분~9시 사이 온 가족 아침 식사" },
                    { time: "09:00 ~ 10:00", task: "🙏 인터넷 예배", note: "가족 인터넷 예배 드리기" },
                    { time: "10:00 ~ 12:00", task: "🎮 게임 & 자유시간 1차 (120분)", note: "공부 완주 후 기분 좋은 자유시간" },
                    { time: "12:00 ~ 13:00", task: "🍱 점심 식사", note: "점심 식사" },
                    { time: "13:00 ~ 15:30", task: "⚾ [신체활동] 아빠와 야구 / 외출", note: "야외활동 또는 주말 여행/외출" },
                    { time: "15:30 ~ 16:30", task: "🔬 흥미 탐구 (과학/역사)", note: "자연 관찰, 과학동아 시청 등" },
                    { time: "16:30 ~ 18:00", task: "🎮 게임 & 자유시간 2차 (90분)", note: "게임 시간 마무리" },
                    { time: "18:00 ~ 19:00", task: "🍖 저녁 식사", note: "가족 저녁 식사" },
                    { time: "19:00 ~ 20:00", task: "🎲 가족 화목 시간", note: "보드게임 또는 이야기 나누기" },
                    { time: "20:00 ~ 21:00", task: "📖 밤 몰입 독서 1시간", note: "부모님 운동 시간 동안 아이 차분한 독서" },
                    { time: "21:00 ~ 21:20", task: "🛋️ 자유 휴식 & 샤워 준비", note: "월요일 준비" },
                    { time: "21:20 ~ 22:10", task: "🚿 샤워 및 취침", note: "21:20 샤워 ➡️ 22:00~22:10 취침" }
                ]
            }
        };

        function setWeekendDay(dayKey) {
            appData.currentWeekendKey = dayKey;
            var btnSat = document.getElementById('btn-sat');
            var btnSun = document.getElementById('btn-sun');

            if (dayKey === 'sat') {
                if (btnSat) btnSat.className = "px-3 py-1 rounded-lg text-xs font-bold bg-emerald-600 text-white";
                if (btnSun) btnSun.className = "px-3 py-1 rounded-lg text-xs font-bold bg-slate-100 text-slate-600 hover:bg-slate-200";
            } else {
                if (btnSun) btnSun.className = "px-3 py-1 rounded-lg text-xs font-bold bg-emerald-600 text-white";
                if (btnSat) btnSat.className = "px-3 py-1 rounded-lg text-xs font-bold bg-slate-100 text-slate-600 hover:bg-slate-200";
            }

            var data = weekendData[dayKey];
            var titleEl = document.getElementById('weekend-title');
            if (titleEl) titleEl.innerText = data.title;
            var container = document.getElementById('weekend-timeline-list');
            if (!container) return;

            var html = "";
            data.items.forEach(function(item) {
                var isHighlight = item.task.indexOf("야구") !== -1 || item.task.indexOf("독서") !== -1 || item.task.indexOf("모닝 학습") !== -1;
                var bgClass = isHighlight ? "bg-emerald-50/70 border-emerald-200" : "bg-slate-50 border-slate-100";

                html += '<div class="p-3.5 rounded-xl border ' + bgClass + ' flex flex-col sm:flex-row sm:items-center justify-between gap-2">' +
                    '<div class="flex items-center gap-3">' +
                        '<span class="text-xs font-bold text-slate-500 w-32 shrink-0">⏰ ' + escapeHtml(item.time) + '</span>' +
                        '<span class="text-sm font-bold text-slate-800">' + escapeHtml(item.task) + '</span>' +
                    '</div>' +
                    '<span class="text-xs text-slate-600">' + escapeHtml(item.note) + '</span>' +
                '</div>';
            });

            container.innerHTML = html;
        }

        function renderChecklists() {
            var wContainer = document.getElementById('weekday-checklist-container');
            var wCount = document.getElementById('weekday-count');
            var wCheckedCount = 0;

            if (wContainer) {
                var wHtml = "";
                appData.checklistWeekday.forEach(function(item, idx) {
                    if (item.checked) wCheckedCount++;
                    wHtml += '<label class="flex items-center gap-3 p-2.5 bg-slate-50 rounded-xl hover:bg-slate-100 cursor-pointer border border-slate-100">' +
                        '<input type="checkbox" ' + (item.checked ? 'checked' : '') + ' onchange="toggleCheckItem(\'w\', ' + idx + ')" class="w-4 h-4 text-blue-600 rounded">' +
                        '<span class="' + (item.checked ? 'line-through text-slate-400 font-medium' : 'text-slate-700 font-medium') + ' flex-grow">' +
                            (appData.isEditMode 
                                ? '<input type="text" value="' + escapeHtml(item.text) + '" onchange="updateCheckItemText(\'w\', ' + idx + ', this.value)" class="editable-input text-xs w-full">'
                                : escapeHtml(item.text)) +
                        '</span>' +
                    '</label>';
                });
                wContainer.innerHTML = wHtml;
            }
            if (wCount) wCount.innerText = wCheckedCount + ' / ' + appData.checklistWeekday.length + ' 완료';

            var wkContainer = document.getElementById('weekend-checklist-container');
            var wkCount = document.getElementById('weekend-count');
            var wkCheckedCount = 0;

            if (wkContainer) {
                var wkHtml = "";
                appData.checklistWeekend.forEach(function(item, idx) {
                    if (item.checked) wkCheckedCount++;
                    wkHtml += '<label class="flex items-center gap-3 p-2.5 bg-slate-50 rounded-xl hover:bg-slate-100 cursor-pointer border border-slate-100">' +
                        '<input type="checkbox" ' + (item.checked ? 'checked' : '') + ' onchange="toggleCheckItem(\'wk\', ' + idx + ')" class="w-4 h-4 text-emerald-600 rounded">' +
                        '<span class="' + (item.checked ? 'line-through text-slate-400 font-medium' : 'text-slate-700 font-medium') + ' flex-grow">' +
                            (appData.isEditMode 
                                ? '<input type="text" value="' + escapeHtml(item.text) + '" onchange="updateCheckItemText(\'wk\', ' + idx + ', this.value)" class="editable-input text-xs w-full">'
                                : escapeHtml(item.text)) +
                        '</span>' +
                    '</label>';
                });
                wkContainer.innerHTML = wkHtml;
            }
            if (wkCount) wkCount.innerText = wkCheckedCount + ' / ' + appData.checklistWeekend.length + ' 완료';

            updateStreakBadge();
        }

        function toggleCheckItem(type, index) {
            if (type === 'w') {
                appData.checklistWeekday[index].checked = !appData.checklistWeekday[index].checked;
            } else {
                appData.checklistWeekend[index].checked = !appData.checklistWeekend[index].checked;
            }
            saveData();
            renderChecklists();
        }

        function updateCheckItemText(type, index, value) {
            if (type === 'w') {
                appData.checklistWeekday[index].text = value;
            } else {
                appData.checklistWeekend[index].text = value;
            }
            saveData();
        }

        function updateStreakBadge() {
            var streakBadge = document.getElementById('streak-badge');
            if (!streakBadge) return;

            var streak = 0;
            var wDone = appData.checklistWeekday.filter(function(i) { return i.checked; }).length;
            var wkDone = appData.checklistWeekend.filter(function(i) { return i.checked; }).length;

            if (wDone === 5 || wkDone === 5) streak++;

            for (var i = 0; i < appData.historyLog.length; i++) {
                if (appData.historyLog[i].count >= 4) streak++;
                else break;
            }

            streakBadge.innerHTML = '🔥 ' + streak + '일 연속 미션 완료 중!';
        }

        function renderHistoryLog() {
            var container = document.getElementById('history-cards-container');
            var summary = document.getElementById('history-total-summary');
            if (!container) return;

            var html = "";
            var logs = appData.historyLog.slice(0, 7);

            if (logs.length === 0) {
                html = '<div class="col-span-full text-center py-6 text-xs text-slate-400">아직 저장된 과거 기록이 없습니다. 오늘 미션을 시작해보세요!</div>';
            } else {
                logs.forEach(function(log) {
                    var isSuccess = log.count >= 4;
                    var cardBg = isSuccess ? "bg-indigo-50 border-indigo-200 text-indigo-900" : "bg-slate-50 border-slate-200 text-slate-700";
                    html += '<div class="p-3 rounded-xl border ' + cardBg + ' text-center flex flex-col items-center justify-center">' +
                        '<span class="text-[10px] font-semibold text-slate-500">' + log.date.slice(5) + '</span>' +
                        '<span class="text-base font-black my-1">' + log.count + ' / ' + log.total + '</span>' +
                        '<span class="text-[10px] font-bold ' + (isSuccess ? 'text-indigo-600' : 'text-slate-400') + '">' + (isSuccess ? '🎉 완수' : '수고했어요') + '</span>' +
                    '</div>';
                });
            }
            container.innerHTML = html;
            if (summary) summary.innerText = '최근 ' + logs.length + '일 기록 저장됨';
        }

        async function fetchGeminiWithRetry(apiUrl, payload, retries, delay) {
            retries = retries || 2;
            delay = delay || 800;
            if (!apiKey) throw new Error("API Key missing");
            for (var i = 0; i < retries; i++) {
                try {
                    var response = await fetch(apiUrl, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    if (response.ok) {
                        return await response.json();
                    }
                } catch (err) {
                    if (i === retries - 1) throw err;
                }
                await new Promise(function(res) { setTimeout(res, delay * Math.pow(2, i)); });
            }
            throw new Error("API call failed");
        }

        async function generateAIQuiz() {
            var subject = document.getElementById('ai-quiz-subject').value;
            var resultBox = document.getElementById('ai-quiz-result');
            var btn = document.getElementById('btn-gen-quiz');

            resultBox.classList.remove('hidden');
            resultBox.innerHTML = '<div class="flex items-center gap-2 text-indigo-600 font-bold">' +
                '<div class="spinner-dark"></div>' +
                '<span>한국사능력검정시험 유형 AI 퀴즈를 생성하는 중입니다...</span>' +
            '</div>';
            btn.disabled = true;

            var systemPrompt = "당신은 한국사능력검정시험(한능검) 출제위원입니다. 초등학교 5학년(한능검 기본 수준)에 맞추어 인물, 유물, 사료 힌트를 바탕으로 한 4지선다형 객관식 퀴즈 1개를 생성하세요.";
            var userQuery = subject + " 주제로 한국사능력검정시험(한능검 기본/초등) 스타일의 1분 퀴즈 1개를 만들어주세요.";

            var apiUrl = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key=' + apiKey;
            var payload = {
                contents: [{ parts: [{ text: userQuery }] }],
                systemInstruction: { parts: [{ text: systemPrompt }] }
            };

            try {
                var data = await fetchGeminiWithRetry(apiUrl, payload);
                var quizText = data.candidates && data.candidates[0] && data.candidates[0].content && data.candidates[0].content.parts && data.candidates[0].content.parts[0] && data.candidates[0].content.parts[0].text;
                if (!quizText) throw new Error("API response empty");
                
                resultBox.innerHTML = '<div class="bg-indigo-50/70 border border-indigo-200 p-3.5 rounded-xl space-y-2 text-slate-800">' +
                    '<div class="font-bold text-indigo-900 flex items-center justify-between border-b border-indigo-200 pb-2">' +
                        '<span>📜 한국사능력검정시험(한능검) 실전 퀴즈</span>' +
                        '<span class="text-[10px] bg-indigo-200 text-indigo-800 px-2 py-0.5 rounded-md font-bold">Gemini AI</span>' +
                    '</div>' +
                    '<div class="whitespace-pre-line text-xs font-medium text-slate-700 leading-relaxed">' + escapeHtml(quizText) + '</div>' +
                '</div>';
            } catch (err) {
                renderFallbackQuiz(subject);
            } finally {
                btn.disabled = false;
            }
        }

        function renderFallbackQuiz(subject) {
            var resultBox = document.getElementById('ai-quiz-result');
            var fallbackBank = {
                "한국사": [
                    { 
                        q: "Q. 다음 설명에 해당하는 조선 시대의 문화유산은 무엇일까요?\n- 정조 임금이 아버지 사도세자의 묘를 옮기면서 건설함\n- 정약용이 거중기를 활용하여 과학적으로 축조함", 
                        options: ["1. 수원 화성", "2. 남한산성", "3. 한양도성", "4. 북한산성"], 
                        desc: "💡 힌트 & 해설: 정조는 정약용이 만든 거중기를 활용하여 수원 화성을 건축했습니다.",
                        a: "1번 수원 화성" 
                    }
                ],
                "과학": [
                    { 
                        q: "Q. 초등 5학년 과학 [용액의 성질]: 푸른색 리트머스 종이를 붉은색으로 변하게 하는 용액의 성질은 무엇일까요?", 
                        options: ["1. 염기성", "2. 산성", "3. 중성", "4. 점성"], 
                        desc: "💡 힌트 & 해설: 식초, 레몬즙 같은 산성 용액은 푸른색 리트머스 종이를 붉게 바꿉니다.",
                        a: "2번 산성" 
                    }
                ],
                "영어": [
                    { 
                        q: "Q. 'He is very ______ solving math puzzles.' (그는 수학 퀴즈 푸는 것을 잘해.)", 
                        options: ["1. good at", "2. interested on", "3. afraid of", "4. famous to"], 
                        desc: "💡 힌트 & 해설: be good at ~은 ~를 잘한다는 뜻입니다.",
                        a: "1번 good at" 
                    }
                ]
            };

            var key = subject.indexOf("한국사") !== -1 ? "한국사" : subject.indexOf("과학") !== -1 ? "과학" : "영어";
            var items = fallbackBank[key] || fallbackBank["한국사"];
            var selected = items[Math.floor(Math.random() * items.length)];

            resultBox.innerHTML = '<div class="bg-indigo-50/70 border border-indigo-200 p-4 rounded-xl space-y-3 text-slate-800">' +
                '<div class="font-bold text-indigo-900 flex items-center justify-between border-b border-indigo-200 pb-2">' +
                    '<span>🎯 [초등 5학년 퀴즈] ' + key + ' 탐구</span>' +
                    '<span class="text-[10px] bg-indigo-200 text-indigo-800 px-2 py-0.5 rounded-md font-bold">도전 퀴즈</span>' +
                '</div>' +
                '<div class="text-xs font-extrabold text-slate-900 leading-relaxed">' + selected.q + '</div>' +
                '<div class="grid grid-cols-1 sm:grid-cols-2 gap-1.5 text-xs text-slate-700 font-semibold my-1">' +
                    selected.options.map(function(o) { return '<div class="bg-white/80 p-2 rounded-lg border border-indigo-100">' + o + '</div>'; }).join('') +
                '</div>' +
                '<div class="text-[11px] text-indigo-900 bg-white/90 p-2.5 rounded-lg border border-indigo-200 leading-relaxed">' + selected.desc + '</div>' +
                '<details class="mt-2 pt-2 border-t border-indigo-200/60">' +
                    '<summary class="cursor-pointer text-xs font-bold text-indigo-600 hover:text-indigo-800">🔒 정답 확인하기 (클릭)</summary>' +
                    '<div class="mt-2 text-xs font-black text-emerald-700 bg-emerald-50 p-2 rounded-lg border border-emerald-200 inline-block">✅ 정답: ' + selected.a + '</div>' +
                '</details>' +
            '</div>';
        }

        async function generateAIVoice() {
            var sitKey = document.getElementById('tts-situation').value;
            var voiceName = document.getElementById('tts-voice').value;
            var btn = document.getElementById('btn-gen-tts');
            var statusBox = document.getElementById('tts-status');

            statusBox.classList.remove('hidden');
            btn.disabled = true;

            var cleanText = getDynamicCheerPhrase(sitKey);

            statusBox.innerHTML = '<div class="p-3.5 bg-purple-50/80 border border-purple-200 rounded-xl text-left space-y-2">' +
                '<div class="font-bold text-purple-900 text-xs flex items-center justify-between border-b border-purple-200 pb-1.5">' +
                    '<span class="flex items-center gap-1.5">💬 AI 멘토의 응원 메시지</span>' +
                    '<span id="tts-audio-status" class="text-[10px] bg-purple-200 text-purple-800 px-2 py-0.5 rounded-full font-bold">🎙️ 음성 준비 중...</span>' +
                '</div>' +
                '<div class="text-xs text-slate-800 font-medium leading-relaxed whitespace-pre-line">' + escapeHtml(cleanText) + '</div>' +
            '</div>';

            var apiUrl = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key=' + apiKey;
            var payload = {
                contents: [{ parts: [{ text: cleanText }] }],
                generationConfig: {
                    responseModalities: ["AUDIO"],
                    speechConfig: { voiceConfig: { prebuiltVoiceConfig: { voiceName: voiceName } } }
                },
                model: "gemini-2.5-flash-preview-tts"
            };

            var statusEl = document.getElementById('tts-audio-status');

            try {
                var data = await fetchGeminiWithRetry(apiUrl, payload);
                var part = data.candidates && data.candidates[0] && data.candidates[0].content && data.candidates[0].content.parts && data.candidates[0].content.parts[0];
                var audioBase64 = part && part.inlineData && part.inlineData.data;
                var mimeType = (part && part.inlineData && part.inlineData.mimeType) || "";

                if (audioBase64) {
                    if (statusEl) statusEl.innerText = "🔊 음성 재생 중!";
                    var sampleRate = 24000;
                    var match = mimeType.match(/rate=(\d+)/);
                    if (match) sampleRate = parseInt(match[1], 10);

                    var pcmBuffer = base64ToArrayBuffer(audioBase64);
                    var pcm16 = new Int16Array(pcmBuffer);
                    var wavBlob = pcm16ToWavBlob(pcm16, sampleRate);
                    var audioUrl = URL.createObjectURL(wavBlob);

                    var audio = new Audio(audioUrl);
                    audio.play();
                    audio.onended = function() { if (statusEl) statusEl.innerText = "✅ 재생 완료! 힘내서 파이팅!"; };
                } else {
                    throw new Error("TTS base64 missing");
                }
            } catch (err) {
                speakWithWebSpeech(cleanText, voiceName, statusEl);
            } finally {
                btn.disabled = false;
            }
        }

        function getDynamicCheerPhrase(sitKey) {
            var greet = "멋진 5학년 친구!";
            var phrases = {
                morning: greet + " 좋은 아침이에요! 06시 30분 기상 완수! 오늘 아침 한국사 시청하고 활기차게 등교해 봐요!",
                evening: greet + " 오늘 70분 저녁 몰입 학습 진짜 대단했어요! 샤워 후 편안히 쉬세요!",
                weekend: greet + " 주말 모닝 학습 완주까지 해내다니 정말 최고의 하루였어요!",
                together: greet + " 의샤의샤! 함께 힘내봐요!"
            };
            return phrases[sitKey] || phrases.together;
        }

        function speakWithWebSpeech(cleanText, voiceName, statusEl) {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
                var utterance = new SpeechSynthesisUtterance(cleanText);
                utterance.lang = 'ko-KR';
                utterance.pitch = voiceName === 'Puck' ? 1.35 : 1.0;
                utterance.rate = 1.0;
                if (statusEl) statusEl.innerText = '🔊 음성 재생 중!';
                window.speechSynthesis.speak(utterance);
                utterance.onend = function() { if (statusEl) statusEl.innerText = "✅ 재생 완료! 오늘도 힘내자!"; };
            } else {
                if (statusEl) statusEl.innerText = "👏 축하해요! 오늘 미션 완수!";
            }
        }

        function base64ToArrayBuffer(base64) {
            var binaryString = window.atob(base64);
            var len = binaryString.length;
            var bytes = new Uint8Array(len);
            for (var i = 0; i < len; i++) {
                bytes[i] = binaryString.charCodeAt(i);
            }
            return bytes.buffer;
        }

        function pcm16ToWavBlob(pcm16Data, sampleRate) {
            sampleRate = sampleRate || 24000;
            var buffer = new ArrayBuffer(44 + pcm16Data.length * 2);
            var view = new DataView(buffer);

            writeString(view, 0, 'RIFF');
            view.setUint32(4, 36 + pcm16Data.length * 2, true);
            writeString(view, 8, 'WAVE');
            writeString(view, 12, 'fmt ');
            view.setUint32(16, 16, true);
            view.setUint16(20, 1, true);
            view.setUint16(22, 1, true);
            view.setUint32(24, sampleRate, true);
            view.setUint32(28, sampleRate * 2, true);
            view.setUint16(32, 2, true);
            view.setUint16(34, 16, true);
            writeString(view, 36, 'data');
            view.setUint32(40, pcm16Data.length * 2, true);

            for (var i = 0; i < pcm16Data.length; i++) {
                view.setInt16(44 + i * 2, pcm16Data[i], true);
            }

            return new Blob([buffer], { type: 'audio/wav' });
        }

        function writeString(view, offset, string) {
            for (var i = 0; i < string.length; i++) {
                view.setUint8(offset + i, string.charCodeAt(i));
            }
        }

        async function generateAISticker() {
            var todayStr = getTodayString();
            var existingTodaySticker = (appData.stickers || []).find(function(s) { return s.date === todayStr; });
            var resultContainer = document.getElementById('sticker-result');
            var btn = document.getElementById('btn-gen-sticker');

            if (existingTodaySticker) {
                resultContainer.innerHTML = '<div class="p-3 bg-amber-50 border border-amber-200 rounded-2xl text-center space-y-1">' +
                    '<div class="text-xs font-bold text-amber-900">⚠️ 오늘의 칭찬 스티커는 이미 획득했습니다! (1일 1장)</div>' +
                '</div>';
                return;
            }

            var userPrompt = document.getElementById('sticker-prompt').value;
            resultContainer.innerHTML = '<div class="flex flex-col items-center justify-center p-6 text-pink-600 gap-2"><div class="spinner-dark"></div><span class="text-xs font-bold">칭찬 스티커를 생성하는 중입니다...</span></div>';
            btn.disabled = true;

            var fullPrompt = 'Cute cartoon badge sticker icon for a 5th grade Korean student: ' + userPrompt;
            var apiUrl = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-image:generateContent?key=' + apiKey;
            var payload = { contents: [{ parts: [{ text: fullPrompt }] }], generationConfig: { responseModalities: ['TEXT', 'IMAGE'] } };

            try {
                var data = await fetchGeminiWithRetry(apiUrl, payload);
                var base64Data = data && data.candidates && data.candidates[0] && data.candidates[0].content && data.candidates[0].content.parts && data.candidates[0].content.parts.find(function(p) { return p.inlineData; }) && data.candidates[0].content.parts.find(function(p) { return p.inlineData; }).inlineData.data;

                if (base64Data) {
                    var stickerObj = { id: Date.now(), date: getTodayString(), title: userPrompt, img: 'data:image/png;base64,' + base64Data };
                    saveStickerToCollection(stickerObj);
                    resultContainer.innerHTML = '<div class="flex flex-col items-center gap-2"><img src="' + stickerObj.img + '" class="w-28 h-28 object-contain rounded-2xl shadow-md border border-pink-100"><span class="text-xs font-bold text-pink-700">🎉 축하합니다! 칭찬 스티커가 내 스티커북에 저장되었습니다!</span></div>';
                } else {
                    throw new Error("No image data");
                }
            } catch (err) {
                var stickerObjFallback = { id: Date.now(), date: getTodayString(), title: userPrompt, icon: '🏆', gradient: 'from-pink-400 to-purple-500' };
                saveStickerToCollection(stickerObjFallback);
                resultContainer.innerHTML = '<div class="text-xs font-bold text-pink-900">✨ 미션 완수 배지가 수집되었습니다!</div>';
            } finally {
                btn.disabled = false;
            }
        }

        function saveStickerToCollection(stickerObj) {
            if (!appData.stickers) appData.stickers = [];
            appData.stickers.push(stickerObj);
            saveData();
            renderStickerGallery();
        }

        function updateRewardGoal(value) {
            appData.rewardGoal = value;
            saveData();
        }

        function renderStickerGallery() {
            var container = document.getElementById('sticker-gallery');
            var badge = document.getElementById('sticker-count-badge');
            var goalInput = document.getElementById('reward-goal-input');
            var progressText = document.getElementById('reward-progress-text');
            if (!container) return;

            var stickers = appData.stickers || [];
            if (badge) badge.innerText = stickers.length;
            if (goalInput && appData.rewardGoal !== undefined) goalInput.value = appData.rewardGoal;

            var count = stickers.length;
            var percent = Math.min(100, Math.round((count / 30) * 100));
            if (progressText) progressText.innerText = count + ' / 30개 (' + percent + '%)';

            var html = "";
            for (var i = 0; i < 30; i++) {
                if (stickers[i]) {
                    var st = stickers[i];
                    if (st.img) {
                        html += '<div class="w-8 h-8 sm:w-9 sm:h-9 rounded-lg border-2 border-pink-400 bg-white overflow-hidden shadow-sm flex items-center justify-center"><img src="' + st.img + '" class="w-full h-full object-cover"></div>';
                    } else {
                        html += '<div class="w-8 h-8 sm:w-9 sm:h-9 rounded-lg border-2 border-pink-400 bg-gradient-to-tr ' + (st.gradient || 'from-pink-300 to-indigo-300') + ' flex items-center justify-center text-sm shadow-sm">' + (st.icon || '⭐') + '</div>';
                    }
                } else {
                    html += '<div class="w-8 h-8 sm:w-9 sm:h-9 rounded-lg border border-dashed border-pink-200 bg-white/60 flex items-center justify-center text-[9px] text-pink-300 font-bold">' + (i + 1) + '</div>';
                }
            }
            container.innerHTML = html;
        }

        function resetStickers() {
            if (window.confirm("모은 칭찬 스티커판을 초기화하시겠습니까?")) {
                appData.stickers = [];
                saveData();
                renderStickerGallery();
                document.getElementById('sticker-result').innerHTML = '<span class="text-xs text-slate-400">새로운 30개 스티커판이 시작되었습니다!</span>';
            }
        }

        async function searchAIQna() {
            var query = document.getElementById('search-query').value;
            var container = document.getElementById('search-result');
            var btn = document.getElementById('btn-gen-search');

            container.classList.remove('hidden');
            container.innerHTML = '<div class="flex items-center gap-2 text-emerald-600 font-bold text-xs"><div class="spinner-dark"></div><span>Google 검색으로 탐색 중입니다...</span></div>';
            btn.disabled = true;

            var systemPrompt = "당신은 초등학교 5학년 학생을 위한 백과사전 튜터입니다.";
            var apiUrl = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key=' + apiKey;
            var payload = { contents: [{ parts: [{ text: query }] }], tools: [{ "google_search": {} }], systemInstruction: { parts: [{ text: systemPrompt }] } };

            try {
                var data = await fetchGeminiWithRetry(apiUrl, payload);
                var text = data.candidates && data.candidates[0] && data.candidates[0].content && data.candidates[0].content.parts && data.candidates[0].content.parts[0] && data.candidates[0].content.parts[0].text;
                container.innerHTML = '<div class="text-slate-800 space-y-2"><div class="font-bold text-emerald-900">💡 AI 탐구 답변</div><div class="whitespace-pre-line text-xs leading-relaxed text-slate-700">' + escapeHtml(text || "답변을 가져올 수 없습니다.") + '</div></div>';
            } catch (err) {
                renderFallbackQna(query, container);
            } finally {
                btn.disabled = false;
            }
        }

        function renderFallbackQna(query, container) {
            var answerText = "💡 초등 5학년 탐구 백과:\n\n이순신 장군님은 임진왜란 당시 학익진 전법과 거북선으로 나라를 구한 위대한 영웅입니다! 대표적인 3대 대첩은 한산도 대첩, 명량 대첩, 노량 대첩입니다.";
            container.innerHTML = '<div class="text-slate-800 space-y-2"><div class="font-bold text-emerald-900">💡 [5학년 추천 백과] 탐구 답변</div><div class="whitespace-pre-line text-xs leading-relaxed text-slate-700">' + answerText + '</div></div>';
        }

        function initCharts() {
            var pieCanvas = document.getElementById('timePieChart');
            if (pieCanvas) {
                new Chart(pieCanvas.getContext('2d'), {
                    type: 'doughnut',
                    data: {
                        labels: ['수면 (8.5시간)', '학교/학원 (8시간)', '여유/이동/식사 (6.3시간)', '저녁몰입학습 (1.1시간)'],
                        datasets: [{ data: [35, 33, 27, 5], backgroundColor: ['#6366f1', '#3b82f6', '#f59e0b', '#10b981'], borderWidth: 2, borderColor: '#ffffff' }]
                    },
                    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } } } }
                });
            }

            var barCanvas = document.getElementById('studyBarChart');
            if (barCanvas) {
                new Chart(barCanvas.getContext('2d'), {
                    type: 'bar',
                    data: {
                        labels: ['수학 (학원숙제)', '영어 (단어+학습지)', '국어 (어휘/독해)', '마무리 (가방/책상)'],
                        datasets: [{ label: '분(Min)', data: [30, 15, 15, 10], backgroundColor: ['#3b82f6', '#8b5cf6', '#ec4899', '#64748b'], borderRadius: 8 }]
                    },
                    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, max: 35, ticks: { stepSize: 10 } } } }
                });
            }
        }

        function escapeHtml(text) {
            if (!text) return "";
            return String(text).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
        }

        // 초기화 함수 직접 실행
        window.onload = function() {
            loadData();
            renderDaySchedule('mon');
            setEveningPlan('A');
            setWeekendDay('sat');
            renderChecklists();
            renderStickerGallery();
            updateStreakBadge();
            initCharts();
        };
    </script>
</body>
</html>"""

# API 키를 안전하게 치환하여 Streamlit 컴포넌트로 렌더링
final_html = html_code.replace("__API_KEY__", api_key)

st.components.v1.html(
    final_html,
    height=1300,
    scrolling=True,
)
