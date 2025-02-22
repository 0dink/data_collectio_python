import socket
from video_utils import send_receive_and_save

def read_ip():
    try:
        return open("./inputs/server_ip.txt", "r").readline().strip()
    except Exception as e:
        print(f"Error reading IP: {e}")
        exit(1)

def main():
    server_ip = read_ip()

    # Create separate sockets for audio and video
    video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    audio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        video_socket.connect((server_ip, 8080))
        audio_socket.connect((server_ip, 8081))
        print("Connected to the server on both sockets")
    except Exception as e:
        print(f"Connection failed: {e}")
        exit(1)

    send_receive_and_save(audio_socket, video_socket, 20, "Client")

    # Close sockets
    video_socket.close()
    audio_socket.close()

if __name__ == "__main__":
    main()
