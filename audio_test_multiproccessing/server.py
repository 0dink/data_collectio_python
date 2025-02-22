import socket
import pyaudio
import struct
import multiprocessing


# PyAudio setup
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

def receive_audio(socket, address):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True)

    with socket:
        print('Connected by', address)
        while True:
            size_data = socket.recv(4)
            number_size = struct.unpack("!I", size_data)[0]  
            audio_data = socket.recv(2048)

            number_data = b""
            while len(number_data) < number_size:
                packet = socket.recv(number_size - len(number_data))
                if not packet:
                    break
                number_data += packet

            print(len(number_data))
            stream.write(audio_data)

    socket.close()

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

    receive_process = multiprocessing.Process(target=receive_audio, args=(client_socket, client_address,))

    receive_process.start()

if __name__ == "__main__":
    main()

