import os
import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class VectorStore:
    def __init__(self, path="rag_index/store.pkl"):
        self.path = path
        self.documents = []
        self.matrix = None
        self.embedder = None

    def build(self, documents, embedder):
        directory = os.path.dirname(self.path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        self.documents = documents
        self.embedder = embedder
        self.matrix = embedder.fit([d["text"] for d in documents])
        self.save()

    def save(self):
        with open(self.path, "wb") as f:
            pickle.dump(
                {
                    "documents": self.documents,
                    "matrix": self.matrix,
                    "embedder": self.embedder
                },
                f
            )

    def search(self, query, top_k):
        if self.matrix is None or self.embedder is None:
            return []
        query_vector = self.embedder.transform([query])
        scores = cosine_similarity(query_vector, self.matrix)[0]
        indexes = np.argsort(scores)[::-1][:top_k]
        return [
            {**self.documents[i], "score": float(scores[i])}
            for i in indexes
            if scores[i] > 0
        ]
