import socket
import time 
import random
from screeninfo import get_monitors
from utilities.video_utils import send_receive_and_save
from utilities.io_utils import create_collection_folder, read_config
from utilities.calibration_utils import display_dot_and_record

def generate_seeded_id():
    random.seed(int(time.time()))  # Seed with current timestamp
    return random.randint(0, 2**32 - 1)  # Generate 32-bit integer

def main():
    config = read_config()
    session_id = generate_seeded_id()
    save_collection_to = create_collection_folder(config["output_directory"])

    capture_resolution = (config["width"], config["height"])
    
    for monitor in get_monitors():
        if monitor.is_primary:
            display_resolution = (monitor.width, monitor.height)
            monitor_dimensions = (monitor.width_mm, monitor.height_mm)

    local_fps = display_dot_and_record(display_resolution, capture_resolution, config["calibration"], save_collection_to, path_step=5)

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

    print(f"Session ID:{session_id}")
    video_client.sendall(session_id.to_bytes(4, 'big')) 
    

    video_client.sendall(local_fps.to_bytes(4, 'big'))
    
    remote_fps = int.from_bytes(video_client.recv(4), 'big')
    print(f"Received FPS from remote: {remote_fps}")

    with open(f"{save_collection_to}/general_info.txt", "w") as file:
        file.write(f"session ID: {session_id}\n")
        file.write(f"local fps: {local_fps}\n")
        file.write(f"remote fps: {remote_fps}\n")
        file.write(f"display resolution: {display_resolution[0]}X{display_resolution[1]}\n")
        file.write(f"monitor dimensions in mm: {monitor_dimensions[0]}x{monitor_dimensions[1]}") 

    # Start send/receive processes
    send_receive_and_save(audio_client, video_client, local_fps, remote_fps, save_collection_to, config["width"], config["height"])

    # Close connections
    video_client.close()
    audio_client.close()
    video_socket.close()
    audio_socket.close()

if __name__ == "__main__":
    main()

