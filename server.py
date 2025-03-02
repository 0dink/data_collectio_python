import socket
import time 
import random
from utilities.video_utils import send_receive_and_save
from utilities.io_utils import create_collection_folder, read_config
from utilities.calibration_utils import display_dot_and_record

def generate_seeded_id():
    random.seed(int(time.time()))  # Seed with current timestamp
    return random.randint(0, 2**32 - 1)  # Generate 32-bit integer

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

    unique_id = generate_seeded_id()
    print(f"Generated unique ID: {unique_id}")
    with open(f"{save_collection_to}/session_id.txt", "w") as f:
        f.write(str(unique_id))

    video_client.sendall(unique_id.to_bytes(4, 'big'))

    # Start send/receive processes
    send_receive_and_save(audio_client, video_client, config["fps"], save_collection_to, config["width"], config["height"])

    # Close connections
    video_client.close()
    audio_client.close()
    video_socket.close()
    audio_socket.close()

if __name__ == "__main__":
    main()

