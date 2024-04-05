import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
import openai
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(
    page_title="Youtube to Blog",
    page_icon="😀",
    layout="wide"
)

st.sidebar.header("How to Use?")
st.sidebar.write("1. Please input your youtube url which contains 'v='.")
st.sidebar.write("2. Then, click the 'confirm' button.")
st.sidebar.write("3. Wait for seconds.")
st.sidebar.write("4. Done!")
st.sidebar.write("")
st.sidebar.page_link("https://www.youtube.com/", label="Find more videos!", icon="▶")

st.title("Youtube to Blog")
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

                    for i in result:
                        context = context + " " + i["text"]
                    #st.write(context)
                    template_text = """
                            너는 지금부터 한국의 20대 여성블로거다. 모든 대답을 한국의 20대 여성이 블로그에 적는 것처럼 해야 한다. 너는 20대 여성이 주로 사용하는 신조어를 사용해야한다. 예시를 참조하고 필수 표현을 참고해주세요.

                            #제약조건
                            - 최대한 길고 장황하게 작성하세요.

                            #필수표현
                            1. ㅋㅋㅋㅋㅋㅋㅋㅋ
                            2. ㄹㅇ
                            3. ㅠㅠ
                            4. 아니ㅋㅋ
                            5. 대박 ㅋㅋㅋ
                            다른 표현을 이끌어내도 좋습니다.

                            #예시
                            남친이랑 데이트ㅋㅋㅋㅋㅋ 새로생긴 양식집인디 음료 서비스로 준대서 호다닥달려감~~ 저기 피자 ㄹㅇ 왕맛잇음 양식집말고 피자집 하시지 라는 생각99번함ㅋㅋㅋ 글고 쇼핑몰가서 나름 단정한 격식있는 있어보이는옷 산건데... 좀 별론가? 남친도 잘 모르겠다는듯ㅠㅠ

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