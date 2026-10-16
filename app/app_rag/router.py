import json

from app.VectorStorage import get_embedding, VectorStore
from app.chunker import Chunker
import ollama

from app.utils.settings import settings


def main():
    chunker = Chunker()
    MODEL = "bge-m3"
    store = VectorStore(embed_model=MODEL)


    with open(settings.articles_json_path, encoding="utf-8") as f:
        for line in f:
            article = json.loads(line)
            for i, chunk in enumerate(chunker.split_into_chunks(article["text"], chunk_size=800, overlap=100)):
                store.add_text(
                    f"{article['title']}\n\n{chunk}",
                    metadata={"title": article["title"], "url": article["url"], "chunk": i},
                )
            print(article["title"])

    store.save(settings.articles_place_path)


if __name__ == "__main__":
    main()