from config import RAG_TOP_K

from rag.documents import build_documents
from rag.embeddings import LocalEmbedder
from rag.vector_store import VectorStore


class SchemaRetriever:

    def __init__(self):

        print("[RAG] Initializing Schema Retriever...")

        self.store = VectorStore()
        self.embedder = LocalEmbedder()

        # Build / refresh the schema index
        self.refresh()

    # =========================================================
    # REFRESH / INDEX DATABASE SCHEMA
    # =========================================================

    def refresh(self):

        documents = build_documents()

        if not documents:
            raise RuntimeError(
                "No database schema documents were created.\n\n"
                "Check your database connection and make sure "
                "your PostgreSQL database contains tables."
            )

        self.store.build(
            documents,
            self.embedder
        )

        print(
            f"[RAG] Indexed {len(documents)} "
            f"schema documents."
        )

    # =========================================================
    # RETRIEVE RELEVANT SCHEMA
    # =========================================================

    def retrieve(self, question, top_k=None):

        if not question or not question.strip():
            return []

        k = top_k if top_k is not None else RAG_TOP_K

        results = self.store.search(
            question,
            k
        )

        if not results:

            print(
                "[RAG] WARNING: "
                "No schema documents retrieved."
            )

            return []

        valid_results = []

        for item in results:

            if not isinstance(item, dict):
                continue

            text = item.get("text")

            if not text or not text.strip():
                continue

            valid_results.append(item)

        print(
            f"[RAG] Retrieved "
            f"{len(valid_results)} schema documents."
        )

        return valid_results

    # =========================================================
    # FORMAT RAG CONTEXT
    # =========================================================

    @staticmethod
    def format_context(results):

        if not results:
            return ""

        context_parts = []

        for item in results:

            text = item.get(
                "text",
                ""
            ).strip()

            if not text:
                continue

            score = item.get(
                "score",
                0.0
            )

            context_parts.append(
                f"{text}\n"
                f"RETRIEVAL SCORE: {score:.4f}"
            )

        return "\n\n".join(
            context_parts
        )