import cv2
import threading
import socket
import struct
from multiprocessing import Process, Queue
from video_utils import send_frame, save_frame

# Create client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('server_ip_here', 8080))  # Replace 'server_ip_here' with actual server IP

# Capture video from the client's webcam
cap = cv2.VideoCapture(0)
cap.set(3, 1920)  # Set the resolution to 1920x1080
cap.set(4, 1080)

# Get the actual frame rate from the webcam
fps = cap.get(cv2.CAP_PROP_FPS)
print(f"Using frame rate: {fps} FPS")

# Prepare the output video writer for saving webcam feed
fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # MJPG codec
output_writer_send = cv2.VideoWriter('client_sent_video.avi', fourcc, fps, (1920, 1080))

# Create a queue to share frames between the save and send processes
frame_queue = Queue()

# Start the send and save processes
send_process = Process(target=send_frame, args=(client_socket, frame_queue))
save_process = Process(target=save_frame, args=(frame_queue, output_writer_send))

send_process.start()
save_process.start()

# Capture and pass frames to both processes
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.resize(frame, (1920, 1080))  # Resize to 640x480 for sending
    frame_queue.put(frame)  # Put the frame in the queue to be processed by the send and save processes

    # Check for quitting condition (e.g., pressing 'q')
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Stop the processes by sending a sentinel value (None)
frame_queue.put(None)
frame_queue.put(None)

# Wait for the processes to finish
send_process.join()
save_process.join()

# Release resources
cap.release()
output_writer_send.release()
cv2.destroyAllWindows()
client_socket.close()
