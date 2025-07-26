import os
import numpy as np
from resemblyzer import VoiceEncoder, preprocess_wav

class VoiceAuthenticator:
    def __init__(self, reference_audio_path: str, threshold: float = 0.75):
        """
        Initialize with a voice sample and similarity threshold.

        :param reference_audio_path: Path to WAV file of your enrolled voice.
        :param threshold: Cosine similarity threshold (default 0.75) to accept a voice as yours.
        """
        if not os.path.exists(reference_audio_path):
            raise FileNotFoundError(f"Reference audio file not found: {reference_audio_path}")
        
        self.threshold = threshold
        self.encoder = VoiceEncoder()
        self.ref_embedding = self._embed_audio(reference_audio_path)

    def _embed_audio(self, audio_path: str) -> np.ndarray:
        """
        Process WAV audio and extract embedding vector.

        :param audio_path: Path to WAV file.
        :return: Normalized embedding vector of shape (d,)
        """
        wav = preprocess_wav(audio_path)
        return self.encoder.embed_utterance(wav)

    def is_my_voice(self, test_audio_path: str) -> bool:
        """
        Check if the test audio matches the enrolled voice.

        :param test_audio_path: Path to test WAV file to check.
        :return: True if similarity >= threshold; False otherwise.
        """
        if not os.path.exists(test_audio_path):
            print(f"Test audio file not found: {test_audio_path}")
            return False

        try:
            test_embedding = self._embed_audio(test_audio_path)
            # Compute cosine similarity
            similarity = float(
                np.dot(self.ref_embedding, test_embedding) /
                (np.linalg.norm(self.ref_embedding) * np.linalg.norm(test_embedding))
            )
            print(f"[VoiceAuthenticator] Cosine similarity: {similarity:.4f} (Threshold: {self.threshold})")
            return similarity >= self.threshold
        except Exception as e:
            print(f"[VoiceAuthenticator] Error during voice verification: {e}")
            return False
