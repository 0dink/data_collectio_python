import socket
from utilities.video_utils import send_receive_and_save
from utilities.io_utils import create_collection_folder, read_config
from utilities.calibration_utils import display_dot_and_record

def main():
    # Initialize server sockets

    config = read_config()
    save_collection_to = create_collection_folder(config["output_directory"])

    capture_resolution = (config["width"], config["height"])
    display_resolution = (1920, 1080) # make this dynamic 
    display_dot_and_record(display_resolution, capture_resolution, config["calibration"], config["fps"], save_collection_to, path_step=5)

    ####################
    # connection stuff #
    ####################

    video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    audio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    video_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    audio_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind to different ports
    video_socket.bind(('0.0.0.0', 8080))
    audio_socket.bind(('0.0.0.0', 8081))

    video_socket.listen(5)
    audio_socket.listen(5)

    print("Server listening on ports 8080 (video) and 8081 (audio)...")

    # Accept client connections
    video_client, video_address = video_socket.accept()
    audio_client, audio_address = audio_socket.accept()

    print(f"Video connection established with {video_address}")
    print(f"Audio connection established with {audio_address}")

    # Start send/receive processes
    send_receive_and_save(audio_client, video_client, "Server", config["fps"], save_collection_to, config["width"], config["height"])

    # Close connections
    video_client.close()
    audio_client.close()
    video_socket.close()
    audio_socket.close()

if __name__ == "__main__":
    main()