import cv2
import threading
import time
import datetime
import numpy as np
import os
import glob
import vertexai
import json
from PIL import Image, ImageGrab 

unix_timestamp_seconds = int(time.time())
output_dir = "output_image"

def capture_image():
    # Initialize the camera (0 is usually the default webcam)
    cap = cv2.VideoCapture(0)
    
    # Check if camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    try:
        while True:
            #timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            unix_timestamp_seconds = int(time.time())
            filename = f"{unix_timestamp_seconds}.jpg"
            output_file = os.path.join(output_dir,filename)
            # Capture frame
            ret, frame = cap.read()
            
            if ret:
                # Generate filename with timestamp
                #filename = filename
                
                # Save the frame
                small_frame = cv2.resize(frame, (0,0), fx=0.25, fy=0.25) 
                cv2.imwrite(output_file, small_frame)
                print(f"Saved {output_file}")
                
                # Wait for 1 second
                im = ImageGrab.grab(bbox = None) 
    
                #im2.show() 
                (width, height) = (im.width // 4, im.height // 4)
                im_resized = im.resize((width, height))
                im_resized.save(f"{output_file}.screen.png") 


                time.sleep(1)
            else:
                print("Error: Could not read frame")
                break
                
    except KeyboardInterrupt:
        print("\nRecording stopped by user")
    
    finally:
        # Release the camera
        cap.release()

def files(curr_dir = '.', ext = '*.exe'):
    """当前目录下的文件"""
    for i in glob.glob(os.path.join(curr_dir, ext)):
        yield i

def cleanup_audio_image():
    while True:
        unix_timestamp_seconds = int(time.time())

        # for i in range(unix_timestamp_seconds-600, unix_timestamp_seconds-300):
        #     for j in files(output_dir, f"{i}.*"):
        #         os.remove(j)
        #         print(f"removed {j}")
        # for i in range(unix_timestamp_seconds-600, unix_timestamp_seconds-300):
        #     for j in files("output_wav", f"{i}.*"):
        #         os.remove(j)
        #         print(f"removed {j}")

        for i in range(unix_timestamp_seconds-600, unix_timestamp_seconds-300):
            for j in glob.glob(f"{output_dir}/{i}*"): #files(output_dir, f"{i}.*"):
                os.remove(j)
                print(f"removed {j}")
        for i in range(unix_timestamp_seconds-600, unix_timestamp_seconds-300):
            for j in glob.glob(f"output_wav/{i}*"):#files("output_wav", f"{i}.*"):
                os.remove(j)
                print(f"removed {j}")
        
        time.sleep(60)

def main():
    
    if not os.path.exists(output_dir):  
            os.makedirs(output_dir)  
    # Use threads to record audio and capture image concurrently
    image_thread = threading.Thread(target=capture_image, args=())
    cleanup_thread = threading.Thread(target=cleanup_audio_image, args=())
    
    image_thread.start()
    cleanup_thread.start()

    image_thread.join()
    cleanup_thread.join()

if __name__ == "__main__":
    main()

