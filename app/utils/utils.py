import requests
from app.utils.settings import settings

def get_embedding(text: str) -> list[float]:
    response = requests.post(
        settings.embedding_link,
        json={"model": settings.embedding_model, "prompt": text}
    )
    return response.json()["embedding"]

def matches_filter(metadata: dict, filter_metadata: dict) -> bool:
    for key, value in filter_metadata.items():
        if metadata.get(key) != value:
            return False
    return True

