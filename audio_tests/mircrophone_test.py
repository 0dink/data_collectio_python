import pyaudio
import wave

# Parameters
CHUNK = 1024  # Number of frames per buffer
FORMAT = pyaudio.paInt16  # 16-bit format
CHANNELS = 1  # Mono input
RATE = 44100  # Sampling rate
OUTPUT_FILENAME = "mic_playback_record.wav"

def mic_playback():
    """Plays the microphone input back in real time and saves it to a file."""
    p = pyaudio.PyAudio()
    
    # Open input stream
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    output=True,  # Enable output to play the audio
                    frames_per_buffer=CHUNK)
    
    frames = []  # List to store audio frames
    
    print("Mic playback started. Press Ctrl+C to stop.")
    try:
        while True:
            data = stream.read(CHUNK)
            stream.write(data)  # Playback
            frames.append(data)
    except KeyboardInterrupt:
        print("\nStopping playback and saving audio.")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Save the recorded audio
        wf = wave.open(OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        print(f"Audio saved as {OUTPUT_FILENAME}")

if __name__ == "__main__":
    mic_playback()
