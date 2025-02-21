import cv2
import struct
import numpy as np
import multiprocessing
import time
import keyboard

def capture_frames(queue, width, height, stop_event):
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    if cap.get(cv2.CAP_PROP_FRAME_WIDTH) != width or cap.get(cv2.CAP_PROP_FRAME_HEIGHT) != height:
        cap.release()
        raise RuntimeError(f"Error: Unable to set resolution to {width}x{height}, current resolution is {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")

    while not stop_event.is_set():
        ret, frame = cap.read()
        if ret:
            queue.put(frame)  # Put the frame in the queue
        else:
            break
    cap.release()

def save_frames(queue, fps, stop_event):
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Try MJPG codec
    video_writer = cv2.VideoWriter("./outputs/output.avi", fourcc, fps, (1920, 1080))

    while not stop_event.is_set():
        frame = queue.get()
        video_writer.write(frame)

def send_frames(queue, sock, stop_event):
    while not stop_event.is_set():
        # frame = cv2.resize(frame, (1920, 1080))
        data = cv2.imencode('.jpg', queue.get())[1].tobytes()
        size = struct.pack("!I", len(data))  # Send frame size first (4 bytes)

        try:
            sock.sendall(size + data)
        except Exception as e:
            print(f"Error while sending: {e}")
            break

def receive(sock, window_name, stop_event):
    """Receive and display video frames from a socket."""
    while not stop_event.is_set():
        try:
            # Read frame size (4 bytes)
            size_data = sock.recv(4)

            if not size_data:
                break
            size = struct.unpack("!I", size_data)[0]  # Extract frame size

            # Receive the frame data
            data = b""
            while len(data) < size:
                packet = sock.recv(size - len(data))
                if not packet:
                    break
                data += packet

            # Decode and display the frame
            nparr = np.frombuffer(data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                continue

            cv2.imshow(window_name, img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except Exception as e:
            print(f"Error in receiving frame: {e}")
            break

def send_receive_and_save(sock, fps, window_name, width=1920, height=1080):
    frame_queue = multiprocessing.Queue()
    stop_event = multiprocessing.Event()

    # Create processes
    capture_process = multiprocessing.Process(target=capture_frames, args=(frame_queue, width, height, stop_event,))
    save_process = multiprocessing.Process(target=save_frames, args=(frame_queue, fps, stop_event,))
    send_process = multiprocessing.Process(target=send_frames, args=(frame_queue, sock, stop_event,))
    receive_process = multiprocessing.Process(target=receive, args=(sock, window_name, stop_event,))

    # Start processes
    capture_process.start()
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
    # time.sleep(0.1)  # Prevent high CPU usage

    capture_process.terminate()
    save_process.terminate()
    send_process.terminate()
    receive_process.terminate()
    
    # Optionally, wait for processes to finish
    capture_process.join()
    save_process.join()
    send_process.join()
    receive_process.join()

