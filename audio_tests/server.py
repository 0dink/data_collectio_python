import socket
import pyaudio

# Server setup
HOST = '127.0.0.1'  # Listen on all interfaces
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

# PyAudio setup
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True)

# Socket setup
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server listening on {HOST}:{PORT}")
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(CHUNK * 2)
            if not data:
                break
            stream.write(data)

stream.stop_stream()
stream.close()
audio.terminate()