import streamlit as st
import cv2
import numpy as np
import utils

import pyaudio
import wave
import threading
import time
import datetime
import numpy as np
import os
import base64
import vertexai
#from google import genai
from vertexai.generative_models import GenerativeModel, Part,Image
from vertexai.generative_models import (
    Content,
    FunctionDeclaration,
    GenerationConfig,
    GenerativeModel,
    Part,
    Tool,
    ToolConfig,
)

from google.cloud import translate_v3beta1 as translate
from google.cloud import texttospeech
import json
import simpleaudio as sa
#from pydub import AudioSegment
#from pydub.playback import play
from playsound3 import playsound
from google.cloud import translate_v3beta1 as translate_v3
#from google.cloud import translate_v3
from PIL import Image as PILImage
import os
import img2pdf,pdf2image
from pdf2image import convert_from_path
import webrtcvad
import collections
import signal
import sys
import time
from datetime import datetime

import googlesearch
from googlesearch import search

img_file_buffer = st.camera_input("实时视频")

vertexai.init(project=utils.PROJECT_ID, location=utils.LOCATION)
model = GenerativeModel(utils.MODEL)

output_image = "output_image"
output_wav = "output_wav"
if not os.path.exists(output_image):  
    os.makedirs(output_image)  
if not os.path.exists(output_wav):  
    os.makedirs(output_wav)  


if img_file_buffer is not None:
    # To read image file buffer with OpenCV:
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    # Check the type of cv2_img:
    # Should output: <class 'numpy.ndarray'>
    st.write(type(cv2_img))

    # Check the shape of cv2_img:
    # Should output shape: (height, width, channels)
    st.write(cv2_img.shape)

st.markdown(
    """
<style>
    .st-emotion-cache-4oy321 {
        flex-direction: row-reverse;
        text-align: right;
    }
</style>
""",
    unsafe_allow_html=True,
)

fc_google_search = FunctionDeclaration(
    name="fc_google_search",
    description="when you donot the answers to user's quesiton, do Google search answers for user's question",
    parameters={
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "a question from the user"
            },
        },
    },
)


tools = Tool(
    function_declarations=[
        fc_google_search,
    ],
)
generation_config = GenerationConfig(temperature=1)

if st.button("开始对话"):
    file = open(f"{output_wav}/current.txt", "w") 
    file.write(" ") 
    file.close() 
    #chat_session = model.start_chat()
    current = " "
    history_queue = []

    try:
        while True:
            file = open(f"{output_wav}/current.txt", "r") 
            lines = file.readlines()
            if current==lines[0]:
                time.sleep(1)
                continue

            prompt = """你是一位多功能的机器人，擅长情感陪伴，例如角色扮演，聊天恋爱，情绪抚慰。你也擅长教育，例如口语教学，总结新闻等。
            你也擅长生活助手场景，例如日常饮食、休闲玩乐、出行规划及健身指导，音乐推荐与介绍等。除此之外，回复客户'不在服务范围' 
            分析会话历史: {history}
            根据语音文件中用户的问题进行回答。200字以内。以用户的语言回复，例如用户说中文就用中文回复。
            仅输出json格式，user字段记录用户的话，assistant字段记录你回复的话。如果语音文件中没有内容，输出为空。
            '''
            {{
             "user": "语音文件中的文本",
             "assistant": "你的回复的话"
            }}
            '''
            """
            #tool = Tool.from_google_search_retrieval(grounding.GoogleSearchRetrieval())

            start = time.time()
            st.toast('starting...', icon="🛸")

            response = model.generate_content(
                [Part.from_data(mime_type="audio/wav",data=utils.wav_to_base64(lines[0])),
                prompt.format(history=' '.join(map(str,history_queue)))],
                generation_config=generation_config,
                tools=[tools],
                tool_config=ToolConfig(
                    function_calling_config=ToolConfig.FunctionCallingConfig(
                        # ANY mode forces the model to predict only function calls
                        mode=ToolConfig.FunctionCallingConfig.Mode.ANY,
                        # Allowed function calls to predict when the mode is ANY. If empty, any  of
                        # the provided function calls will be predicted.
                        allowed_function_names=["fc_google_search"],
                    ))
                )

            #st.write(response.candidates)

            if (response.candidates[0].function_calls[0].name == "fc_google_search"):
                # Extract the arguments to use in your API call
                user_question = response.candidates[0].function_calls[0].args["question"]
                search_results = googlesearch.search(user_question, num_results=5,advanced=True)
                search_results_json = []
                for result in search_results:
                    search_results_json.append({"description":result.description})
                #     print("Title:", result.title)
                #     print("URL:", result.url)
                #     print("Description:", result.description)
                #     print("-" * 20)
            #st.write(search_results_json)

            user_prompt_content = Content(
                role="user",
                parts=[
                    #Part.from_text(user_question +"instruction:" +instruction),
                    Part.from_text(user_question),
                    ],
                )
            response1 = model.generate_content(
                [
                    user_prompt_content,  # User prompt
                    response.candidates[0].content,  # Function call response
                    Content(
                        parts=[
                            Part.from_function_response(
                                name="fc_google_search",
                                response={
                                    "content": search_results_json#search_results_json,  # Return the API response to Gemini
                                },
                            )
                        ],
                    ),
                ],
                tools=[tools],
            )
            # Get the model summary response
            #st.write(response1.text)

        
            #result = json.loads(response1.text.replace("```json","").replace("```",""))
            #st.write(response.text)

            if response1.text:
                messages = [
                            {
                                "author": "user",
                                "message": user_question,
                            },
                            {
                                "author": "assistant", 
                                "message": response1.text
                            }
                        ] 

                for message in messages:
                    with st.chat_message(message["author"]):
                        st.write(message["message"])
                end = time.time()
                st.success(f'completed in {round(end - start,3)} seconds!', icon = "🎉")

                #tts(result["assistant")
                current=lines[0]
                if len(history_queue)==10:
                    history_queue.pop(0)
                else:
                    history_queue.append(result)





    except KeyboardInterrupt:
        print("stopped by user")
    
    finally:
        # do nothing
        print("finally")


