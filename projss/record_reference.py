import sounddevice as sd
from scipy.io.wavfile import write

fs = 16000  # 16,000 samples per second — needed for best quality
seconds = 5  # Record for 5 seconds, you can change if you want

print("Please speak *now* to record your reference voice...")
recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')  # mono, 16kHz
sd.wait()  # Wait until done
write('my_voice_sample.wav', fs, recording)
print("Voice sample saved as my_voice_sample.wav")
