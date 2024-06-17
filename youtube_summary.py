import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
import openai
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(
    page_title="Youtube Summary",
    page_icon="😀",
    layout="wide"
)

st.sidebar.header("How to Use?")
st.sidebar.write("1. Please input your youtube url.")
st.sidebar.write("2. Then, click the 'Confirm' button.")
st.sidebar.write("3. Wait for seconds.")
st.sidebar.write("4. Done!")
st.sidebar.write("")
st.sidebar.page_link("https://www.youtube.com/", label="Find more videos!", icon="▶")

st.title("Youtube Summary")
st.write("")
url = st.text_input("Youtube URL")

button = st.button("Confirm")
context = ""
result = ""
error = 0

if button:
    with st.spinner("Waiting..."):
        if "v=" in url:
            video_id = url.split("?v=")[1]
        elif "youtu.be/" in url:
            video_id = url.split("youtu.be/")[1]
        else:
            st.write("Error occured. Please check the url.")
            error = 1
        
        if error == 0:
            for i in range(5):
                try:
                    result = YouTubeTranscriptApi.get_transcript(video_id, languages=["ko"])

                    for text in result:
                        context = context + " " + text["text"]
                        
                    template_text = """
                            반드시 입력문에 있는 내용을 3줄로 요약해주세요. 아래 출력예시와 비슷하게 3개의 bullet point로 문장을 정리하면 됩니다.

                            # 예시
                            ·금요일 미세먼지 '매우 나쁨'예상: 내몽골 발원 황사, 북서풍으로 유입
                            ·황사위기경보 발령: 수도권, 강원, 충남, 경북에 관심 요청, 외출 자제 권고
                            ·대기질 악화 예상: 30일까지 전국적으로 미세 먼지 '나쁨' 수준 지속 예상

                            # 입력문
                            -{prompt}
                            """

                    template1 = PromptTemplate.from_template(template_text)

                    llm = ChatOpenAI(temperature=0.7, max_tokens=1000, model_name='gpt-3.5-turbo', openai_api_key=openai.api_key)
                    result = (
                        template1
                        | llm
                        | StrOutputParser()
                    )
                    result = result.invoke({"prompt": context})

                    template_text = """
                            아래 입력문에서 영어 키워드 5개만 뽑아내세요. 뽑아낸 키워드는 쉼표로 구분해주세요.

                            #예시
                            apple, steve jobs, presentation, iphone, 2007

                            # 입력문
                            -{prompt}

                            """
                    template1 = PromptTemplate.from_template(template_text)

                    llm = ChatOpenAI(temperature=0.7, max_tokens=1000, model_name='gpt-3.5-turbo', openai_api_key=openai.api_key)
                    result2 = (
                        template1
                        | llm
                        | StrOutputParser()
                    )
                    keyword = result2.invoke({"prompt": context})

                    response = openai.images.generate(
                        model="dall-e-3",
                        prompt=f"{keyword},realistic photo,photo",
                        size="1024x1024",
                        quality="standard",
                        n=1
                    )

                    image_url = response.data[0].url

                    st.write(result)
                    st.write(keyword)
                    st.image(image_url)
                    break
                except:
                    continue
