import streamlit as st

# Streamlit 페이지 기본 설정
st.set_page_config(
    page_title="초등 5학년 주간 일정표 & AI 대시보드",
    page_icon="📅",
    layout="wide",
)

# 전체 대시보드 HTML/CSS/JS 코드를 Streamlit 컴포넌트에 안전하게 임베드
st.components.v1.html(
    """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>초등 5학년 주간 일정표 & AI 스마트 루틴 대시보드</title>
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

            <!-- Navigation Tabs -->
            <div class="flex items-center gap-2 flex-wrap shrink-0">
                <nav class="flex flex-wrap gap-1 bg-slate-100 p-1 rounded-xl text-xs font-medium">
                    <button onclick="switchTab('dashboard')" id="nav-dashboard" class="tab-btn active px-2.5 py-1.5 rounded-lg transition-all whitespace-nowrap">📊 대시보드</button>
                    <button onclick="switchTab('weekday')" id="nav-weekday" class="tab-btn px-2.5 py-1.5 rounded-lg text-slate-600 hover:bg-white transition-all whitespace-nowrap">🎒 요일별 학원</button>
                    <button onclick="switchTab('evening')" id="nav-evening" class="tab-btn px-2.5 py-1.5 rounded-lg text-slate-600 hover:bg-white transition-all whitespace-nowrap">🌙 저녁 루틴</button>
                    <button onclick="switchTab('weekend')" id="nav-weekend" class="tab-btn px-2.5 py-1.5 rounded-lg text-slate-600 hover:bg-white transition-all whitespace-nowrap">☀️ 주말 일과</button>
                    <button onclick="switchTab('checklist')" id="nav-checklist" class="tab-btn px-2.5 py-1.5 rounded-lg text-slate-600 hover:bg-white transition-all whitespace-nowrap">✅ 체크 & 기록</button>
                    <button onclick="switchTab('ai')" id="nav-ai" class="tab-btn px-2.5 py-1.5 rounded-lg text-slate-600 hover:bg-white transition-all whitespace-nowrap">✨ AI 코치 & 퀴즈</button>
                </nav>
            </div>
        </div>
    </header>

    <!-- Main Content Area -->
    <main class="max-w-6xl mx-auto px-4 py-6 flex-grow w-full">

        <!-- TAB 1: DASHBOARD OVERVIEW -->
        <section id="sec-dashboard" class="space-y-6">
            <div class="bg-blue-50 border border-blue-200 rounded-2xl p-4 text-blue-900 text-sm leading-relaxed flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                <div>
                    💡 <strong>맞춤형 스마트 루틴 대시보드:</strong> 학원 동선, 70분 저녁 집중 학습, 주말 야외활동 및 독서 루틴이 통합 저장됩니다.
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
                </div>
                <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
                    <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">평일 저녁 집중 학습</span>
                    <div class="mt-2 flex items-baseline justify-between">
                        <span class="text-2xl font-black text-blue-600">70분</span>
                        <span class="text-xs text-slate-500">20:10~21:20</span>
                    </div>
                </div>
                <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
                    <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">주말 야외/신체 활동</span>
                    <div class="mt-2 flex items-baseline justify-between">
                        <span class="text-2xl font-black text-amber-600">2.5시간</span>
                        <span class="text-xs text-slate-500">오후 13:00~</span>
                    </div>
                </div>
                <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
                    <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">주말 게임 시간 관리</span>
                    <div class="mt-2 flex items-baseline justify-between">
                        <span class="text-2xl font-black text-emerald-600">3시간</span>
                        <span class="text-xs text-slate-500">1.5h × 2회</span>
                    </div>
                </div>
            </div>

            <!-- Charts Section -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
                    <h3 class="text-base font-bold text-slate-800 mb-1">📊 평일 하루 시간 배분 비율</h3>
                    <div class="chart-container">
                        <canvas id="timePieChart"></canvas>
                    </div>
                </div>
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
                    <h3 class="text-base font-bold text-slate-800 mb-1">🎯 저녁 70분 몰입 학습 과목 구성</h3>
                    <div class="chart-container">
                        <canvas id="studyBarChart"></canvas>
                    </div>
                </div>
            </div>
        </section>

        <!-- TAB 2: WEEKDAY ACADEMIES & ROUTES -->
        <section id="sec-weekday" class="hidden space-y-6">
            <div class="bg-amber-50 border border-amber-200 rounded-2xl p-4 text-amber-900 text-sm">
                🎒 <strong>방과 후 학원 동선:</strong> 합기도는 매일 17:30(도보 3분), 수요일은 피아노와 수학이 연속 수강됩니다.
            </div>
            <div class="flex flex-wrap gap-2">
                <button onclick="renderDaySchedule('mon')" id="day-mon" class="day-btn active px-4 py-2 rounded-xl border border-slate-200 bg-white text-sm">월요일</button>
                <button onclick="renderDaySchedule('tue')" id="day-tue" class="day-btn px-4 py-2 rounded-xl border border-slate-200 bg-white text-sm">화요일</button>
                <button onclick="renderDaySchedule('wed')" id="day-wed" class="day-btn px-4 py-2 rounded-xl border border-slate-200 bg-white text-sm">수요일</button>
                <button onclick="renderDaySchedule('thu')" id="day-thu" class="day-btn px-4 py-2 rounded-xl border border-slate-200 bg-white text-sm">목요일</button>
                <button onclick="renderDaySchedule('fri')" id="day-fri" class="day-btn px-4 py-2 rounded-xl border border-slate-200 bg-white text-sm">금요일</button>
            </div>
            <div id="day-schedule-card" class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4"></div>
        </section>

        <!-- TAB 3: EVENING ROUTINE -->
        <section id="sec-evening" class="hidden space-y-6">
            <div class="bg-indigo-50 border border-indigo-200 rounded-2xl p-4 text-indigo-900 text-sm flex justify-between items-center">
                <div>🌙 <strong>저녁 루틴 모드:</strong> Plan A와 Plan B를 선택하세요.</div>
                <div class="flex gap-2">
                    <button onclick="setEveningPlan('A')" id="btn-planA" class="px-3 py-1 rounded-lg text-xs font-bold bg-indigo-600 text-white">Plan A</button>
                    <button onclick="setEveningPlan('B')" id="btn-planB" class="px-3 py-1 rounded-lg text-xs font-bold bg-slate-100 text-slate-600">Plan B</button>
                </div>
            </div>
            <div id="evening-plan-container" class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4"></div>
        </section>

        <!-- TAB 4: WEEKEND SCHEDULE -->
        <section id="sec-weekend" class="hidden space-y-6">
            <div class="bg-emerald-50 border border-emerald-200 rounded-2xl p-4 text-emerald-900 text-sm flex justify-between items-center">
                <div>☀️ <strong>주말 원칙:</strong> 모닝 90분 공부 완주, 야구, 게임 쪼개기!</div>
                <div class="flex gap-2">
                    <button onclick="setWeekendDay('sat')" id="btn-sat" class="px-3 py-1 rounded-lg text-xs font-bold bg-emerald-600 text-white">토요일</button>
                    <button onclick="setWeekendDay('sun')" id="btn-sun" class="px-3 py-1 rounded-lg text-xs font-bold bg-slate-100 text-slate-600">일요일</button>
                </div>
            </div>
            <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
                <h3 id="weekend-title" class="text-lg font-bold text-slate-800">🗓️ 주말 타임라인</h3>
                <div id="weekend-timeline-list" class="space-y-3"></div>
            </div>
        </section>

        <!-- TAB 5: CHECKLIST -->
        <section id="sec-checklist" class="hidden space-y-6">
            <div class="bg-purple-50 border border-purple-200 rounded-2xl p-4 text-purple-900 text-sm flex justify-between items-center">
                <div>✅ <strong>일일 루틴 체크리스트:</strong> 매일 미션을 달성해 보세요!</div>
                <button onclick="forceDailyReset()" class="px-3 py-1.5 bg-purple-600 text-white text-xs font-bold rounded-xl">초기화</button>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
                    <h3 class="font-bold text-slate-800">📅 평일 필수 미션</h3>
                    <div id="weekday-checklist-container" class="space-y-2 text-xs"></div>
                </div>
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
                    <h3 class="font-bold text-slate-800">☀️ 주말 필수 미션</h3>
                    <div id="weekend-checklist-container" class="space-y-2 text-xs"></div>
                </div>
            </div>
        </section>

        <!-- TAB 6: AI COACH -->
        <section id="sec-ai" class="hidden space-y-6">
            <div class="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-6 text-white shadow-md">
                <h2 class="text-2xl font-black">✨ 초등 5학년 Gemini AI 스마트 학습 코치</h2>
                <p class="text-xs text-indigo-100 mt-1">퀴즈, 칭찬 스티커, 탐구 질의응답을 즐겨보세요!</p>
            </div>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
                    <h3 class="font-bold text-slate-800 mb-3">🧠 1분 AI 퀴즈</h3>
                    <button onclick="generateAIQuiz()" class="px-4 py-2 bg-indigo-600 text-white font-bold rounded-xl text-xs">퀴즈 생성하기</button>
                    <div id="ai-quiz-result" class="mt-3 bg-slate-50 p-4 rounded-xl text-xs hidden"></div>
                </div>
                <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
                    <h3 class="font-bold text-slate-800 mb-3">🎨 AI 칭찬 스티커북</h3>
                    <button onclick="generateAISticker()" class="px-4 py-2 bg-pink-600 text-white font-bold rounded-xl text-xs">스티커 획득하기</button>
                    <div id="sticker-gallery" class="grid grid-cols-6 gap-1.5 mt-3 bg-pink-50 p-2.5 rounded-xl"></div>
                </div>
            </div>
        </section>
    </main>

    <script>
        function switchTab(tabId) {
            ['dashboard', 'weekday', 'evening', 'weekend', 'checklist', 'ai'].forEach(t => {
                document.getElementById(`sec-${t}`)?.classList.add('hidden');
                document.getElementById(`nav-${t}`)?.classList.remove('active');
            });
            document.getElementById(`sec-${tabId}`)?.classList.remove('hidden');
            document.getElementById(`nav-${tabId}`)?.classList.add('active');
            if (tabId === 'ai') renderStickerGallery();
        }

        const schedules = {
            mon: [{time: "15:00", name: "수학학원"}, {time: "17:30", name: "합기도"}],
            tue: [{time: "14:00", name: "피아노학원"}, {time: "17:30", name: "합기도"}],
            wed: [{time: "14:00", name: "피아노학원"}, {time: "15:00", name: "수학학원"}, {time: "17:30", name: "합기도"}],
            thu: [{time: "14:00", name: "피아노학원"}, {time: "17:30", name: "합기도"}],
            fri: [{time: "14:00", name: "미술학원"}, {time: "17:30", name: "합기도"}]
        };

        function renderDaySchedule(dayKey) {
            ['mon', 'tue', 'wed', 'thu', 'fri'].forEach(d => {
                document.getElementById(`day-${d}`)?.className = (d === dayKey) ? "day-btn active px-4 py-2 rounded-xl border border-slate-200 bg-white text-sm" : "day-btn px-4 py-2 rounded-xl border border-slate-200 bg-white text-sm";
            });
            const items = schedules[dayKey] || [];
            document.getElementById('day-schedule-card').innerHTML = items.map(i => `<div class="p-3 bg-slate-50 rounded-xl">🕒 ${i.time} - ${i.name}</div>`).join('');
        }

        function setEveningPlan(plan) {
            document.getElementById('btn-planA').className = plan === 'A' ? "px-3 py-1 rounded-lg text-xs font-bold bg-indigo-600 text-white" : "px-3 py-1 rounded-lg text-xs font-bold bg-slate-100 text-slate-600";
            document.getElementById('btn-planB').className = plan === 'B' ? "px-3 py-1 rounded-lg text-xs font-bold bg-indigo-600 text-white" : "px-3 py-1 rounded-lg text-xs font-bold bg-slate-100 text-slate-600";
            document.getElementById('evening-plan-container').innerHTML = plan === 'A' ? "<div>Plan A: 20:10~21:20 저녁 몰입 학습 (70분)</div>" : "<div>Plan B: 유연한 저녁 학습 스케줄</div>";
        }

        function setWeekendDay(day) {
            document.getElementById('btn-sat').className = day === 'sat' ? "px-3 py-1 rounded-lg text-xs font-bold bg-emerald-600 text-white" : "px-3 py-1 rounded-lg text-xs font-bold bg-slate-100 text-slate-600";
            document.getElementById('btn-sun').className = day === 'sun' ? "px-3 py-1 rounded-lg text-xs font-bold bg-emerald-600 text-white" : "px-3 py-1 rounded-lg text-xs font-bold bg-slate-100 text-slate-600";
            document.getElementById('weekend-title').innerText = day === 'sat' ? "🗓️ 토요일 알찬 타임라인" : "🗓️ 일요일 알찬 타임라인 (예배 포함)";
            document.getElementById('weekend-timeline-list').innerHTML = `<div class="p-3 bg-slate-50 rounded-xl">모닝 공부 90분 + 아빠와 야구 야외활동 루틴</div>`;
        }

        let checklists = {
            weekday: [{text: "아침 한국사 시청", checked: false}, {text: "저녁 70분 공부 완수", checked: false}, {text: "취침 22시 이전", checked: false}],
            weekend: [{text: "주말 모닝 공부", checked: false}, {text: "아빠와 야구 야외활동", checked: false}]
        };

        function renderChecklists() {
            ['weekday', 'weekend'].forEach(type => {
                const container = document.getElementById(`${type}-checklist-container`);
                if (!container) return;
                container.innerHTML = checklists[type].map((item, idx) => `
                    <label class="flex items-center gap-2 p-2 bg-slate-50 rounded-lg cursor-pointer">
                        <input type="checkbox" ${item.checked ? 'checked' : ''} onchange="checklists['${type}'][${idx}].checked = !checklists['${type}'][${idx}].checked; renderChecklists();">
                        <span class="${item.checked ? 'line-through text-slate-400' : 'text-slate-700'}">${item.text}</span>
                    </label>
                `).join('');
            });
        }

        function forceDailyReset() {
            checklists.weekday.forEach(i => i.checked = false);
            checklists.weekend.forEach(i => i.checked = false);
            renderChecklists();
        }

        let stickers = [];
        function generateAISticker() {
            stickers.push({icon: "⭐"});
            renderStickerGallery();
        }

        function renderStickerGallery() {
            const container = document.getElementById('sticker-gallery');
            if (!container) return;
            let html = "";
            for (let i = 0; i < 30; i++) {
                html += `<div class="w-8 h-8 rounded-lg bg-pink-200 flex items-center justify-center text-sm">${stickers[i] ? stickers[i].icon : i + 1}</div>`;
            }
            container.innerHTML = html;
        }

        function generateAIQuiz() {
            const box = document.getElementById('ai-quiz-result');
            box.classList.remove('hidden');
            box.innerHTML = "📜 <b>한국사 퀴즈:</b> 조선 시대 정약용이 거중기를 활용해 축조한 유네스코 세계문화유산은?<br><span class='text-emerald-600 font-bold'>정답: 수원 화성</span>";
        }

        window.addEventListener('DOMContentLoaded', () => {
            renderDaySchedule('mon');
            setEveningPlan('A');
            setWeekendDay('sat');
            renderChecklists();
            renderStickerGallery();
            
            // Charts
            new Chart(document.getElementById('timePieChart')?.getContext('2d'), {
                type: 'doughnut',
                data: { labels: ['수면', '학교/학원', '여유/이동', '저녁몰입'], datasets: [{ data: [35, 33, 27, 5], backgroundColor: ['#6366f1', '#3b82f6', '#f59e0b', '#10b981'] }] },
                options: { responsive: true, maintainAspectRatio: false }
            });
            new Chart(document.getElementById('studyBarChart')?.getContext('2d'), {
                type: 'bar',
                data: { labels: ['수학', '영어', '국어', '마무리'], datasets: [{ data: [30, 15, 15, 10], backgroundColor: ['#3b82f6', '#8b5cf6', '#ec4899', '#64748b'], borderRadius: 8 }] },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
            });
        });
    </script>
</body>
</html>
    """,
    height=900,
    scrolling=True,
)
