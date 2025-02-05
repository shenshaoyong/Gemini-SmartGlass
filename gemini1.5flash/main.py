import streamlit as st
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
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from google.genai import types
from vertexai.generative_models import GenerativeModel, Part,Image
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

st.set_page_config(
    page_title="Hello, glass",
    page_icon="😎",
)

vertexai.init(project=utils.PROJECT_ID, location=utils.LOCATION)
model = GenerativeModel(utils.MODEL)

#client = genai.Client(vertexai=True, project='veo-testing', location='us-central1')


output_image = "output_image"
output_wav = "output_wav"
if not os.path.exists(output_image):  
    os.makedirs(output_image)  
if not os.path.exists(output_wav):  
    os.makedirs(output_wav)  



st.write("# Welcome to the console of Shenshaoyong's Checkride demo ! 👋")

st.sidebar.success("start by clicking the demo link ")

st.markdown(
    """
    **👈 Select a demo from the sidebar** 
    """
)
st.image("glass.png")

if st.button("开始语音助手"):
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

            prompt = """你是一位专业的意图识别大师，根据用户的语音中的信息识别用户的意图，匹配到 H.回到首页 A.视频对话翻译 B.图片翻译 C.文本翻译 D.角色扮演. E.Agent
            输出对应的编码，例如，如果识别为图片翻译，输出 B
            '''
            {{
             "intent_id": "意图编码",
             "intent": "意图"
            }}
            '''
            """

            start = time.time()
            st.toast('starting...', icon="🛸")

            response = model.generate_content([Part.from_data(mime_type="audio/wav",data=utils.wav_to_base64(lines[0])),prompt.format(history=' '.join(map(str,history_queue)))])
    
            # response = client.models.generate_content(
            #     model="gemini-2.0-flash-exp",
            #     #contents=[types.Part.from_text("美国2025年总统是？")],
            #     contents=[
            #         # types.Part.from_bytes(
            #         #     data=image_bytes,
            #         #     mime_type='image/jpeg'),
            #         prompt,
            #         # types.Part.from_bytes(
            #         #     data=utils.wav_to_bytes(lines[0]),
            #         #     mime_type='audio/wav'),
            #     ],

            #     config=types.GenerateContentConfig(
            #         response_modalities=["TEXT"],
            #     )
            # )

            print(f"{response}")
            result = json.loads(response.text.replace("```json","").replace("```",""))
            #result = json.loads(response.candidates[0].content.parts[0].replace("```json","").replace("```",""))
            st.write(response.text)
            intent_id= result["intent_id"]
            if intent_id=="A":
                st.switch_page("pages/1_👓_视频对话翻译.py")
            elif intent_id=="B":
                st.switch_page("pages/2_🖼️_图片翻译.py")
            elif intent_id=="C":
                st.switch_page("pages/3_🌐_文本翻译.py")
            elif intent_id=="D":
                st.switch_page("pages/4_☕_角色扮演.py")
            elif intent_id=="E":
                st.switch_page("pages/5_🤖_agent.py")
            elif intent_id=="H":
                st.switch_page("main.py")



    except KeyboardInterrupt:
        print("stopped by user")
    
    finally:
        # do nothing
        print("finally")
