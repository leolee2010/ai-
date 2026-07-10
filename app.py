import streamlit as st
import random
import time
import os
import matplotlib.pyplot as plt

# --- 데이터 저장 파일 설정 ---
DATA_FILE = "dot_experiment_results.txt"

# --- 실험 설정 ---
total_rounds = 10
# AI가 틀린 정보를 제공할 라운드 (6라운드부터 조금씩 틀리기 시작)
ai_error_rounds = {
    6: 2,   # 실제보다 +2 혹은 -2 오차
    7: -3,  # 실제보다 -3 오차
    8: 4,   # 실제보다 +4 오차
    9: -5,  # 실제보다 -5 오차
    10: 6   # 실제보다 +6 오차
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
    user_name = st.text_input("이름 또는 참가자 ID:")
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
    st.write(f"### 📋 라ust 라운드 {r} / {total_rounds}")
    
    # 라운드별 빨간 점 이미지 생성 (최초 1회만 고정 생성)
    if f'round_{r}_dots' not in st.session_state.round_data:
        num_dots = random.randint(50, 80)
        # 0~1 사이의 무작위 좌표 생성
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

    # 흑백(검은 화면에 빨간 점) 그래프 그리기
    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    ax.scatter(dots_x, dots_y, color='red', s=30) # s는 점의 크기
    ax.axis('off') # 축 숨기기
    st.pyplot(fig)
    plt.close()

    # 정답 입력받기
    user_answer = st.number_input("화면에 보이는 빨간 점은 총 몇 개입니까?", min_value=0, step=1, key=f"ans_{r}")
    
    if st.button("정답 제출 및 다음 단계"):
        time_taken = time.time() - st.session_state.start_time
        error_value = user_answer - actual_dots # 양수면 더 많이 셈, 음수면 더 적게 셈
        
        st.session_state.user_results.append({
            'round': r,
            'user_ans': user_answer,
            'actual': actual_dots,
            'error': error_value,
            'time': round(time_taken, 2)
        })
        st.session_state.round += 1
        st.rerun()

# 3단계: 종료 및 데이터 누적
else:
    st.success("🎉 모든 테스트가 완료되었습니다. 수고하셨습니다!")
    
    # 파일에 결과 누적 저장
    if 'saved' not in st.session_state:
        with open(DATA_FILE, "a", encoding="utf-8") as f:
            for res in st.session_state.user_results:
                # 데이터 형식: 이름,그룹,라운드,유저답,실제답,오차(차이),소요시간
                line = f"{st.session_state.user_name},{st.session_state.group},{res['round']},{res['user_ans']},{res['actual']},{res['error']},{res['time']}\n"
                f.write(line)
        st.session_state.saved = True

    st.write("### 📊 나의 실험 요약")
    for res in st.session_state.user_results:
        st.write(f"- **{res['round']}라운드**: 실제 {res['actual']}개 | 제출 {res['user_ans']}개 (오차: **{res['error']}**) | {res['time']}초")

    st.write("---")
    # ⚙️ 연구자(우리 팀) 전용 데이터 뷰어
    if st.checkbox("⚙️ [연구자 전용] 전체 참가자 누적 데이터 확인"):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                st.text_area("누적 데이터 (이름, 그룹, 라운드, 유저답, 실제정답, 오차, 시간)", f.read(), height=250)
        else:
            st.write("아직 쌓인 데이터가 없습니다.")

    if st.button("새로운 참여자로 시작하기"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
