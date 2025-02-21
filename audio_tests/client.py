import socket
import pyaudio


FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

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

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    while True:
        data = stream.read(CHUNK)
        client_socket.sendall(data)

if __name__ == "__main__":
    main()
