import sounddevice as sd
from scipy.io.wavfile import write

fs = 16000  # Sample rate
duration = 5  # seconds

print("Please speak now to create 'temp_test.wav'...")
recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
sd.wait()
write("temp_test.wav", fs, recording)
print("Recording saved as 'temp_test.wav'. You can now use it for testing.")
