import socket
import pyaudio
import multiprocessing

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

def audio_record(audio_queue):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    while True:
        data = stream.read(CHUNK)
        

def send_audio(audio_queue, socket):
    while True:
        audio_data = audio_queue.get()
        socket.send(audio_data)


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create client socket
    try:
        client_socket.connect((read_ip(), 8080))  # Replace 'server_ip_here' with actual server IP
        print("Connected to the server")
    except Exception as e:
        print(f"Connection failed: {e}")
        exit(1)

    audio_queue = multiprocessing.Queue()

    record_proccess = multiprocessing.Process(target=audio_record, args=(audio_queue))
    send_process = multiprocessing.Process(target=send_audio, args=(audio_queue, client_socket))

    record_proccess.start()
    send_process.start()

    record_proccess.join()
    send_process.join()

if __name__ == "__main__":
    main()

