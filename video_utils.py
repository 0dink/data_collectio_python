import cv2
import struct
import numpy as np

def send(sock, cap, output_writer):
    """Send video frames over a socket and save them."""
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (1920, 1080))  # Set resolution to 1920x1080
        data = cv2.imencode('.jpg', frame)[1].tobytes()
        size = struct.pack("!I", len(data))  # Send frame size first (4 bytes)

        try:
            sock.sendall(size + data)
            output_writer.write(frame)  # Save the frame to video file
        except:
            break

def receive(sock, window_name, output_writer):
    """Receive and display video frames from a socket and save them."""
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
            output_writer.write(img)  # Save the frame to video file

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except:
            break
