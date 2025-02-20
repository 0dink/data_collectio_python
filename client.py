import cv2
import threading
import socket
import multiprocessing

from video_utils import send_receive_and_save 

# Create client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('server_ip_here', 8080))  # Replace 'server_ip_here' with actual server IP

send_receive_and_save(client_socket, 30, "Client")

client_socket.close()
