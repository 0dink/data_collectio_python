import cv2
import threading
import socket
from video_utils import send, receive

# Create client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('server_ip_here', 8080))  # Replace 'server_ip_here' with actual server IP

# Capture video from the client's webcam
cap = cv2.VideoCapture(0)

# Create and start threads for sending and receiving
send_thread = threading.Thread(target=send, args=(client_socket, cap))
receive_thread = threading.Thread(target=receive, args=(client_socket, "Client"))

send_thread.start()
receive_thread.start()

send_thread.join()
receive_thread.join()

# Release resources
cap.release()
cv2.destroyAllWindows()
client_socket.close()
