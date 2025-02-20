import cv2
import threading
import socket
from video_utils import send, receive

# Initialize server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 8080))
server_socket.listen(10)
print("Server listening on port 8080...")

# Accept a client connection
client_socket, client_address = server_socket.accept()
print(f"Connection established with {client_address}")

# Capture video from the server's webcam
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Set the resolution to 1920x1080
cap.set(4, 480)

# Get the actual frame rate from the webcam
fps = cap.get(cv2.CAP_PROP_FPS)
print(f"Using frame rate: {fps} FPS")

# Prepare the output video writer (saving the sent video stream)
fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # Try MJPG codec
output_writer_send = cv2.VideoWriter('server_sent_video.avi', fourcc, fps, (640, 480))

# Create and start threads for sending and receiving
send_thread = threading.Thread(target=send, args=(client_socket, cap, output_writer_send))
receive_thread = threading.Thread(target=receive, args=(client_socket, "Server"))

send_thread.start()
receive_thread.start()

send_thread.join()
receive_thread.join()

# Release resources
cap.release()
output_writer_send.release()
cv2.destroyAllWindows()
client_socket.close()
server_socket.close()
