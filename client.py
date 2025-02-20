import socket

from video_utils import send_receive_and_save 

if __name__ == "__main__":
    # Create client socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('server_ip_here', 8080))  # Replace 'server_ip_here' with actual server IP
        print("Connected to the server")
    except Exception as e:
        print(f"Connection failed: {e}")
        exit(1)
    send_receive_and_save(client_socket, 30, "Client")

    client_socket.close()
