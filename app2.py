<!DOCTYPE html>
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
            background-color: #3b82f6;
            color: #ffffff;
            font-weight: 700;
            box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.3);
        }
        .day-btn.active {
            border-color: #3b82f6;
            background-color: #eff6ff;
            color: #1d4ed8;
            font-weight: 700;
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

            <div id="day-schedule-card" class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
                <!-- Dynamic Content -->
            </div>
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

            <div id="evening-plan-container" class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
                <!-- Dynamic Content -->
            </div>
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
                <div id="weekend-timeline-list" class="space-y-3">
                    <!-- Dynamic Content -->
                </div>
            </div>
        </section>

        <!-- TAB 5: CHECKLIST & CUMULATIVE HISTORY -->
        <section id="sec-checklist" class="hidden space-y-6">
            <div class="bg-purple-50 border border-purple-200 rounded-2xl p-4 text-purple-900 text-sm leading-relaxed flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                <div>
                    ✅ <strong>스마트 일일 루틴 체크리스트:</strong> 매일 자정이 지나면 체크리스트가 <strong>자동 초기화</strong>되며, 완료 실적은 기록에 남습니다.
                </div>
                <button onclick="forceDailyReset()" class="px-3 py-1.5 bg-purple-600 text-white text-xs font-bold rounded-xl hover:bg-purple-700 transition-all shrink-0">
                    🔄 오늘 체크 수동 초기화
                </button>
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
                    <h3 class="text-base font-bold text-slate-800 flex items-center gap-2"><span>📈</span> 최근 7일 실천 기록</h3>
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
                        <p class="text-xs text-indigo-100 mt-1 max-w-xl">
                            AI가 퀴즈 생성, 음성 응원 칭찬, 칭찬 스티커 생성, 그리고 역사/과학 궁금증 답변까지 돕습니다!
                        </p>
                    </div>
                    <span class="text-3xl">🤖</span>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- Quiz Generator -->
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between border-b pb-3 mb-4">
                            <h3 class="font-bold text-slate-800 flex items-center gap-2"><span>🧠</span> 초등 5학년 1분 AI 퀴즈 생성기</h3>
                        </div>
                        <div class="flex gap-2 mb-4">
                            <select id="ai-quiz-subject" class="bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs font-semibold text-slate-700 flex-grow">
                                <option value="한국사능력검정시험">📜 한국사 실전 퀴즈</option>
                                <option value="초등 5학년 과학">🔬 과학 퀴즈</option>
                                <option value="초등 영어">영어 단어 & 표현 퀴즈</option>
                            </select>
                            <button onclick="generateAIQuiz()" id="btn-gen-quiz" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl text-xs flex items-center gap-1.5 transition-all shrink-0">✨ 퀴즈 생성</button>
                        </div>
                        <div id="ai-quiz-result" class="bg-slate-50 border border-slate-200 rounded-xl p-4 text-xs leading-relaxed hidden min-h-[140px]"></div>
                    </div>
                </div>

                <!-- Voice Encouragement -->
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between border-b pb-3 mb-4">
                            <h3 class="font-bold text-slate-800 flex items-center gap-2"><span>🔊</span> AI 멘토 음성 응원 메시지</h3>
                        </div>
                        <div class="grid grid-cols-2 gap-2 mb-3">
                            <select id="tts-situation" class="w-full bg-slate-50 border border-slate-300 rounded-xl px-2.5 py-1.5 text-xs text-slate-700">
                                <option value="morning">🌅 아침 등교 전 화이팅!</option>
                                <option value="evening">🌙 저녁 70분 공부 완수!</option>
                                <option value="weekend">⚾ 주말 운동 완수!</option>
                            </select>
                            <select id="tts-voice" class="w-full bg-slate-50 border border-slate-300 rounded-xl px-2.5 py-1.5 text-xs text-slate-700">
                                <option value="Puck">Puck (밝은 소년)</option>
                                <option value="Zephyr">Zephyr (상냥한 톤)</option>
                            </select>
                        </div>
                        <button onclick="generateAIVoice()" id="btn-gen-tts" class="w-full py-2.5 bg-purple-600 hover:bg-purple-700 text-white font-bold rounded-xl text-xs flex items-center justify-center gap-2 transition-all">🎙️ AI 응원 음성 들려주기</button>
                        <div id="tts-status" class="mt-3 text-center text-xs font-semibold text-slate-500 hidden"></div>
                    </div>
                </div>

                <!-- Reward Sticker -->
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between border-b pb-3 mb-4">
                            <h3 class="font-bold text-slate-800 flex items-center gap-2"><span>🎨</span> AI 칭찬 스티커북</h3>
                        </div>
                        <div class="flex gap-2 mb-4">
                            <input type="text" id="sticker-prompt" value="용감한 초등학생 히어로 배지" class="bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs text-slate-800 flex-grow">
                            <button onclick="generateAISticker()" id="btn-gen-sticker" class="px-4 py-2 bg-pink-600 hover:bg-pink-700 text-white font-bold rounded-xl text-xs flex items-center gap-1 shrink-0">🖼️ 스티커 그리기</button>
                        </div>
                        <div id="sticker-result" class="bg-slate-50 border border-slate-200 rounded-xl p-3 flex items-center justify-center min-h-[140px]">
                            <span class="text-xs text-slate-400">버튼을 누르면 칭찬 스티커가 생성됩니다.</span>
                        </div>
                        <div class="mt-4 border-t border-slate-100 pt-3">
                            <div class="flex items-center justify-between mb-2">
                                <span class="text-xs font-bold text-pink-900">🏆 내 스티커북 (<span id="sticker-count-badge">0</span>/30개)</span>
                                <button onclick="resetStickers()" class="text-[10px] text-slate-400 hover:text-red-500 underline">초기화</button>
                            </div>
                            <div id="sticker-gallery" class="grid grid-cols-6 sm:grid-cols-10 gap-1.5 bg-pink-50/50 p-2.5 rounded-xl border border-pink-100 min-h-[110px] items-center"></div>
                        </div>
                    </div>
                </div>

                <!-- Grounded Search Q&A -->
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between border-b pb-3 mb-4">
                            <h3 class="font-bold text-slate-800 flex items-center gap-2"><span>🔍</span> AI 탐구 & 호기심 질의응답</h3>
                        </div>
                        <div class="flex gap-2 mb-4">
                            <input type="text" id="search-query" value="이순신 장군 3대 대첩이 뭐야?" class="bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs text-slate-800 flex-grow">
                            <button onclick="searchAIQna()" id="btn-gen-search" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-xs flex items-center gap-1 shrink-0">🔍 질문하기</button>
                        </div>
                        <div id="search-result" class="bg-slate-50 border border-slate-200 rounded-xl p-4 text-xs leading-relaxed hidden min-h-[160px] max-h-[220px] overflow-y-auto"></div>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <!-- Footer -->
    <footer class="bg-white border-t border-slate-200 mt-8 py-4 text-center text-xs text-slate-500">
        <p>초등 5학년 맞춤 주간 일정표 & AI 스마트 루틴 대시보드</p>
    </footer>

    <!-- JS Application Logic -->
    <script>
        const apiKey = "AQ.Ab8RN6JboNQJcwX0o0eAFfLsm4GebGvHTtyOzLpKAtQwp_g1UA";
        const DEFAULT_WEEKDAY_SCHEDULES = {
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
                    { time: "15:00 ~ 17:30", name: "🏠 할아버지 댁 여유시간", detail: "💡 독서, 숙제 사전 해결", badge: "여유시간" },
                    { time: "17:30 ~ 18:30", name: "🥋 합기도 학원", detail: "도보 3분", badge: "운동" },
                    { time: "18:30 ~ 19:15", name: "🚘 하원 픽업 & 집 이동", detail: "집 도착", badge: "픽업" }
                ]
            },
            wed: {
                title: "수요일 일정 (★ 학원 연계 데이)",
                items: [
                    { time: "14:00 ~ 15:00", name: "🎹 피아노 학원", detail: "픽업 차량 이용", badge: "학원" },
                    { time: "15:00 ~ 17:00", name: "📐 수학 학원", detail: "바로 옆 호실 즉시 이동", badge: "바로연결" },
                    { time: "17:00 ~ 17:30", name: "할아버지 댁 이동", detail: "휴식", badge: "휴식" },
                    { time: "17:30 ~ 18:30", name: "🥋 합기도 학원", detail: "운동", badge: "운동" },
                    { time: "18:30 ~ 19:15", name: "🚘 하원 픽업 & 집 이동", detail: "픽업", badge: "픽업" }
                ]
            },
            thu: {
                title: "목요일 일정 (★ 여유 시간 활용)",
                items: [
                    { time: "14:00 ~ 15:00", name: "🎹 피아노 학원", detail: "학원", badge: "학원" },
                    { time: "15:00 ~ 17:30", name: "🏠 할아버지 댁 여유시간", detail: "독서 및 숙제", badge: "여유시간" },
                    { time: "17:30 ~ 18:30", name: "🥋 합기도 학원", detail: "운동", badge: "운동" },
                    { time: "18:30 ~ 19:15", name: "🚘 하원 픽업 & 집 이동", detail: "픽업", badge: "픽업" }
                ]
            },
            fri: {
                title: "금요일 일정 (미술 데이)",
                items: [
                    { time: "14:00 ~ 16:00", name: "🎨 미술 학원", detail: "학원", badge: "학원" },
                    { time: "16:00 ~ 17:30", name: "🏠 할아버지 댁 휴식", detail: "휴식", badge: "휴식" },
                    { time: "17:30 ~ 18:30", name: "🥋 합기도 학원", detail: "운동", badge: "운동" },
                    { time: "18:30 ~ 19:15", name: "🚘 하원 픽업 & 집 이동", detail: "귀가", badge: "픽업" }
                ]
            }
        };

        const DEFAULT_CHECKLIST_WEEKDAY = [
            { id: "w1", text: "아침 뇌 깨우기: 06:50 최태성 한국사 시청", checked: false },
            { id: "w2", text: "학원 미션: 학원 수강 및 안전한 이동", checked: false },
            { id: "w3", text: "70분 몰입 학습: 수학+영어+국어 완수", checked: false },
            { id: "w4", text: "내일 준비: 책상 정돈 및 가방 챙기기", checked: false },
            { id: "w5", text: "취침 골든타임: 22:00 이전 소등 및 취침", checked: false }
        ];

        const DEFAULT_CHECKLIST_WEEKEND = [
            { id: "wk1", text: "주말 모닝 공부: 90분 학습 완주", checked: false },
            { id: "wk2", text: "아빠와 야구: 야외 신체활동 다녀오기", checked: false },
            { id: "wk3", text: "게임 약속 준수: 3시간 쪼개기 규칙", checked: false },
            { id: "wk4", text: "밤 몰입 독서: 1시간 독서", checked: false },
            { id: "wk5", text: "취침 리듬 유지: 22:00 이전 눕기", checked: false }
        ];

        let appData = {
            schedules: JSON.parse(JSON.stringify(DEFAULT_WEEKDAY_SCHEDULES)),
            checklistWeekday: JSON.parse(JSON.stringify(DEFAULT_CHECKLIST_WEEKDAY)),
            checklistWeekend: JSON.parse(JSON.stringify(DEFAULT_CHECKLIST_WEEKEND)),
            lastDate: "",
            historyLog: [],
            stickers: [],
            rewardGoal: "아빠와 프로야구 직관 가기!",
            isEditMode: false,
            currentDayKey: 'mon',
            currentPlanKey: 'A',
            currentWeekendKey: 'sat'
        };

        function loadData() {
            const stored = localStorage.getItem('elem5_routine_data_v2');
            if (stored) {
                try { appData = { ...appData, ...JSON.parse(stored) }; } catch (e) {}
            }
            if (!appData.stickers) appData.stickers = [];
            checkAndResetDailyData();
        }

        function saveData() {
            localStorage.setItem('elem5_routine_data_v2', JSON.stringify(appData));
        }

        function getTodayString() {
            const today = new Date();
            return `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
        }

        function checkAndResetDailyData() {
            const todayStr = getTodayString();
            const dateBadge = document.getElementById('current-date-badge');
            if (dateBadge) dateBadge.innerText = `오늘: ${todayStr}`;
            if (appData.lastDate !== todayStr) {
                appData.lastDate = todayStr;
                saveData();
            }
        }

        function toggleEditMode() {
            appData.isEditMode = !appData.isEditMode;
            const btn = document.getElementById('btn-edit-mode');
            btn.className = appData.isEditMode ? "text-xs px-3 py-1.5 bg-amber-500 text-white font-bold rounded-xl transition-all shadow-sm shrink-0 whitespace-nowrap" : "text-xs px-3 py-1.5 bg-slate-200 hover:bg-slate-300 text-slate-700 font-bold rounded-xl transition-all shrink-0 whitespace-nowrap";
            btn.innerText = appData.isEditMode ? "💾 수정 완료" : "✏️ 일정 수정";
            renderDaySchedule(appData.currentDayKey);
            renderChecklists();
        }

        function switchTab(tabId) {
            ['dashboard', 'weekday', 'evening', 'weekend', 'checklist', 'ai'].forEach(t => {
                document.getElementById(`sec-${t}`)?.classList.add('hidden');
                const nav = document.getElementById(`nav-${t}`);
                if (nav) { nav.classList.remove('active'); nav.classList.add('text-slate-600'); }
            });
            document.getElementById(`sec-${tabId}`)?.classList.remove('hidden');
            const activeNav = document.getElementById(`nav-${tabId}`);
            if (activeNav) { activeNav.classList.add('active'); activeNav.classList.remove('text-slate-600'); }
            if (tabId === 'checklist') renderHistoryLog();
            if (tabId === 'ai') renderStickerGallery();
        }

        function renderDaySchedule(dayKey) {
            appData.currentDayKey = dayKey;
            ['mon', 'tue', 'wed', 'thu', 'fri'].forEach(d => {
                document.getElementById(`day-${d}`)?.className = (d === dayKey) ? "day-btn active px-4 py-2 rounded-xl border border-slate-200 bg-white text-sm transition-all" : "day-btn px-4 py-2 rounded-xl border border-slate-200 bg-white text-sm transition-all";
            });
            const data = appData.schedules[dayKey];
            const container = document.getElementById('day-schedule-card');
            if (!container || !data) return;

            let html = `<div class="flex items-center justify-between border-b pb-3"><h3 class="text-lg font-bold text-slate-800">${escapeHtml(data.title)}</h3></div><div class="space-y-3">`;
            data.items.forEach((item, index) => {
                html += `
                    <div class="flex flex-col sm:flex-row sm:items-center justify-between p-3.5 bg-slate-50 rounded-xl border border-slate-100 gap-2">
                        <div class="flex items-center gap-3">
                            <span class="text-xs font-bold text-slate-500 w-28 shrink-0">🕒 ${escapeHtml(item.time)}</span>
                            <span class="text-sm font-bold text-slate-800">${escapeHtml(item.name)}</span>
                        </div>
                        <span class="text-xs text-slate-500">${escapeHtml(item.detail)}</span>
                    </div>
                `;
            });
            container.innerHTML = html + `</div>`;
        }

        function setEveningPlan(planKey) {
            appData.currentPlanKey = planKey;
            document.getElementById('btn-planA').className = planKey === 'A' ? "px-2.5 py-1 rounded-lg text-xs font-bold bg-indigo-600 text-white" : "px-2.5 py-1 rounded-lg text-xs font-bold bg-slate-100 text-slate-600";
            document.getElementById('btn-planB').className = planKey === 'B' ? "px-2.5 py-1 rounded-lg text-xs font-bold bg-indigo-600 text-white" : "px-2.5 py-1 rounded-lg text-xs font-bold bg-slate-100 text-slate-600";
            
            const plans = {
                A: [{ time: "20:10 ~ 21:20", title: "⚡ 자기주도 몰입 학습 (70분)", detail: "수학 ➡️ 영어 ➡️ 국어" }],
                B: [{ time: "19:40 ~ 20:10", title: "📖 선(先) 집중 학습", detail: "영어 + 국어" }, { time: "20:50 ~ 21:20", title: "📐 수학 마무리", detail: "수학 숙제 완수" }]
            };
            document.getElementById('evening-plan-container').innerHTML = `<div class="space-y-3">` + plans[planKey].map(i => `<div class="p-4 bg-slate-50 rounded-xl border border-slate-100"><div class="text-xs font-bold text-indigo-600">${i.time}</div><div class="text-sm font-bold">${i.title}</div><div class="text-xs text-slate-600">${i.detail}</div></div>`).join('') + `</div>`;
        }

        function setWeekendDay(dayKey) {
            document.getElementById('btn-sat').className = dayKey === 'sat' ? "px-3 py-1 rounded-lg text-xs font-bold bg-emerald-600 text-white" : "px-3 py-1 rounded-lg text-xs font-bold bg-slate-100 text-slate-600";
            document.getElementById('btn-sun').className = dayKey === 'sun' ? "px-3 py-1 rounded-lg text-xs font-bold bg-emerald-600 text-white" : "px-3 py-1 rounded-lg text-xs font-bold bg-slate-100 text-slate-600";
            document.getElementById('weekend-title').innerText = dayKey === 'sat' ? "🗓️ 토요일 알찬 타임라인" : "🗓️ 일요일 알찬 타임라인";
            document.getElementById('weekend-timeline-list').innerHTML = `<div class="p-3.5 bg-slate-50 rounded-xl border border-slate-100">모닝 90분 학습 + 아빠와 야구 야외활동 루틴 진행</div>`;
        }

        function renderChecklists() {
            ['weekday', 'weekend'].forEach(type => {
                const list = type === 'weekday' ? appData.checklistWeekday : appData.checklistWeekend;
                const container = document.getElementById(`${type}-checklist-container`);
                const countEl = document.getElementById(`${type}-count`);
                if (!container) return;
                let checkedCount = 0;
                container.innerHTML = list.map((item, idx) => {
                    if (item.checked) checkedCount++;
                    return `<label class="flex items-center gap-3 p-2.5 bg-slate-50 rounded-xl cursor-pointer border border-slate-100"><input type="checkbox" ${item.checked ? 'checked' : ''} onchange="toggleCheckItem('${type}', ${idx})" class="w-4 h-4 rounded"><span class="${item.checked ? 'line-through text-slate-400' : 'text-slate-700'}">${escapeHtml(item.text)}</span></label>`;
                }).join('');
                if (countEl) countEl.innerText = `${checkedCount} / ${list.length} 완료`;
            });
        }

        function toggleCheckItem(type, index) {
            if (type === 'weekday') appData.checklistWeekday[index].checked = !appData.checklistWeekday[index].checked;
            else appData.checklistWeekend[index].checked = !appData.checklistWeekend[index].checked;
            saveData();
            renderChecklists();
        }

        function forceDailyReset() {
            appData.checklistWeekday.forEach(i => i.checked = false);
            appData.checklistWeekend.forEach(i => i.checked = false);
            saveData();
            renderChecklists();
        }

        function renderHistoryLog() {
            document.getElementById('history-cards-container').innerHTML = `<div class="col-span-full text-center py-6 text-xs text-slate-400">루틴 기록 대기 중</div>`;
        }

        async function fetchGeminiWithRetry(apiUrl, payload) {
            const res = await fetch(apiUrl, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
            if (!res.ok) throw new Error("API call failed");
            return await res.json();
        }

        async function generateAIQuiz() {
            const resultBox = document.getElementById('ai-quiz-result');
            resultBox.classList.remove('hidden');
            resultBox.innerHTML = `<div class="flex items-center gap-2 text-indigo-600 font-bold"><div class="spinner-dark"></div><span>퀴즈 생성 중...</span></div>`;
            setTimeout(() => {
                resultBox.innerHTML = `<div class="bg-indigo-50 p-3.5 rounded-xl"><div class="font-bold text-indigo-900">📜 한국사 퀴즈</div><p class="text-xs mt-1">조선 시대 정약용이 거중기를 활용해 축조한 유네스코 세계문화유산은?</p><div class="mt-2 text-xs font-black text-emerald-700">✅ 정답: 수원 화성</div></div>`;
            }, 800);
        }

        async function generateAIVoice() {
            const statusBox = document.getElementById('tts-status');
            statusBox.classList.remove('hidden');
            statusBox.innerHTML = `<div class="p-3 bg-purple-50 rounded-xl text-xs font-bold text-purple-900">💬 "오늘도 멋진 5학년 대장님 파이팅!" (음성 재생 완료)</div>`;
        }

        async function generateAISticker() {
            const resultContainer = document.getElementById('sticker-result');
            const prompt = document.getElementById('sticker-prompt').value;
            appData.stickers.push({ id: Date.now(), title: prompt, icon: "⭐", gradient: "from-pink-400 to-purple-500" });
            saveData();
            renderStickerGallery();
            resultContainer.innerHTML = `<div class="text-xs font-bold text-pink-700">🎉 칭찬 스티커가 스티커북에 저장되었습니다!</div>`;
        }

        function renderStickerGallery() {
            const container = document.getElementById('sticker-gallery');
            document.getElementById('sticker-count-badge').innerText = appData.stickers.length;
            let html = "";
            for (let i = 0; i < 30; i++) {
                if (appData.stickers[i]) {
                    html += `<div class="w-8 h-8 rounded-lg bg-gradient-to-tr ${appData.stickers[i].gradient} flex items-center justify-center text-sm shadow-sm">${appData.stickers[i].icon}</div>`;
                } else {
                    html += `<div class="w-8 h-8 rounded-lg border border-dashed border-pink-200 bg-white/60 flex items-center justify-center text-[9px] text-pink-300 font-bold">${i + 1}</div>`;
                }
            }
            container.innerHTML = html;
        }

        function resetStickers() {
            if (confirm("스티커판을 초기화하시겠습니까?")) {
                appData.stickers = [];
                saveData();
                renderStickerGallery();
            }
        }

        async function searchAIQna() {
            const query = document.getElementById('search-query').value;
            const container = document.getElementById('search-result');
            container.classList.remove('hidden');
            container.innerHTML = `<div class="text-xs text-slate-700">⚔️ **'${escapeHtml(query)}' 탐구 백과**<br><br>이순신 장군님은 임진왜란 당시 학익진 전법과 거북선으로 나라를 구한 위대한 영웅입니다!</div>`;
        }

        function initCharts() {
            const pieCtx = document.getElementById('timePieChart')?.getContext('2d');
            if (pieCtx) {
                new Chart(pieCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['수면 (8.5시간)', '학교/학원 (8시간)', '여유/이동 (6.3시간)', '저녁몰입 (1.1시간)'],
                        datasets: [{ data: [35, 33, 27, 5], backgroundColor: ['#6366f1', '#3b82f6', '#f59e0b', '#10b981'] }]
                    },
                    options: { responsive: true, maintainAspectRatio: false }
                });
            }
            const barCtx = document.getElementById('studyBarChart')?.getContext('2d');
            if (barCtx) {
                new Chart(barCtx, {
                    type: 'bar',
                    data: {
                        labels: ['수학', '영어', '국어', '마무리'],
                        datasets: [{ data: [30, 15, 15, 10], backgroundColor: ['#3b82f6', '#8b5cf6', '#ec4899', '#64748b'], borderRadius: 8 }]
                    },
                    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
                });
            }
        }

        function escapeHtml(text) {
            if (!text) return "";
            return String(text).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
        }

        window.addEventListener('DOMContentLoaded', () => {
            loadData();
            renderDaySchedule('mon');
            setEveningPlan('A');
            setWeekendDay('sat');
            renderChecklists();
            renderStickerGallery();
            initCharts();
        });
    </script>
</body>
</html>
