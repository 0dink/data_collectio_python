import socket
import pyaudio
import struct
import multiprocessing
import random

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

def read_ip():
    try:
        return open("../inputs/server_ip.txt", "r").readline()
    except Exception as e:
        print("getting IP: {e}")
        exit(1)

def generate_random_number(number_queue):
    try: 
        print("random number start")
        while True:
            number_queue.put([0] * 2000)
    except Exception as e:
        print(f"generating random number: {e}")

def audio_record(audio_queue):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    while True:
        audio_data = stream.read(CHUNK)
        audio_queue.put(audio_data)
        
def send_audio_number(number_queue, audio_queue, socket):    
    while True:
        audio_data = audio_queue.get()
        number_data = bytes(number_queue.get())
        packet = struct.pack("!T", len(number_data)) + audio_data + number_data
        socket.sendall(packet)
        
def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create client socket
    try:
        client_socket.connect((read_ip(), 8080))  # Replace 'server_ip_here' with actual server IP
        print("Connected to the server")
    except Exception as e:
        print(f"Connection failed: {e}")
        exit(1)

    audio_queue = multiprocessing.Queue()
    number_queue = multiprocessing.Queue()

    record_process = multiprocessing.Process(target=audio_record, args=(audio_queue,))
    random_number_process = multiprocessing.Process(target=generate_random_number, args=(number_queue,))
    send_process = multiprocessing.Process(target=send_audio_number, args=(number_queue, audio_queue, client_socket,))

    record_process.start()
    random_number_process.start()
    send_process.start()

    record_process.join()
    random_number_process.join()
    send_process.join()

if __name__ == "__main__":
    main()

