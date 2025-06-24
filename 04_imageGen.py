import streamlit as st
from openai import OpenAI

# --- 페이지 설정 ---
st.set_page_config(page_title="AI 이미지 생성기", page_icon="🖼️")
st.title("🖼️ AI 이미지 생성기")
st.write("생성된 이미지는 아래 기록에 계속 누적됩니다. 새로운 스타일을 선택해 이미지를 추가해보세요.")

# --- 세션 상태 초기화 ---
# 'image_history' 키가 세션 상태에 없으면, 빈 리스트로 초기화합니다.
if "image_history" not in st.session_state:
    st.session_state.image_history = []

# --- 사이드바 - 설정 ---
st.sidebar.title("🔑 설정")
openai_api_key = st.sidebar.text_input("OpenAI API 키 입력", type="password")

# 이미지 크기 선택 옵션
size_options = ["1024x1024", "1792x1024", "1024x1792"]
selected_size = st.selectbox("이미지 크기를 선택하세요", size_options, index=0)

# 기록 지우기 버튼
if st.sidebar.button("기록 지우기"):
    st.session_state.image_history = [] # 이미지 기록 리스트를 비웁니다.
    st.rerun() # 페이지를 새로고침하여 즉시 반영합니다.

if not openai_api_key:
    st.sidebar.warning("OpenAI API 키를 입력하세요.")
    st.stop()

# --- OpenAI 클라이언트 설정 ---
try:
    client = OpenAI(api_key=openai_api_key)
except Exception as e:
    st.error(f"OpenAI 클라이언트 설정 중 오류가 발생했습니다: {e}")
    st.stop()

# --- 사용자 입력 ---
prompt = st.text_input("📝 그리고 싶은 이미지에 대한 설명을 입력하세요",
                       value="A cute dog running in a field")

# --- 스타일 선택 버튼 ---
st.subheader("🎨 원하는 스타일을 선택하세요")

styles = {
    "리얼리즘": "a realistic and detailed photograph of",
    "만화": "a cute cartoon style of",
    "수채화": "a watercolor painting of",
    "일러스트": "an illustration of"
}



cols = st.columns(len(styles))
style_keys = list(styles.keys())

# --- 버튼 클릭 및 이미지 생성 로직 ---
for i, col in enumerate(cols):
    style_name = style_keys[i]
    if col.button(style_name):
        final_prompt = f"{styles[style_name]} {prompt}"

        with st.spinner(f"'{style_name}' 스타일로 이미지를 생성 중입니다... (2개 생성)"):
            try:
                for j in range(2):
                    response = client.images.generate(
                        prompt=final_prompt,
                        model="dall-e-3",
                        n=1,
                        size=selected_size,
                        quality="standard"
                    )
                    image_url = response.data[0].url
                    
                    # ★★★ 생성된 이미지 정보를 세션 상태에 저장 ★★★
                    st.session_state.image_history.append({
                        "url": image_url,
                        "prompt": prompt,
                        "style": style_name,
                        "size": selected_size
                    })

                st.success("이미지 2개를 성공적으로 생성했습니다! 아래 기록에서 확인하세요.")
            except Exception as e:
                st.error(f"이미지 생성 중 오류가 발생했습니다: {e}")

st.write("---")
st.subheader("🖼️ 생성된 이미지 기록")

# --- 기록된 이미지 표시 로직 ---
if not st.session_state.image_history:
    st.info("아직 생성된 이미지가 없습니다. 스타일을 선택해 이미지를 만들어보세요!")
else:
    # 최신 이미지가 위로 오도록 역순으로 표시
    for i, img_data in enumerate(reversed(st.session_state.image_history)):
        caption_text = f"#{len(st.session_state.image_history) - i} | {img_data['style']} | {img_data['size']} | {img_data['prompt']}"
        st.image(
            img_data["url"], 
            caption=caption_text,
            use_container_width=True
        )
        st.write("") # 이미지 사이에 약간의 공간 추가
