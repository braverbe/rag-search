import pickle

import numpy as np

from app.utils import get_embedding
from app.utils.models import AnswerResponse
from app.utils.utils import matches_filter



class VectorStore:
    def __init__(self):
        self.chunks = []
        self.embeddings = []
        self.metadata = []

    def add(
        self,
        text: str,
        embedding: list[float],
        metadata: dict|None = None
    ) -> None:
        """Добавить один чанк в хранилище"""
        self.chunks.append(text)
        self.embeddings.append(embedding)
        self.metadata.append(metadata if metadata else {})

    def add_text(
        self,
        text: str,
        metadata: dict|None = None
    ) -> None:
        """Создать эмбединги"""
        embedding = get_embedding(
            f"search_document: {text}"
        )
        self.add(text, embedding, metadata)

    def save(self, path: str):
        data = {
            "chunks": self.chunks,
            "embeddings": self.embeddings,
            "metadata": self.metadata
        }
        with open(path, "wb") as f:
            pickle.dump(data, f)

    def load(self, path: str):
        with open(path, "rb") as f:
            data = pickle.load(f)
            self.chunks = data["chunks"]
            self.embeddings = data["embeddings"]
            self.metadata = data["metadata"]

    def search(
        self,
        query_text: str,
        top_k: int = 3,
        score_threshold: float = 0.0,
        filter_metadata: dict = None,
    ) -> list[dict]:
        """Найти top_k чанков, наиболее похожих на query_text"""
        if not self.embeddings:
            return []

        query_embedding = get_embedding(
            f"search_query: {query_text}"
        )

        if filter_metadata is None:
            valid_indices = list(range(len(self.chunks)))
        else:
            valid_indices = [
                i for i in range(len(self.chunks))
                    if matches_filter(self.metadata[i], filter_metadata)
            ]

        if not valid_indices:
            return []

        matrix = np.array([self.embeddings[i] for i in valid_indices])
        query = np.array(query_embedding)

        # Формула косинусного сходства
        dot_products = matrix @ query
        norms = np.linalg.norm(matrix, axis=1) * np.linalg.norm(query)
        similarities = dot_products / norms

        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            real_idx = valid_indices[idx]
            score = float(similarities[idx])
            if score < score_threshold:
                continue
            results.append(
                AnswerResponse(
                    text=self.chunks[real_idx],
                    score=score,
                    metadata=self.metadata[real_idx],
                )
            )
        return results


def get_vector_storage() -> VectorStore:
    return VectorStore()
