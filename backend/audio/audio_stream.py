
import random
import threading
import time

class FakeAudioStream:
    """
    Fake simulator:
    - περιμένει λίγο
    - επιλέγει τυχαίο speaker
    - για X δευτερόλεπτα τον "κάνει να μιλάει" καλώντας callback(speaker_id)
    """
    def __init__(self, speaker_ids):
        self.speaker_ids = speaker_ids
        self.running = False
        self.thread = None

    def start(self, callback):
        if self.running:
            return
        self.running = True

        def run():
            while self.running:
                # silence
                time.sleep(random.uniform(0.5, 1.5))

                # pick someone to talk
                speaker = random.choice(self.speaker_ids)
                duration = random.uniform(0.8, 2.5)
                start = time.time()

                while self.running and (time.time() - start) < duration:
                    callback(speaker)
                    time.sleep(0.1)

        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
