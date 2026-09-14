import streamlit as st

# 1. 페이지 기본 설정 (브라우저 탭 이름 등)
st.set_page_config(
    page_title="내 개인 홈페이지",
    page_icon="💻",
    layout="centered",
)

# 2. 사이드바 메뉴 (페이지 이동 역할)
st.sidebar.title("메뉴")
menu = st.sidebar.selectbox(
    "이동할 페이지", ["홈 (Home)", "AI 검색 비서", "내 소개 & 기록"]
)

# 3. 메뉴별 화면 구성
if menu == "홈 (Home)":
  st.title("환영합니다! 👋")
  st.write("제가 직접 만든 저만의 개인 홈페이지입니다.")
  st.info("좌측 메뉴에서 다른 페이지로 이동해 보세요.")

elif menu == "AI 검색 비서":
  st.title("🤖 AI 검색 선생님")
  st.write("초등학교 5학년 눈높이에 맞춰 궁금한 걸 요약해 주는 공간입니다.")

  user_question = st.text_input("궁금한 점을 입력하세요:")
  if st.button("검색 및 정리"):
    if user_question:
      # 여기에 아까 그 Gemini AI 연동 코드가 들어가면 됩니다!
      st.success(f"'{user_question}'에 대한 답변입니다 (준비 중)")
    else:
      st.warning("내용을 입력해주세요.")

elif menu == "내 소개 & 기록":
  st.title("📝 프로필 & 기록")
  st.write("제가 만든 프로그램들과 소소한 일상을 기록하는 공간입니다.")
  st.text_area("메모장 공간", "여기에 자유롭게 글을 남길 수 있습니다.")