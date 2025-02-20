import cv2
import threading
import socket
import multiprocessing

from video_utils import send, receive, save_to_video 

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

# Create and start threads for sending and receiving
send_thread = threading.Thread(target=send, args=(client_socket, cap))
receive_thread = threading.Thread(target=receive, args=(client_socket, "Client"))

save_process = multiprocessing.Process(target=save_to_video, args=("./output.avi", fps, cap))

send_thread.start()
receive_thread.start()
save_process.start()


send_thread.join()
receive_thread.join()
save_process.join()

# Release resources
cap.release()
cv2.destroyAllWindows()
client_socket.close()
