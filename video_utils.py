import cv2
import struct
import numpy as np
import multiprocessing
import keyboard
import pyaudio
import wave
import time
import csv

# Audio Setting 
AUDIO_FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

def append_to_csv(filename, value1, value2, value3):
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([value1, value2, value3])

def capture_video(video_queue, width, height, stop_event):
    try:  
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        if cap.get(cv2.CAP_PROP_FRAME_WIDTH) != width or cap.get(cv2.CAP_PROP_FRAME_HEIGHT) != height:
            cap.release()
            raise RuntimeError(f"Error: Unable to set resolution to {width}x{height}, current resolution is {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")

        while not stop_event.is_set():
            ret, frame = cap.read()
            if ret:
                video_queue.put(frame)  # Put the frame in the queue
            else:
                break
            
    except Exception as e:
        print(f"error with audio stream: {e}")

    cap.release()

def capture_audio(audio_queue, stop_event):
    try:
        audio = pyaudio.PyAudio()
        stream = audio.open(format=AUDIO_FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

        while not stop_event.is_set():
            audio_data = stream.read(CHUNK, exception_on_overflow=True)
            audio_queue.put(audio_data)

    except Exception as e:
        print(f"error with audio stream: {e}")

    stream.stop_stream()
    stream.close()
    audio.terminate()

def save_frames(video_queue, fps, stop_event):
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Try MJPG codec
    video_writer = cv2.VideoWriter("./outputs/output.avi", fourcc, fps, (1920, 1080))

    while not stop_event.is_set():
        frame = video_queue.get()
        video_writer.write(frame)

def send_audio_video(audio_queue, video_queue, sock, stop_event): 
    audio_frames = []

    while not stop_event.is_set():
        try:
            start_time = time.time()
            frame = video_queue.get()
            video_data = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 30])[1].tobytes()

            audio_data = audio_queue.get()
                        
            audio_frames.append(audio_data)

            packet = audio_data + video_data
            sock.sendall(packet)

            time_to_send = time.time() - start_time
            append_to_csv("./outputs/sending_info.csv", time_to_send, len(video_data), len(audio_data))

        except Exception as e:
            print(f"Error while sending {e}")
    
    if audio_frames: # saves audio that is sent
        try: 
            audio = pyaudio.PyAudio()
            stream = audio.open(format=AUDIO_FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
            
            with wave.open("./outputs/sent_audio.wav", "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(audio.get_sample_size(AUDIO_FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b"".join(audio_frames))
            
            stream.stop_stream()
            stream.close()
            audio.terminate()
        except Exception as e:
            print(f"Error when saving audio: {e}")
    else:
        print("No audio data received, skipping file save.")

def receive_audio_video(sock, window_name, stop_event):
    
    audio = pyaudio.PyAudio()
    stream = audio.open(format=AUDIO_FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
    
    audio_frames = []

    while not stop_event.is_set():
        try:
            
            audio_data = sock.recv(2048)
            if not audio_data:
                break  # Stop if no data is received

            video_data = sock.recv(1000000)  # Large buffer to get the rest in one go
            if not video_data:
                break

            # Decode and display the frame
            nparr = np.frombuffer(video_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is not None:
                cv2.imshow(window_name, img)

            stream.write(audio_data)
            audio_frames.append(audio_data)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        except Exception as e:
            print(f"Error receiving: {e}")
    
    if audio_frames:
        try: 
            with wave.open("./outputs/received_audio.wav", "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(audio.get_sample_size(AUDIO_FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b"".join(audio_frames))
            
            stream.stop_stream()
            stream.close()
            audio.terminate()
        except Exception as e:
            print(f"Error when saving audio: {e}")
    else:
        print("No audio data received, skipping file save.")

def send_receive_and_save(sock, fps, window_name, width=640, height=480):
    audio_queue = multiprocessing.Queue()
    video_queue = multiprocessing.Queue()
    stop_event = multiprocessing.Event()

    # Create processes
    capture_video_process = multiprocessing.Process(target=capture_video, args=(video_queue, width, height, stop_event,))
    capture_audio_process = multiprocessing.Process(target=capture_audio, args=(audio_queue, stop_event,))
    save_process = multiprocessing.Process(target=save_frames, args=(video_queue, fps, stop_event,))
    send_process = multiprocessing.Process(target=send_audio_video, args=(audio_queue, video_queue, sock, stop_event,))
    receive_process = multiprocessing.Process(target=receive_audio_video, args=(sock, window_name, stop_event,))

    # Start processes
    capture_video_process.start()
    capture_audio_process.start()
    save_process.start()
    send_process.start()
    receive_process.start()

    print("Press 'e' to stop the program.")

    # Listen for 'e' key to stop
    while True:
        if keyboard.is_pressed('e'):
            print("Stopping...")
            stop_event.set()
            break
    
    # Optionally, wait for processes to finish
    capture_video_process.join()
    capture_audio_process.join()
    save_process.join()
    send_process.join()
    receive_process.join()
