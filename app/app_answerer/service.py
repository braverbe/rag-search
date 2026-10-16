import ollama
from fastapi import Depends

from app import get_vector_storage
from app.utils.storage import VectorStore
from app.utils.settings import settings

class AnswererService:
    def __init__(self, vector_storage: VectorStore) -> None:
        self._vector_storage = vector_storage

    def _get_answer(self, question: str):
        self._vector_storage.load(settings.articles_placefolder_path)

        results = self._vector_storage.search(question, top_k=5)

        return results

    def get_answer(self, question: str) -> str:
        results = self._get_answer(question=question)

        context = "\n\n---\n\n".join(
            f"[{i + 1}] {r.text[:200]}\nИсточник: {r.metadata['url']}"
            for i, r in enumerate(results)
        )

        prompt = f"""Ответь на вопрос, опираясь только на фрагменты ниже.
        Если ответа в них нет, так и скажи. Указывай ссылки на источники.

        {context}

        Вопрос: {question}"""

        return ollama.chat(
            model=settings.answer_model,
            messages=[{"role": "user", "content": prompt}],
            think=False,
        ).message.content


def get_answer_service(
    vector_storage: VectorStore = Depends(get_vector_storage)
) -> AnswererService:
    return AnswererService(vector_storage=vector_storage)