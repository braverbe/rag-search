from pydantic import HttpUrl
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    embedding_model: str = "bge-m3"
    embedding_link: HttpUrl = "http://localhost:11434/api/embeddings"
    answer_model: str = "qwen3"

    articles_json_path: str = "data/wiki/articles.jsonl"
    articles_placefolder_path: str = "data/wiki_index.pkl"

settings = Settings()