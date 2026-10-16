import json

from fastapi import APIRouter

from app.utils.storage import get_vector_storage
from app.app_rag.chunker import Chunker

from app.utils.settings import settings

router = APIRouter(prefix="/train")


@router.post("")
def main():
    chunker = Chunker()
    store = get_vector_storage()


    with open(settings.articles_json_path, encoding="utf-8") as f:
        for line in f:
            article = json.loads(line)
            for i, chunk in enumerate(chunker.split_into_chunks(article["text"], chunk_size=800, overlap=100)):
                store.add_text(
                    f"{article['title']}\n\n{chunk}",
                    metadata={"title": article["title"], "url": article["url"], "chunk": i},
                )
            print(article["title"])

    store.save(settings.articles_placefolder_path)
    return {"chunks": len(store.chunks)}


if __name__ == "__main__":
    main()