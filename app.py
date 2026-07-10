import streamlit as st
import random
import time
import os
import matplotlib.pyplot as plt

# --- 데이터 저장 파일 설정 ---
DATA_FILE = "dot_experiment_results.txt"

# --- 실험 설정 (10단계) ---
total_rounds = 10
# 6라운드부터 AI가 고의로 오답 가이드를 제공 (실제 개수 대비 오차)
ai_error_rounds = {
    6: 2,   # 실제 정답보다 +2개 높여서 말함
    7: -3,  # 실제 정답보다 -3개 낮춰서 말함
    8: 4,   # 실제 정답보다 +4개 높여서 말함
    9: -5,  # 실제 정답보다 -5개 낮춰서 말함
    10: 6   # 실제 정답보다 +6개 높여서 말함
}

# --- 세션 상태 초기화 ---
if 'exp_started' not in st.session_state:
    st.session_state.exp_started = False
if 'round' not in st.session_state:
    st.session_state.round = 1
if 'group' not in st.session_state:
    st.session_state.group = None
if 'user_results' not in st.session_state:
    st.session_state.user_results = []
if 'round_data' not in st.session_state:
    st.session_state.round_data = {}
if 'start_time' not in st.session_state:
    st.session_state.start_time = 0

st.title("🔴 시각 인지 및 AI 협업 능력 테스트")
st.caption("화면에 나타나는 점의 개수를 신속하고 정확하게 파악하는 실험입니다.")

# 1단계: 사용자 정보 입력 및 조 배정
if not st.session_state.exp_started:
    st.subheader("참여자 정보 입력")
    user_name = st.text_input("학번과 이름을 입력하세요 (예: 10130 홍길동):")
    selected_group = st.radio("할당받은 그룹을 선택하세요:", ("A 그룹 (일반)", "B 그룹 (AI 보조)"))
    
    if st.button("실험 시작하기"):
        if user_name:
            st.session_state.user_name = user_name
            st.session_state.group = 'A' if "A 그룹" in selected_group else 'B'
            st.session_state.exp_started = True
            st.session_state.round = 1
            st.rerun()
        else:
            st.error("이름을 입력해주세요!")

# 2단계: 실험 진행 화면
elif st.session_state.round <= total_rounds:
    r = st.session_state.round
    st.write(f"### 📋 라운드 {r} / {total_rounds}")
    
    # 라운드별 빨간 점 무작위 좌표 생성 (라운드 진입 시 최초 1회만 고정)
    if f'round_{r}_dots' not in st.session_state.round_data:
        num_dots = random.randint(50, 80)
        x = [random.random() for _ in range(num_dots)]
        y = [random.random() for _ in range(num_dots)]
        
        st.session_state.round_data[f'round_{r}_dots'] = num_dots
        st.session_state.round_data[f'round_{r}_x'] = x
        st.session_state.round_data[f'round_{r}_y'] = y
        st.session_state.start_time = time.time()

    actual_dots = st.session_state.round_data[f'round_{r}_dots']
    dots_x = st.session_state.round_data[f'round_{r}_x']
    dots_y = st.session_state.round_data[f'round_{r}_y']

    # B그룹에게만 AI 예측치 제공 (후반부로 갈수록 틀림)
    if st.session_state.group == 'B':
        if r in ai_error_rounds:
            ai_pred = actual_dots + ai_error_rounds[r]
            st.error(f"💡 [AI 가이드]: 해당 화면의 빨간 점은 약 **{ai_pred}개**로 예측됩니다.")
        else:
            st.success(f"💡 [AI 가이드]: 해당 화면의 빨간 점은 약 **{actual_dots}개**로 예측됩니다.")

    # 검은 배경에 빨간 점 그래프 생성 (안정성 강화 버전)
    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    ax.scatter(dots_x, dots_y, color='red', s=40) 
    ax.axis('off') 
    
    # 웹 화면에 플롯 띄우기
    st.pyplot(fig)
    plt.close(fig) # 메모리 해제

    # 정답 입력받기
    user_answer = st.number_input("화면에 보이는 빨간 점은 총 몇 개입니까?", min_value=0, step=1, key=f"ans_{r}")
    
    if st.button("정답 제출 및 다음 단계"):
        time_taken = time.time() - st.session_state.start_time
        error_value = user_answer - actual_dots # 오차 계산 (양수: 과다측정, 음수: 과소측정)
        
        st.session_state.user_results.append({
            'round': r,
            'user_ans': user_answer,
            'actual': actual_dots,
            'error': error_value,
            'time': round(time_taken, 2)
        })
        st.session_state.round += 1
        st.rerun()

# 3단계: 종료 및 연구자 데이터 확인
else:
    st.success("🎉 모든 테스트가 완료되었습니다. 수고하셨습니다!")
    
    # 데이터 파일 누적 저장
    if 'saved' not in st.session_state:
        with open(DATA_FILE, "a", encoding="utf-8") as f:
            for res in st.session_state.user_results:
                line = f"{st.session_state.user_name},{st.session_state.group},{res['round']},{res['user_ans']},{res['actual']},{res['error']},{res['time']}\n"
                f.write(line)
        st.session_state.saved = True

    st.write("### 📊 나의 결과 요약")
    for res in st.session_state.user_results:
        st.write(f"- **{res['round']}라운드**: 실제 {res['actual']}개 | 제출 {res['user_ans']}개 (나의 오차: **{res['error']}**) | {res['time']}초 소요")

    st.write("---")
    # 연구자(우리 팀) 전용 데이터 수합 뷰어
    if st.checkbox("⚙️ [연구자 전용] 전체 참가자 데이터 확인"):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                st.text_area("누적 데이터 (이름, 그룹, 라운드, 제출답, 실제정답, 오차, 시간)", f.read(), height=250)
        else:
            st.write("아직 저장된 데이터가 없습니다.")

    if st.button("새로운 참여자로 다시 시작"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
