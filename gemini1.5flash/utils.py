import cv2
import pyaudio
import wave
import threading
import time
import datetime
import numpy as np
import os
import glob
import base64
import vertexai
from google import genai
from vertexai.generative_models import GenerativeModel, Part,Image
from google.cloud import texttospeech
import json
import simpleaudio as sa
from playsound3 import playsound
from pathlib import Path


PROJECT_ID = "your project id"#your project id
LOCATION="us-central1"

GEMINI_15_FLASH_002 = "gemini-1.5-flash-002"
GEMINI_15_PRO_002 = "gemini-1.5-pro-002"
#GEMINI_20_FLASH_EXP = "gemini-2.0-flash-exp"


MODEL = GEMINI_15_FLASH_002

vertexai.init(project=PROJECT_ID, location=LOCATION)

unix_timestamp_seconds = int(time.time())

client = texttospeech.TextToSpeechClient()


def wav_to_base64(wav_file_path):
    try:
        with open(wav_file_path, 'rb') as wav_file:
            wav_data = wav_file.read()
            base64_data = base64.b64encode(wav_data).decode('utf-8')
            return base64_data
    except Exception as e:
        print(f"Error: {e}")
        return None

def wav_to_bytes(wav_file_path):
    try:
        audio_file_path = Path(wav_file_path)
        audio_bytes = audio_file_path.read_bytes()  
        return audio_bytes
    except Exception as e:
        print(f"Error: {e}")
        return None

def image_to_bytes(image_file_path):
    try:
        with Image.open(image_file_path) as img:
            # Create a BytesIO object
            byte_arr = io.BytesIO()

            # Save the image in the BytesIO object
            img.save(byte_arr, format='JPEG') 

            # Get the byte data
            image_bytes = byte_arr.getvalue() 
            return image_bytes
    except Exception as e:
        print(f"Error: {e}")
        return None

def tts(transcription):
    # Instantiates a client
    output_dir = "output_wav"
    
    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=transcription)

    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    voice = texttospeech.VoiceSelectionParams(
        language_code="zh-Hans-CN", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    unix_timestamp_seconds = int(time.time())

    #os.system("afplay file.mp3") 

    # The response's audio_content is binary.
    with open(f"{output_dir}/{unix_timestamp_seconds}.mp3", "wb") as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        print(f'Audio content written to file "{unix_timestamp_seconds}.mp3"')
        

        # for playing wav file
        time.sleep(1)
        #song = AudioSegment.from_mp3(f"{output_dir}/output.mp3")
        #print('playing sound using  pydub')
        #play(song)
        #os.system(f"{output_dir}/{unix_timestamp_seconds}.mp3")

        print(os.path.join(os.getcwd(), f"{output_dir}/{unix_timestamp_seconds}.mp3"))
        playsound(os.path.join(os.getcwd(), f"{output_dir}/{unix_timestamp_seconds}.mp3"))

def files(curr_dir = '.', ext = '*.exe'):
    """当前目录下的文件"""
    for i in glob.glob(os.path.join(curr_dir, ext)):
        yield i


