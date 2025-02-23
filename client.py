import socket
from utilities.video_utils import send_receive_and_save
from utilities.io_utils import create_collection_folder, read_config

def read_ip():
    try:
        return open("./inputs/server_ip.txt", "r").readline().strip()
    except Exception as e:
        print(f"Error reading IP: {e}")
        exit(1)

def main():
    server_ip = read_ip()
    config = read_config()
    save_collection_to = create_collection_folder(config["output_directory"])
    
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

    send_receive_and_save(audio_socket, video_socket, "Client", config["fps"], save_collection_to, config["width"], config["height"],)

    # Close sockets
    video_socket.close()
    audio_socket.close()

if __name__ == "__main__":
    main()
