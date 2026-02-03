import numpy as np
from resemblyzer import VoiceEncoder

class SpeakerEmbedder:
    def __init__(self):
        self.encoder = VoiceEncoder()

    def embed(self, audio_float32_16khz: np.ndarray):
        # resemblyzer expects float waveform at 16k
        if audio_float32_16khz.dtype != np.float32:
            audio_float32_16khz = audio_float32_16khz.astype(np.float32)
        return self.encoder.embed_utterance(audio_float32_16khz)
