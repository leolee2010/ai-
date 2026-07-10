import streamlit as st
import random
import time
import os
import matplotlib.pyplot as plt
import math

# --- 데이터 저장 파일 설정 ---
DATA_FILE = "dot_experiment_results.txt"

# --- 실험 설정 (10단계) ---
total_rounds = 10
ai_error_rounds = {
    6: 1,   # 실제 정답보다 +1
    7: -2,  # 실제 정답보다 -2
    8: 2,   # 실제 정답보다 +2
    9: -3,  # 실제 정답보다 -3
    10: 3   # 실제 정답보다 +3
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
    user_name = st.text_input("학번과 이름을 입력하세요 (예: 202612345 홍길동):")
    selected_group = st.radio("할당받은 그룹을 선택하세요:", ("A 그룹 (일반)", "B 그룹 (AI 보조)"))
    
    if st.button("실험 시작하기"):
        if user_name:
            st.session_state.user_name = user_name
            st.session_state.group = 'A' if "A 그룹" in selected_group else 'B'
            st.session_state.exp_started = True
            st.session_state.round = 1
            st.rerun()
        else:
            st.error("학번과 이름을 입력해주세요!")

# 2단계: 실험 진행 화면
elif st.session_state.round <= total_rounds:
    r = st.session_state.round
    st.write(f"### 📋 라운드 {r} / {total_rounds}")
    
    # 점 개수 생성 및 겹침 방지 배치 알고리즘
    if f'round_{r}_dots' not in st.session_state.round_data:
        num_dots = random.randint(15, 30)
        x_list = []
        y_list = []
        
        min_distance = 0.08 # 점들 사이의 최소 거리 설정
        
        while len(x_list) < num_dots:
            potential_x = random.uniform(0.05, 0.95)
            potential_y = random.uniform(0.05, 0.95)
            
            is_too_close = False
            for ex, ey in zip(x_list, y_list):
                dist = math.sqrt((potential_x - ex)**2 + (potential_y - ey)**2)
                if dist < min_distance:
                    is_too_close = True
                    break
            
            if not is_too_close:
                x_list.append(potential_x)
                y_list.append(potential_y)
                
        st.session_state.round_data[f'round_{r}_dots'] = num_dots
        st.session_state.round_data[f'round_{r}_x'] = x_list
        st.session_state.round_data[f'round_{r}_y'] = y_list
        st.session_state.start_time = time.time()

    actual_dots = st.session_state.round_data[f'round_{r}_dots']
    dots_x = st.session_state.round_data[f'round_{r}_x']
    dots_y = st.session_state.round_data[f'round_{r}_y']

    # B그룹 가이드 메시지 (차별 없는 무색/회색 톤 박스로 수정)
    if st.session_state.group == 'B':
        if r in ai_error_rounds:
            ai_pred = actual_dots + ai_error_rounds[r]
            st.info(f"💡 [AI 가이드]: 해당 화면의 빨간 점은 약 **{ai_pred}개**로 예측됩니다.")
        else:
            st.info(f"💡 [AI 가이드]: 해당 화면의 빨간 점은 약 **{actual_dots}개**로 예측됩니다.")

    # 그래프 그리기
    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    
    # 윤곽선 효과 추가된 점 생성
    ax.scatter(dots_x, dots_y, color='red', s=80, edgecolor='white', linewidth=1.2)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off') 
    
    st.pyplot(fig)
    plt.close(fig)

    # 정답 입력받기
    user_answer = st.number_input("화면에 보이는 빨간 점은 총 몇 개입니까?", min_value=0, step=1, key=f"ans_{r}")
    
    if st.button("정답 제출 및 다음 단계"):
        time_taken = time.time() - st.session_state.start_time
        error_value = user_answer - actual_dots
        
        st.session_state.user_results.append({
            'round': r,
            'user_ans': user_answer,
            'actual': actual_dots,
            'error': error_value,
            'time': round(time_taken, 2)
        })
        st.session_state.round += 1
        st.rerun()

# 3단계: 종료 및 데이터 확인
else:
    st.success("🎉 모든 테스트가 완료되었습니다. 수고하셨습니다!")
    
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
    if st.checkbox("⚙️ [연구자 전용] 전체 참가자 데이터 확인"):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                st.text_area("누적 데이터 (학번 이름, 그룹, 라운드, 제출답, 실제정답, 오차, 시간)", f.read(), height=250)
        else:
            st.write("아직 저장된 데이터가 없습니다.")

    if st.button("새로운 참여자로 다시 시작"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
