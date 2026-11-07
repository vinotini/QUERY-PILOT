from sentence_transformers import SentenceTransformer


class LocalEmbedder:

    def __init__(self):

        print(
            "[EMBEDDINGS] Loading "
            "all-MiniLM-L6-v2..."
        )

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    # =========================================================
    # EMBED DOCUMENTS
    # =========================================================

    def fit(self, texts):

        return self.model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True
        )

    # =========================================================
    # EMBED QUERY
    # =========================================================

    def transform(self, texts):

        return self.model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True
        )