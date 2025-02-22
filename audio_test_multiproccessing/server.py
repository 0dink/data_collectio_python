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
            sizes_data = socket.recv(8)


            if not sizes_data:
                break

            number_size, audio_size = struct.unpack("!II", sizes_data)

            number_data = b""
            while len(number_data) < number_size:
                packet = socket.recv(number_size - len(number_data))
                if not packet:
                    break
                number_data += packet
            
            # Receive audio data
            audio_data = b""
            while len(audio_data) < audio_size:
                packet = socket.recv(audio_size - len(audio_data))
                if not packet:
                    break
                audio_data += packet

            print(number_data)
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

