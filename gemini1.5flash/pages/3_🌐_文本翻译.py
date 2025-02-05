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



if st.button("翻译图片上的文字输出文字"):

    start = time.time()
    st.toast('starting...', icon="🛸")

    unix_timestamp_seconds = int(time.time()) 
    image_filename = f"{output_image}/{unix_timestamp_seconds-1}.jpg"
    if not os.path.exists(image_filename):
        image_filename = f"{output_image}/{unix_timestamp_seconds-2}.jpg"
    prompt_template = """You are an image analyst expert, extract all text from the image, then identify the language, then translate them into {target_language}, then output them in pair """
    response = model.generate_content([Part.from_image(vertexai.generative_models.Image.load_from_file(f"{image_filename}")),prompt_template.format(target_language="Chinese") ])
    #result = json.loads(response.text.replace("```json","").replace("```",""))
    
    col1, col2 = st.columns(2)
    with col1:
        st.header("要翻译的图片")
        st.image(image_filename)
    with col2:
        st.header("文本对照")
        st.write(response.text)

    end = time.time()
    st.success(f'completed in {round(end - start,3)} seconds!', icon = "🎉")




