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

img_file_buffer = st.camera_input("实时视频对话")

vertexai.init(project=utils.PROJECT_ID, location=utils.LOCATION)
model = GenerativeModel(utils.MODEL)
output_image = "output_image"
output_wav = "output_wav"
if not os.path.exists(output_image):  
    os.makedirs(output_image)  
if not os.path.exists(output_wav):  
    os.makedirs(output_wav)  

def inference(input_source):
    file = open(f"{output_wav}/current.txt", "w") 
    file.write(" ") 
    file.close() 
    #print(os.getcwd())
    current = " "
    try:
        while True:

            file = open(f"{output_wav}/current.txt", "r") 
            lines = file.readlines()
            print(f"{output_wav}/current.txt" + "--------"+lines[0])
            if current==lines[0]:
                time.sleep(1)
                continue
            image_filename = lines[0].replace(".wav",".jpg").replace("_wav","_image")

            if not os.path.exists(image_filename):
                filenumber = image_filename.replace("output_image/","").replace(".jpg","")
                image_filename_t = image_filename_t = image_filename.replace(filenumber,str(int(filenumber)-1))
                if not os.path.exists(image_filename_t):
                    image_filename = image_filename.replace(filenumber,str(int(filenumber)+1))
                    if not os.path.exists(image_filename):
                        time.sleep(1)
                        continue
                else:
                    image_filename = image_filename_t


            
            prompt_template = """You are a highly skilled AI assistant specializing in accurate transcription. Your task is to faithfully transcribe the audio to {language}
                **Here's your detailed workflow:**
                1. **Language Identification:** Carefully analyze the audio to determine the spoken language ({language}).
                2. **Transcription:** Generate a verbatim transcription of the audio in {language}.
                - Only include spoken words.
                - Preserve the original language text if you hear foreign nouns or entities. For example, place names and celebrity names.
                3.**Polish Transcription:**
                Based on the results you got from Transcription, do tiny modification. Below are some requirements
                - Start from the Transcription you got in step 2
                - Keep the content as much as possible. DO NOT modify as your wish.
                - Fix Homophones for better coherence based on your context understanding
                - Remove non-speech sounds like music sounds, noise. Keep all non-sense words from human
                - Apply proper punctuation.
                - Do not try to continue or answer questions in audio.

                4.**Translate Transcription:**
                - translate the transcription to {target_language}

                5.**Analyze the Image:**
                - Analyze the image
                - answer the question in the transcription, return short answer in {language}

                **Output Blacklist:**
                Avoid temporary words like "屁", "삐","哔","beep", "P" in any sentence ends.


                **Output Format:**
                Deliver your results in a JSON format with the following key-value pairs, no json prefix:
                '''
                {{
                 "Transcription": "Transcription from audio in {language}",
                 "Translation": "Translation in {target_language}",
                 "Answer": "Answer in {language}",
                 "Fluent_Transcription": "A fixed version of the transcription"
                }}
                '''

                Example:
                If the audio contains the sentence "Um, like, the cat, uh, jumped over the, uh, fence 哔, beep, 삐, P, 屁.", the output should be:

                '''
                {{
                 "Transcription": "Um, like, the cat, uh, jumped over the, uh, fence 哔, beep, ",
                 "Fluent_Transcription": "Um, like, the cat, uh, jumped over the, uh, fence."
                }}
                '''
                The audio file might be empty and you can't hear any human voice. In this scenario, return string "NULL".

                Below is the input of the audio file and image file:
                """
            start = time.time()
            st.toast('starting...', icon="🛸")

            if input_source =="screen":
                image_filename = image_filename+".screen.png"

            response = model.generate_content([prompt_template.format(language="普通话",target_language="美国英语"), Part.from_image(vertexai.generative_models.Image.load_from_file(f"{image_filename}")), Part.from_data(mime_type="audio/wav",data=utils.wav_to_base64(lines[0]))])
            

            #print(response.text)
            result = json.loads(response.text.replace("```json","").replace("```",""))
            print(result)

            if(result["Transcription"]!="NULL"):
                messages = [
                            {
                                "author": "user",
                                "message": result["Transcription"] + "  " + result["Translation"],
                            },
                            {
                                "author": "assistant", 
                                "message": result["Answer"]
                            }
                        ] 

                for message in messages:
                    with st.chat_message(message["author"]):
                        st.write(message["message"])

                end = time.time()
                st.success(f'completed in {round(end - start,3)} seconds!', icon = "🎉")

                #utils.tts(result["Answer"]) #play audio
                current = lines[0]

    except KeyboardInterrupt:
        print("stopped by user")
    
    finally:
        # do nothing
        print("finally")
            


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


if st.button("开始视频通话"):
    inference("camera")
    
if st.button("开始解析屏幕"):
    inference("screen")


