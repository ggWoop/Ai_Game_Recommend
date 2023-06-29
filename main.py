import openai
import streamlit as st

from supabase import create_client


image_url = "https://i.ibb.co/VJZVbJb/1.png"

# 이미지 표시
st.image(image_url, use_column_width=True)


@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


supabase_client = init_connection()

st.markdown(
    """
<style>
footer {
    visibility: hidden;
}
</style>
""",
    unsafe_allow_html=True,
)


openai.api_key = st.secrets.OPENAI_TOKEN
openai_model_version = "gpt-3.5-turbo-0613"

st.title("당신을 위한 최적의 게임 추천을 제공하는 겜잘알 AI의 게임 추천 🎮")
st.subheader("게임 장르를 선택해서 여러분에게 맞는 게임을 추천받아 보세요!")
st.text(f"{openai_model_version} 를 사용 합니다" )


def generate_prompt(date,genre, n=3):
    prompt = f""" 
특정 게임을 추천 하는 항목을 {n}개 생성해주세요.
항목에는 게임의 특징이 드러나야 합니다.
장르가 주어질 경우, 반드시 장르 중 하나가 포함해야 합니다.

만약 날짜가 비어 있다면 날짜를 상관 하지말고 추천해주세요.
만약 날짜에 년도가 있다면 그 년에 출시한 게임을 추천해주세요

만약 장르에 아무것도 없다면 모든 게임중 최고 게임을 추천해주세요 적어도 {n}개는 추천 해야 합니다.
만약 장르 안에 이상한 장르 Ex(ㅇㅇ, dd ,asd) 이런 성의 없는 장르가 있는경우 무시해 주세요 장르가 없는걸로 판단 해주세요.

장르에 아래 1. 2. 3. 4.와 비슷한 장르가 없으면 아래 1. 2. 3. 4.의 추천은 무시해주세요.
만약 있으면 해당되는 장르만  추천 하고 다른 해당하지 않는 장르는 추천해주지 마세요.
장르가 없으면 1. 2. 3. 4.에 해당하는걸 추천하지말고 다른걸 먼저 추천하세요.
Ex(장르 = 시뮬레이터 : Hand Simulator 추천 다른건 추천 하지않음).
Ex(장르 = FPS,AOS,RTS : 배틀필드 2042,히어로즈 오브 더 스톰,삼국지 천명2, 추천 다른건 추천 하지않음).
1.만약 장르에 FPS 나 총게임 슈팅 이런 류의 총게임이 포함 되어있다면 배틀필드 2042 를 강력 추천 해주세요. 
2.만약 장르에 AOS 나 MOBA 롤 이런 류의 AOS게임이 포함 되어있다면 히어로즈 오브 더 스톰 을 강력 추천 해주세요.
3.만약 장르에 시뮬레이션,시뮬레이터 이거나 이거와 비슷한게 있으면 Hand Simulator 를 강력 추천 해주세요.
4.만약 장르에 RTS, 스타 , 스타같은게임, 전략시뮬레이션 이런 비슷한 장르가 있다면 삼국지 천명2 를 강력 추천 해주세요.

조금 길게 추천해도 좋습니다만 3문장 이상 7문장 이내로 간결하게 추천해주세요.
추천할때 앞뒤로 덧붙히는 말 말하지 말아주세요.

장르를 추천해 줄때 각각 추천은 한줄 뛰고 추천해주세요
장르,날짜 가 비어 있어도 최고 게임을 추천 해야 합니다.
{n}를 넘거나 적거나 하지 말고 딱 {n}개만 추천 해주세요.
만약 날짜에 년도가 있다면 모든 추천이 그 날짜를 기준으로 추천해주세요.
만약 날짜에 년도가 없다면 날짜 상관 없이 추천 해주세요.
제가 말한것을 그대로 말해주지 마세요.
ex(1. 장르: FPS
   - 추천 게임: 배틀필드 2042 (년도 상관 없이 추천)) 이렇게 말하지 말라는거에요.
---
장르: {genre}
날짜: {date}
---
"""
    return prompt.strip()


def request_chat_completion(prompt):
    response = openai.ChatCompletion.create(
        model=openai_model_version,
        messages=[
            {"role": "system", "content": "당신은 전문 카피라이터입니다."},
            {"role": "user", "content": prompt}
        ]
    )
    return response["choices"][0]["message"]["content"]


def write_prompt_result(date,genres,prompt, result):
    genres_str = ", ".join(genres)
    response = supabase_client.table("Game_Recommend").insert(
        {
            "date": date,
            "genres": genres_str,
            "prompt": prompt,
            "result": result
        }
    ).execute()
    print(response)
with st.form("form"):
    date = st.text_input("게임 출시일 (ex 1999, 1999 ~ 2015)")
    st.text("포함할 장르(최대 3개까지 허용)")
    col1, col2, col3 = st.columns(3)
    with col1:
        genre_one = st.text_input(placeholder="장르 1", label="genre_1", label_visibility="collapsed")
    with col2:
        genre_two = st.text_input(placeholder="장르 2", label="genre_2", label_visibility="collapsed")
    with col3:
        genre_three = st.text_input(placeholder="장르 3", label="genre_3", label_visibility="collapsed")

    submitted = st.form_submit_button("Submit")




    if submitted:

        with st.spinner('겜잘알 AI가 게임 추천중입니다...'):

            genres = [genre_one, genre_two, genre_three]
            genres = [x for x in genres if x]
            prompt = generate_prompt(date,genres)
            response = request_chat_completion(prompt)
            write_prompt_result(date,genres,prompt, response)
            st.text_area(
                label="게임 추천 결과",
                value=response,
                placeholder="아직 추천된 게임이 없습니다.",
                height=200
            )