import numpy as np
import time

class EnergySegmenter:
    """
    Πολύ απλό segmentation για αρχή:
    - μετρά RMS ενέργεια
    - όταν περάσει threshold -> "speech"
    - όταν πέσει για λίγο -> κλείνει segment
    """
    def __init__(self, sample_rate=16000, rms_threshold=0.015, min_speech_s=0.6, silence_end_s=0.4, max_segment_s=3.0):
        self.sr = sample_rate
        self.th = rms_threshold
        self.min_speech_s = min_speech_s
        self.silence_end_s = silence_end_s
        self.max_segment_s = max_segment_s

        self.buf = []
        self.in_speech = False
        self.speech_start_t = None
        self.last_loud_t = None

    def _rms(self, x):
        return float(np.sqrt(np.mean(x * x) + 1e-12))

    def push_block(self, block):
        now = time.time()
        rms = self._rms(block)

        if rms >= self.th:
            self.last_loud_t = now
            if not self.in_speech:
                self.in_speech = True
                self.speech_start_t = now
                self.buf = []
            self.buf.append(block)
        else:
            if self.in_speech:
                self.buf.append(block)

        # conditions to close segment
        if self.in_speech:
            dur = now - self.speech_start_t
            silence = (now - self.last_loud_t) if self.last_loud_t else 0.0

            if dur >= self.max_segment_s or silence >= self.silence_end_s:
                self.in_speech = False
                audio = np.concatenate(self.buf, axis=0)
                self.buf = []
                if dur >= self.min_speech_s:
                    return audio
        return None
 