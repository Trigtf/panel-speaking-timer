import numpy as np
import sounddevice as sd
import queue

class MicStream:
    def __init__(self, sample_rate=16000, block_ms=30):
        self.sample_rate = sample_rate
        self.block_size = int(sample_rate * block_ms / 1000)
        self.q = queue.Queue()

    def _callback(self, indata, frames, time_info, status):
        if status:
            # ignore for now
            pass
        # indata shape: (frames, channels). Use mono:
        mono = indata[:, 0].copy()
        self.q.put(mono)

    def start(self):
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            blocksize=self.block_size,
            dtype="float32",
            callback=self._callback
        )
        self.stream.start()

    def read_block(self, timeout=1.0):
        return self.q.get(timeout=timeout)

    def stop(self):
        if hasattr(self, "stream"):
            self.stream.stop()
            self.stream.close()
