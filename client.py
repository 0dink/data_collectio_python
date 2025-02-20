import socket

from video_utils import send_receive_and_save 

def read_ip():
    try:
        return open("./inputs/server_ip.txt", "r").readline()
    except Exception as e:
        print("getting IP: {e}")
        exit(1)

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create client socket
    try:
        client_socket.connect((read_ip(), 8080))  # Replace 'server_ip_here' with actual server IP
        print("Connected to the server")
    except Exception as e:
        print(f"Connection failed: {e}")
        exit(1)
    send_receive_and_save(client_socket, 30, "Client")

    client_socket.close()

if __name__ == "__main__":
    main()
