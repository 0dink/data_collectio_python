import socket

from screeninfo import get_monitors

from utilities.video_utils import send_receive_and_save
from utilities.io_utils import create_collection_folder, read_config
from utilities.calibration_utils import display_dot_and_record

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
    
    capture_resolution = (config["width"], config["height"])
        
    for monitor in get_monitors():
        if monitor.is_primary:
            display_resolution = (monitor.width, monitor.height)
            monitor_dimensions = (monitor.width_mm, monitor.height_mm)

    with open(f"{save_collection_to}/general_info.txt", "w") as file:
        file.write(f"display resolution: {display_resolution}")
        file.write(f"monitor dimensions: {monitor_dimensions}")

    local_fps = display_dot_and_record(display_resolution, capture_resolution, config["calibration"], save_collection_to, path_step=5)
    
    ####################
    # connection stuff #
    ####################
    
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

    session_id = int.from_bytes(video_socket.recv(4), 'big')
    print(f"Received unique ID: {session_id}")

    remote_fps = int.from_bytes(video_socket.recv(4), 'big')
    print(f"Received FPS from server: {remote_fps}")

    video_socket.sendall(round(local_fps).to_bytes(4, 'big'))

    with open(f"{save_collection_to}/general_info.txt", "w") as file:
        file.write(f"session ID: {session_id}\n")
        file.write(f"local fps: {local_fps}\n")
        file.write(f"remote fps: {remote_fps}\n")
        file.write(f"display resolution: {display_resolution[0]}X{display_resolution[1]}\n")
        file.write(f"monitor dimensions in mm: {monitor_dimensions[0]}x{monitor_dimensions[1]}") 

    send_receive_and_save(audio_socket, video_socket, local_fps, remote_fps, save_collection_to, config["width"], config["height"],)

    # Close sockets
    video_socket.close()
    audio_socket.close()

if __name__ == "__main__":
    main()
