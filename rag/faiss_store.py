import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class FAISSVectorStore:

    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.documents = []
        self.index = None

    def build(self, documents):

        self.documents = documents

        texts = [
            doc.page_content if hasattr(doc, "page_content")
            else str(doc)
            for doc in documents
        ]

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True
        ).astype("float32")

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(dimension)

        self.index.add(embeddings)

    def search(self, query, k=5):

        if self.index is None:
            return []

        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True
        ).astype("float32")

        distances, indices = self.index.search(
            query_embedding,
            k
        )

        results = []

        for idx in indices[0]:

            if idx == -1:
                continue

            results.append(self.documents[idx])

        return results