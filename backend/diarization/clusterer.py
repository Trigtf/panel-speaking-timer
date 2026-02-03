import numpy as np

def cosine_sim(a, b):
    a = a / (np.linalg.norm(a) + 1e-9)
    b = b / (np.linalg.norm(b) + 1e-9)
    return float(np.dot(a, b))

class OnlineClusterer:
    """
    Κρατάει centroids για speakers.
    Αν το νέο embedding ταιριάζει αρκετά με centroid -> ίδιο speaker.
    Αλλιώς δημιουργεί νέο speaker (μέχρι max_speakers).
    """
    def __init__(self, max_speakers=6, match_threshold=0.72):
        self.max_speakers = max_speakers
        self.th = match_threshold
        self.centroids = []  # list[np.ndarray]
        self.counts = []     # how many updates per centroid

    def assign(self, emb: np.ndarray):
        if len(self.centroids) == 0:
            self.centroids.append(emb.copy())
            self.counts.append(1)
            return 1  # speaker id (1-based)

        sims = [cosine_sim(emb, c) for c in self.centroids]
        best_i = int(np.argmax(sims))
        best = sims[best_i]

        if best >= self.th:
            # update centroid (running mean)
            n = self.counts[best_i]
            self.centroids[best_i] = (self.centroids[best_i] * n + emb) / (n + 1)
            self.counts[best_i] = n + 1
            return best_i + 1

        if len(self.centroids) < self.max_speakers:
            self.centroids.append(emb.copy())
            self.counts.append(1)
            return len(self.centroids)

        # fallback: force best match
        return best_i + 1
