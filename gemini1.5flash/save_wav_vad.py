import webrtcvad
import pyaudio
import wave
import collections
import time
import signal
import sys
import os
from datetime import datetime

# Audio parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 480  # 30ms at 16kHz
PADDING_DURATION_MS = 1000  # 1 sec
TRIGGERED = False
RING_BUFFER = collections.deque(maxlen=int(PADDING_DURATION_MS * RATE / (CHUNK * 1000)))

# Initialize PyAudio and WebRTC VAD
audio = pyaudio.PyAudio()
vad = webrtcvad.Vad(3)  # Aggressiveness mode, 0-3
output_dir = "output_wav"
if not os.path.exists(output_dir):  
    os.makedirs(output_dir)  

def handle_int(sig, chunk):
    global TRIGGERED
    TRIGGERED = False
    sys.exit(0)

signal.signal(signal.SIGINT, handle_int)

def save_audio(frames, sample_width):
    unix_timestamp_seconds = int(time.time())
    output_filename = f"{output_dir}/{unix_timestamp_seconds}.wav"

    with wave.open(output_filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(sample_width)
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    print(f"------saving {output_filename}")
    update_current_file(output_filename)
def update_current_file(output_filename):
    file = open(f"{output_dir}/current.txt", "w") 
    file.write(output_filename) 
    file.close() 
      
    print("Data is written into the file.") 

def main():
    global TRIGGERED
    frames = []
    
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )

    print("Recording... Press Ctrl+C to stop.")
    
    while True:
        try:
            frame = stream.read(CHUNK)
            is_speech = vad.is_speech(frame, RATE)
            
            if not TRIGGERED:
                RING_BUFFER.append((frame, is_speech))
                num_voiced = len([f for f, speech in RING_BUFFER if speech])
                
                if num_voiced > 0.9 * RING_BUFFER.maxlen:
                    TRIGGERED = True
                    print("Speech detected - Recording...")
                    for f, s in RING_BUFFER:
                        frames.append(f)
                    RING_BUFFER.clear()
            else:
                frames.append(frame)
                RING_BUFFER.append((frame, is_speech))
                num_unvoiced = len([f for f, speech in RING_BUFFER if not speech])
                
                if num_unvoiced > 0.9 * RING_BUFFER.maxlen:
                    TRIGGERED = False
                    print("Silence detected - Saving file...")
                    save_audio(frames, audio.get_sample_size(FORMAT))
                    frames = []
                    RING_BUFFER.clear()
                    print("Ready for next recording...")
                    
        except KeyboardInterrupt:
            print("\nStopping...")
            break

    print("Cleaning up...")
    stream.stop_stream()
    stream.close()
    audio.terminate()

    if frames:
        save_audio(frames, audio.get_sample_size(FORMAT))
        print("Final audio saved")

if __name__ == "__main__":
    main()
