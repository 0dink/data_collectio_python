import multiprocessing.process
import cv2
import struct
import numpy as np
import multiprocessing
from multiprocessing import Manager
import keyboard
import pyaudio
import wave
import select
import queue
import socket
import time

# Audio Setting 
AUDIO_FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 2048

def capture_video(send_video_queue, save_video_queue, width, height, save_collection_to, stop_event):
    try:  
        print("capture_video started")
        
        timestamp_flag = True
        
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

        if cap.get(cv2.CAP_PROP_FRAME_WIDTH) != width or cap.get(cv2.CAP_PROP_FRAME_HEIGHT) != height:
            cap.release()
            raise RuntimeError(f"Error: Unable to set resolution to {width}x{height}, current resolution is {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
        
        while not stop_event.is_set():
            ret, frame = cap.read()
            if ret:
                save_video_queue.put(frame)
                send_video_queue.put(frame)
                    
                if timestamp_flag:
                    with open(f"{save_collection_to}/ts_video_captured.txt", "w") as file:
                        file.write(str(time.time()))
                    timestamp_flag = False
            else:
                break
        
        cap.release()
    except Exception as e:
        print(f"error with audio stream: {e}")

    print("capture_video ended")

def capture_audio(audio_queue, save_collection_to, stop_event):
    try:
        print("capture_audio started")
        audio = pyaudio.PyAudio()
        stream = audio.open(format=AUDIO_FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        timestamp_flag = True

        while not stop_event.is_set():
            audio_data = stream.read(CHUNK, exception_on_overflow=True)
            audio_queue.put(audio_data)
            
            if timestamp_flag:
                with open(f"{save_collection_to}/ts_audio_capture.txt", "w") as file:
                    file.write(str(time.time()))
                timestamp_flag = False

    except Exception as e:
        print(f"Error in capture_audio: {e}")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    print("capture_audio ended")

def save_frames(save_video_queue, fps, save_collection_to, width, height, stop_event):
    try:
        print("save_frames started")
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        video_writer = cv2.VideoWriter(f"{save_collection_to}/webcam_video.avi", fourcc, fps, (width, height))
        
        while not stop_event.is_set():
            try:
                frame = save_video_queue.get(timeout=0.1)
                video_writer.write(frame)
            except queue.Empty:
                continue
        
        video_writer.release()
    except Exception as e:
        print(f"Error in save_frames: {e}")

    print("save_frames ended")

def send_audio(audio_queue, audio_sock, save_collection_to, stop_event):
    print("send_audio started")
    audio_sock.settimeout(2.0)
    audio_frames = []

    while not stop_event.is_set():
        try:
           
            audio_data = audio_queue.get(timeout=0.1)
            audio_frames.append(audio_data)
            audio_size = len(audio_data)
            timestamp = time.time()

            # Send audio size and data separately
            audio_sock.sendall(struct.pack("!dI", timestamp, audio_size))  # Send size first
            audio_sock.sendall(audio_data)  # Send audio data
        
        except queue.Empty:
            continue
        except (socket.timeout, socket.error) as e:
            print(f"Socket error while sending audio: {e}")
            break
        except Exception as e:
            print(f"Error while sending audio: {e}")

    if audio_frames: # for saving sent audio
        try: 
            audio = pyaudio.PyAudio()
            stream = audio.open(format=AUDIO_FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
            
            with wave.open(f"{save_collection_to}/sent_audio.wav", "wb") as wf:
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
    
    audio_sock.close()
    print("send_audio ended")

def send_video(video_queue, video_sock, stop_event):
    print("send_video started")
    video_sock.settimeout(2.0)  # Prevent socket from hanging forever
    
    while not stop_event.is_set():
        try:
            
            # while not video_queue.empty():
            #     video_queue.get_nowait()  # Discard older frame
            
            frame = video_queue.get(timeout=0.1)
            video_data = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 25])[1].tobytes()
            video_size = len(video_data)
            timestamp = time.time()

            video_sock.sendall(struct.pack("!dI", timestamp, video_size))  # Send size first
            video_sock.sendall(video_data)  # Send video data
        
        except queue.Empty:
            continue
        except (socket.timeout, socket.error) as e:
            print(f"Socket error while sending video: {e}")
            break
        except Exception as e:
            print(f"Error while sending video: {e}")
    
    video_sock.close()
    print("send_video ended")

def receive_audio(audio_sock, audio_buffer, stop_event): 
    print("receive_audio started")
    audio = pyaudio.PyAudio()
    stream = audio.open(format=AUDIO_FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
    
    while not stop_event.is_set():
        try:
            # Wait for data to be available with a timeout
            ready, _, _ = select.select([audio_sock], [], [], 0.1)
            if not ready:
                continue  # No data, check stop_event again

            # Receive audio size first
            header = audio_sock.recv(12)
            if not header:
                break
                        
            timestamp, audio_size = struct.unpack("!dI", header)

            # Receive audio data
            audio_data = b""
            while len(audio_data) < audio_size:
                ready, _, _ = select.select([audio_sock], [], [], 0.1)
                if not ready:
                    continue  # No data, avoid blocking
                
                packet = audio_sock.recv(audio_size - len(audio_data))
                if not packet:
                    break
                audio_data += packet
            
            if audio_data:
                # stream.write(audio_data)
                audio_buffer[timestamp] = audio_data  

        except (socket.timeout, socket.error) as e:
            print(f"Socket error in receive_audio: {e}")
            break  
        except Exception as e:
            print(f"Error receiving audio: {e}")
            break

    stream.stop_stream()
    stream.close()
    audio.terminate()
    audio_sock.close()
    print("receive_audio ended")

def receive_video(video_sock, video_buffer, stop_event): 
    print("receive_video started")
    
    while not stop_event.is_set():
        try:
            
            # Wait for data availability
            ready, _, _ = select.select([video_sock], [], [], 0.1)
            if not ready:
                continue  # No data, check stop_event again
            
            # Receive video size first
            header = video_sock.recv(12)
            if not header:
                break

            timestamp, video_size = struct.unpack("!dI", header)

            # Receive video data
            video_data = b""
            while len(video_data) < video_size:
                ready, _, _ = select.select([video_sock], [], [], 0.1)
                if not ready:
                    continue  # No data, avoid blocking
                
                packet = video_sock.recv(video_size - len(video_data))
                if not packet:
                    break
                video_data += packet

            # Decode and display the frame
            if video_data:
                video_buffer[timestamp] = video_data

        except (socket.timeout, socket.error) as e:
            print(f"Socket error in receive_video: {e}")
            break  
        except Exception as e:
            print(f"Error receiving video: {e}")
            break

    video_sock.close()
    print("receive_video ended")

def sync_playback(audio_buffer, video_buffer, save_collection_to, width, height, stop_event):
    print("sync_playback started")
    timestamp_flag = True
    
    audio = pyaudio.PyAudio()
    stream = audio.open(format=AUDIO_FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
    
    fps = 20
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video_writer = cv2.VideoWriter(f"{save_collection_to}/received_video.avi", fourcc, fps, (width, height))

    while not stop_event.is_set():
        if not video_buffer:  
            continue  # Always wait for video

        # Get sorted timestamps (latest first)
        audio_timestamps = sorted(audio_buffer.keys())
        video_timestamps = sorted(video_buffer.keys())

        if not video_timestamps:
            continue

        # Keep only the most recent 1-2 frames in each buffer to reduce delay
        while len(video_timestamps) > 2:
            video_buffer.pop(video_timestamps.pop(0), None)

        while len(audio_timestamps) > 2:
            audio_buffer.pop(audio_timestamps.pop(0), None)

        # Get the latest video frame
        video_ts = video_timestamps[0]
        frame_data = video_buffer.get(video_ts)

        if frame_data: 
            video_buffer.pop(video_ts, None)  # Remove only if it exists

            # Find the closest audio match
            if audio_timestamps:
                closest_audio_ts = min(audio_timestamps, key=lambda t: abs(t - video_ts))
                if abs(closest_audio_ts - video_ts) <= 0.15:  # 150ms max drift
                    audio_data = audio_buffer.pop(closest_audio_ts, b"\x00" * CHUNK)
                else:
                    audio_data = b"\x00" * CHUNK  # Insert silence if too far apart
            else:
                audio_data = b"\x00" * CHUNK  # No audio, insert silence

            # Decode and show video frame
            nparr = np.frombuffer(frame_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is not None:
                cv2.imshow("Video", img)
                img_ts = time.time()
                video_writer.write(img)

            # Play audio
            audio_ts = time.time()
            stream.write(audio_data)
            
            if timestamp_flag:
                with open(f"{save_collection_to}/ts_display.txt", "w") as file:
                    file.write(f"video start timestamp: {img_ts}\n")
                    file.write(f"audio start timestamp: {audio_ts}\n")
                timestamp_flag = False

        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_event.set()
            break

    stream.stop_stream()
    stream.close()
    audio.terminate()
    video_writer.release()
    cv2.destroyAllWindows()
    print("sync_playback ended")

def send_receive_and_save(audio_sock, video_sock, fps, save_collection_to, width, height):
    audio_queue = multiprocessing.Queue()
    send_video_queue = multiprocessing.Queue()
    save_video_queue = multiprocessing.Queue()
    stop_event = multiprocessing.Event()

    manager = Manager()
    audio_buffer = manager.dict()
    video_buffer = manager.dict()

    # Create processes
    capture_video_process = multiprocessing.Process(target=capture_video, args=(send_video_queue, save_video_queue, width, height, save_collection_to, stop_event,))
    capture_audio_process = multiprocessing.Process(target=capture_audio, args=(audio_queue, save_collection_to, stop_event,))
    save_video_process = multiprocessing.Process(target=save_frames, args=(save_video_queue, fps, save_collection_to, width, height, stop_event,))
    send_audio_process = multiprocessing.Process(target=send_audio, args=(audio_queue, audio_sock, save_collection_to, stop_event,)) # also saves audio
    send_video_process = multiprocessing.Process(target=send_video, args=(send_video_queue, video_sock, stop_event,))
    receive_audio_process = multiprocessing.Process(target=receive_audio, args=(audio_sock, audio_buffer, stop_event,))
    receive_video_process = multiprocessing.Process(target=receive_video, args=(video_sock, video_buffer, stop_event,))
    sync_process = multiprocessing.Process(target=sync_playback, args=(audio_buffer, video_buffer, save_collection_to, width, height, stop_event,))
    
    # Start processes
    capture_video_process.start()
    capture_audio_process.start()
    save_video_process.start()
    send_audio_process.start()
    send_video_process.start()
    receive_audio_process.start()
    receive_video_process.start()
    sync_process.start()

    print("=============================")
    print("Press 'e' to stop the program.")

    # Listen for 'e' key to stop
    while True:
        if keyboard.is_pressed('e'):
            print("Stopping...")
            stop_event.set()
            break
    
    time.sleep(0.5)

    capture_video_process.join(timeout=5)
    if capture_video_process.is_alive():
        print(f"Capture video process is still alive (PID: {capture_video_process.pid}) and was terminated")
        capture_video_process.terminate()
        capture_video_process.join()
    else:
        print(f"Capture video process joined successfully.")

    capture_audio_process.join(timeout=5) 
    if capture_audio_process.is_alive():
        print(f"Capture audio process is still alive (PID: {capture_audio_process.pid}) and was terminated")
        capture_audio_process.terminate()
        capture_audio_process.join()
    else:
        print(f"Capture audio process joined successfully.")

    save_video_process.join()
    send_audio_process.join()
    send_video_process.join()
    receive_audio_process.join()
    receive_video_process.join()
    sync_process.join()

    return
