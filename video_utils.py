import cv2
import struct
import numpy as np

def send(sock, cap):
    """Send video frames over a socket."""
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (640, 480))
        data = cv2.imencode('.jpg', frame)[1].tobytes()
        size = struct.pack("!I", len(data))  # Send frame size first (4 bytes)

        try:
            sock.sendall(size + data)
        except:
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
        except:
            break
