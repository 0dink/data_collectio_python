import cv2
import struct
import numpy as np
import multiprocessing

def send_frame(sock, frame_queue):
    """Send video frames over a socket."""
    while True:
        frame = frame_queue.get()  # Get a frame from the queue
        if frame is None:  # Check for the sentinel value to stop the process
            break
        data = cv2.imencode('.jpg', frame)[1].tobytes()
        size = struct.pack("!I", len(data))  # Send frame size first (4 bytes)
        try:
            sock.sendall(size + data)  # Send the frame over the socket
        except Exception as e:
            print(f"Error while sending frame: {e}")
            break

def save_frame(frame_queue, output_writer):
    """Save video frames to a file."""
    while True:
        frame = frame_queue.get()  # Get a frame from the queue
        if frame is None:  # Check for the sentinel value to stop the process
            break
        output_writer.write(frame)  # Save the frame to the file

def start_video_processing(cap, sock, output_writer_send):
    """Start the video sending and saving processes."""
    frame_queue = multiprocessing.Queue()

    # Start the send and save processes
    send_process = multiprocessing.Process(target=send_frame, args=(sock, frame_queue))
    save_process = multiprocessing.Process(target=save_frame, args=(frame_queue, output_writer_send))

    send_process.start()
    save_process.start()

    return frame_queue, send_process, save_process

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
        except:
            break