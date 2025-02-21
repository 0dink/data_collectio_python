import cv2
import struct
import numpy as np
import multiprocessing

def capture_frames(queue, width, height):
    cap = cv2.VideoCapture(0)
    cap.set(3, width)
    cap.set(4, height)

    while True:
        ret, frame = cap.read()
        if ret:
            queue.put(frame)  # Put the frame in the queue
        else:
            break
    cap.release()

def save_frames(queue, fps):
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # Try MJPG codec
    video_writer = cv2.VideoWriter("./output/output.avi", fourcc, fps, (1920, 1080))
    
    while True:
        video_writer.write(queue.get())

def send_frames(queue, sock):
    while True:
        # frame = cv2.resize(frame, (1920, 1080))
        data = cv2.imencode('.jpg', queue.get())[1].tobytes()
        size = struct.pack("!I", len(data))  # Send frame size first (4 bytes)

        try:
            sock.sendall(size + data)
        except Exception as e:
            print(f"Error while sending: {e}")
            break

def receive(sock, window_name):
    """Receive and display video frames from a socket."""
    while True:
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

    # Create processes
    capture_process = multiprocessing.Process(target=capture_frames, args=(frame_queue, width, height,))
    save_process = multiprocessing.Process(target=save_frames, args=(frame_queue, fps,))
    send_process = multiprocessing.Process(target=send_frames, args=(frame_queue, sock,))
    receive_process = multiprocessing.Process(target=receive, args=(sock, window_name,))

    # Start processes
    capture_process.start()
    save_process.start()
    send_process.start()
    receive_process.start()
    
    # Optionally, wait for processes to finish
    capture_process.join()
    save_process.join()
    send_process.join()
    receive_process.join()

