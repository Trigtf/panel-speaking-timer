from backend.diarization.mic_stream import MicStream
from backend.diarization.segmenter import EnergySegmenter
from backend.diarization.embedder import SpeakerEmbedder
from backend.diarization.clusterer import OnlineClusterer

class DiarizationEngine:
    def __init__(self, on_speaker_callback):
        self.on_speaker = on_speaker_callback

        self.mic = MicStream(sample_rate=16000, block_ms=30)
        self.seg = EnergySegmenter(sample_rate=16000)
        self.emb = SpeakerEmbedder()
        self.clu = OnlineClusterer(max_speakers=6, match_threshold=0.72)

        self.running = False

    def start(self):
        self.running = True
        self.mic.start()

        while self.running:
            block = self.mic.read_block()
            segment = self.seg.push_block(block)
            if segment is not None:
                e = self.emb.embed(segment)
                spk_id = self.clu.assign(e)
                # notify timing engine
                self.on_speaker(spk_id)

    def stop(self):
        self.running = False
        self.mic.stop()
