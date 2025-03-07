import pyaudio

# Parameters
CHUNK = 1024  # Number of frames per buffer
FORMAT = pyaudio.paInt16  # 16-bit format
CHANNELS = 1  # Mono input
RATE = 44100  # Sampling rate

def mic_playback():
    """Plays the microphone input back in real time."""
    p = pyaudio.PyAudio()
    
    # Open input stream
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    output=True,  # Enable output to play the audio
                    frames_per_buffer=CHUNK)
    
    print("Mic playback started. Press Ctrl+C to stop.")
    try:
        while True:
            data = stream.read(CHUNK)
            stream.write(data)  # Playback
    except KeyboardInterrupt:
        print("\nStopping playback.")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    mic_playback()