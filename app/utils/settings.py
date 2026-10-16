from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    embedding_model: str = "bge-m3"
    answer_model: str = "qwen3"

settings = Settings()