from auth import VoiceAuthenticator

auth = VoiceAuthenticator("my_voice_sample.wav", threshold=0.75)

# Replace "temp_test.wav" with your test audio file path
result = auth.is_my_voice("temp_test.wav")

if result:
    print("Voice authenticated! This is you.")
else:
    print("Voice NOT recognized.")
