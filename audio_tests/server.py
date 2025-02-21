import socket
import pyaudio

# PyAudio setup
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

def main():
    # Initialize server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind(('0.0.0.0', 8080))
    server_socket.listen(10)
    print("Server listening on port 8080...")

    # Accept a client connection
    client_socket, client_address = server_socket.accept()
    print(f"Connection established with {client_address}")

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True)

    with client_socket:
        print('Connected by', client_address)
        while True:
            data = client_socket.recv(CHUNK * 2)
            if not data:
                break
            stream.write(data)

    client_socket.close()
    server_socket.close()

if __name__ == "__main__":
    main()

