import cv2
import threading
import socket
from video_utils import send, receive

# Create client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_ip = ""
client_socket.connect((server_ip, 8080))  # Replace 'server_ip_here' with actual server IP

# Capture video from the client's webcam
cap = cv2.VideoCapture(0)
cap.set(3, 1920)  # Set the resolution to 1920x1080
cap.set(4, 1080)

# Prepare the output video writer (saving the stream)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
output_writer = cv2.VideoWriter('client_output.avi', fourcc, 30.0, (1920, 1080))

# Create and start threads for sending and receiving
send_thread = threading.Thread(target=send, args=(client_socket, cap, output_writer))
receive_thread = threading.Thread(target=receive, args=(client_socket, "Client"))

send_thread.start()
receive_thread.start()

send_thread.join()
receive_thread.join()

# Release resources
cap.release()
output_writer.release()
cv2.destroyAllWindows()
client_socket.close()