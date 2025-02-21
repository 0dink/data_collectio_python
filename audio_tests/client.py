import socket
import pyaudio

# Client setup
HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

# PyAudio setup
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

# Socket setup
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print(f"Connected to {HOST}:{PORT}")
    while True:
        data = stream.read(CHUNK)
        s.sendall(data)

stream.stop_stream()
stream.close()
audio.terminate()