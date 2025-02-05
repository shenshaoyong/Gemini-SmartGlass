import streamlit as st
import cv2
import numpy as np
import start_backend as start

import pyaudio
import wave
import threading
import time
import datetime
import numpy as np
import os
import base64
import utils

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

output_image = "output_image"
output_wav = "output_wav"
if not os.path.exists(output_image):  
    os.makedirs(output_image)  
if not os.path.exists(output_wav):  
    os.makedirs(output_wav)  


def translate_document(
    img_path: str,
) -> translate_v3.TranslationServiceClient:
    """Translates a document.

    Args:
        project_id: The GCP project ID.
        file_path: The path to the file to be translated.

    Returns:
        The translated document.
    """

    image = PILImage.open(img_path)
    pdf_path = f"{img_path}.pdf"
 
    # converting into chunks using img2pdf
    pdf_bytes = img2pdf.convert(image.filename)
     
    # opening or creating pdf file
    file = open(pdf_path, "wb")
     
    # writing pdf files with chunks
    file.write(pdf_bytes)
     
    # closing image file
    image.close()
     
    # closing pdf file
    file.close()

    
    client = translate_v3.TranslationServiceClient()
    parent = f"projects/{utils.PROJECT_ID}/locations/{utils.LOCATION}"

    # Supported file types: https://cloud.google.com/translate/docs/supported-formats
    with open(pdf_path, "rb") as document:
        document_content = document.read()

    document_input_config = {
        "content": document_content,
        "mime_type": "application/pdf",
    }

    response = client.translate_document(
        request={
            "parent": parent,
            "target_language_code": "zh_CN",
            "document_input_config": document_input_config,
        }
    )

    # To output the translated document, uncomment the code below.
    f = open(f"{img_path}.pdf.pdf", 'wb')
    f.write(response.document_translation.byte_stream_outputs[0])
    f.close()

    pdf2img(f"{img_path}.pdf.pdf")

    # If not provided in the TranslationRequest, the translated file will only be returned through a byte-stream
    # and its output mime type will be the same as the input file's mime type
    print(
        f"Response: Detected Language Code - {response.document_translation.detected_language_code}"
    )

    return response

def pdf2img(pdf_path):
    # Store Pdf with convert_from_path function
    images = convert_from_path(pdf_path)

    for i in range(len(images)):
      
          # Save pages as images in the pdf
        images[i].save(f'{pdf_path}_{i}.jpg', 'JPEG')


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


if st.button("翻译图片上的文字生成图片"):
    start = time.time()
    st.toast('starting...', icon="🛸")

    unix_timestamp_seconds = int(time.time())
    #st.image(f"output/{unix_timestamp_seconds-2}.jpg", caption="要翻译的图片")
    image_filename = f"{output_image}/{unix_timestamp_seconds-1}.jpg"
    if not os.path.exists(image_filename):
        image_filename = f"{output_image}/{unix_timestamp_seconds-2}.jpg"
 
    translate_document(image_filename)
    #st.image(f"output/{unix_timestamp_seconds-2}.jpg.pdf.pdf_0.jpg", caption="翻译后的图片")

    col1, col2 = st.columns(2)
    with col1:
        st.header("要翻译的图片")
        st.image(image_filename)
    with col2:
        st.header("翻译后的图片")
        st.image(f"{image_filename}.pdf.pdf_0.jpg")


    end = time.time()
    st.success(f'completed in {round(end - start,3)} seconds!', icon = "🎉")
