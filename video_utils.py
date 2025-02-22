import multiprocessing.process
import cv2
import struct
import numpy as np
import multiprocessing
import keyboard
import pyaudio
import wave


# Audio Setting 
AUDIO_FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

def capture_video(video_queue, width, height, stop_event):
    try:  
        print("capture_video started")
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
    print("capture_video ended")

def capture_audio(audio_queue, stop_event):
    try:
        print("capture_audio started")
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
    print("capture_audio ended")

def save_frames(video_queue, fps, stop_event):
    try:
        print("save_frames started")
        fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Try MJPG codec
        video_writer = cv2.VideoWriter("./outputs/output.avi", fourcc, fps, (1920, 1080))

        while not stop_event.is_set():
            frame = video_queue.get()
            video_writer.write(frame)
    except Exception as e:
        print(f"Error in save_frames: {e}")

    print("save_frames ended")

def save_audio(audio_queue, stop_event):
    try:
        print("save_audio started")
        p = pyaudio.PyAudio()
        wf = wave.open("./outputs/output_audio.wav", 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsamplewidth(AUDIO_FORMAT)
        wf.setframerate(RATE)

        while not stop_event.is_set():
            audio_chunk = audio_queue.get() 
            
            wf.writeframes(audio_chunk)

        wf.close()
        p.terminate()
    except Exception as e:
        print(f"Error in save_audio: {e}")

    print("save_audio ended")

def send_audio(audio_queue, audio_sock, stop_event):
    print("send_audio started")
    while not stop_event.is_set():
        try:
            audio_data = audio_queue.get()
            audio_size = len(audio_data)

            # Send audio size and data separately
            audio_sock.sendall(struct.pack("!I", audio_size))  # Send size first
            audio_sock.sendall(audio_data)  # Send audio data
        except Exception as e:
            print(f"Error while sending audio: {e}")
    print("send_audio ended")

def send_video(video_queue, video_sock, stop_event):
    print("send_video started")
    while not stop_event.is_set():
        try:
            frame = video_queue.get()
            video_data = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 30])[1].tobytes()
            video_size = len(video_data)

            # Send video size and data separately
            video_sock.sendall(struct.pack("!I", video_size))  # Send size first
            video_sock.sendall(video_data)  # Send video data
        except Exception as e:
            print(f"Error while sending video: {e}")
    print("send_video ended")

def receive_audio(audio_sock, stop_event): 
    print("receive_audio started")
    audio = pyaudio.PyAudio()
    stream = audio.open(format=AUDIO_FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
    
    while not stop_event.is_set():
        try:
            # Receive audio size first
            size_data = audio_sock.recv(4)
            if not size_data:
                break
            
            audio_size = struct.unpack("!I", size_data)[0]

            # Receive audio data
            audio_data = b""
            while len(audio_data) < audio_size:
                packet = audio_sock.recv(audio_size - len(audio_data))
                if not packet:
                    break
                audio_data += packet

            stream.write(audio_data)  # Play the audio immediately

        except Exception as e:
            print(f"Error receiving audio: {e}")

    stream.stop_stream()
    stream.close()
    audio.terminate()
    print("receive_audio ended")

def receive_video(video_sock, window_name, stop_event): 
    print("receive_video started")
    while not stop_event.is_set():
        try:
            # Receive video size first
            size_data = video_sock.recv(4)
            if not size_data:
                break
            
            video_size = struct.unpack("!I", size_data)[0]

            # Receive video data
            video_data = b""
            while len(video_data) < video_size:
                packet = video_sock.recv(video_size - len(video_data))
                if not packet:
                    break
                video_data += packet

            # Decode and display the frame
            nparr = np.frombuffer(video_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is not None:
                cv2.imshow(window_name, img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        except Exception as e:
            print(f"Error receiving video: {e}")

    cv2.destroyAllWindows()
    print("receive_video ended")

def send_receive_and_save(audio_sock, video_sock, fps, window_name, width=1920, height=1080):
    audio_queue = multiprocessing.Queue()
    video_queue = multiprocessing.Queue()
    stop_event = multiprocessing.Event()

    # Create processes
    capture_video_process = multiprocessing.Process(target=capture_video, args=(video_queue, width, height, stop_event,))
    capture_audio_process = multiprocessing.Process(target=capture_audio, args=(audio_queue, stop_event,))
    save_video_process = multiprocessing.Process(target=save_frames, args=(video_queue, fps, stop_event,))
    save_audio_process = multiprocessing.Process(target=save_audio, args=(audio_queue, stop_event,)) 
    send_audio_process = multiprocessing.Process(target=send_audio, args=(audio_queue, audio_sock, stop_event,))
    send_video_process = multiprocessing.Process(target=send_video, args=(video_queue, video_sock, stop_event,))
    receive_audio_process = multiprocessing.Process(target=receive_audio, args=(audio_sock, stop_event,))
    receive_video_process = multiprocessing.Process(target=receive_video, args=(video_sock, window_name, stop_event,))

    # Start processes
    capture_video_process.start()
    capture_audio_process.start()
    save_video_process.start()
    save_audio_process.start()
    send_audio_process.start()
    send_video_process.start()
    receive_audio_process.start()
    receive_video_process.start()

    print("Press 'e' to stop the program.")

    # Listen for 'e' key to stop
    while True:
        if keyboard.is_pressed('e'):
            print("Stopping...")
            stop_event.set()
            break

    capture_video_process.join()
    capture_audio_process.join()
    save_video_process.join()
    save_audio_process.join()
    send_audio_process.join()
    send_video_process.join()
    receive_audio_process.join()
    receive_video_process.join()