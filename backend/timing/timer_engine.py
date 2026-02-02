import time
import threading

class TimerEngine:
    def __init__(self, speaker_ids):
        self.lock = threading.Lock()
        self.speakers = {sid: 0.0 for sid in speaker_ids}
        self.last_update = {sid: None for sid in speaker_ids}
        self.active = None

    def on_speech(self, speaker_id: int):
        now = time.time()
        with self.lock:
            self.active = speaker_id
            last = self.last_update.get(speaker_id)
            if last is None:
                self.last_update[speaker_id] = now
                return
            self.speakers[speaker_id] += (now - last)
            self.last_update[speaker_id] = now

    def get_status(self):
        with self.lock:
            return {
                "times": {str(k): round(v, 1) for k, v in self.speakers.items()},
                "active": self.active
            }

