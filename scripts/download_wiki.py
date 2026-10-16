"""
Скачивает случайные статьи из Википедии в виде чистого текста для RAG.

Пример:
    python scripts/download_wiki.py --count 100 --lang ru --out data/wiki
"""
import argparse
import json
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

USER_AGENT = "rag-dataset-downloader/1.0 (educational project)"

try:
    import certifi
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CONTEXT = ssl.create_default_context()


def api_get(lang: str, params: dict) -> dict:
    params = {**params, "format": "json", "formatversion": "2"}
    url = f"https://{lang}.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=30, context=SSL_CONTEXT) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            if e.code != 429 and e.code < 500:
                raise
            delay = int(e.headers.get("Retry-After") or 2 ** (attempt + 1))
            print(f"  HTTP {e.code}, жду {delay} с...")
            time.sleep(delay)
    raise RuntimeError(f"Не удалось получить {url}")


def random_titles(lang: str, n: int) -> list[str]:
    data = api_get(lang, {
        "action": "query",
        "list": "random",
        "rnnamespace": 0,
        "rnlimit": n,
    })
    return [p["title"] for p in data["query"]["random"]]


def fetch_article(lang: str, title: str) -> dict | None:
    data = api_get(lang, {
        "action": "query",
        "prop": "extracts|info",
        "explaintext": 1,
        "exsectionformat": "plain",
        "inprop": "url",
        "redirects": 1,
        "titles": title,
    })
    page = data["query"]["pages"][0]
    if page.get("missing"):
        return None
    return {
        "id": page["pageid"],
        "title": page["title"],
        "url": page["fullurl"],
        "text": page.get("extract", "").strip(),
    }


def safe_filename(title: str) -> str:
    return re.sub(r'[\\/:*?"<>|\s]+', "_", title).strip("_")[:100]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--lang", default="ru")
    parser.add_argument("--min-chars", type=int, default=2000,
                        help="пропускать слишком короткие статьи-заготовки")
    parser.add_argument("--out", default="data/wiki")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    meta_path = out_dir / "articles.jsonl"
    articles = []
    if meta_path.exists():
        articles = [json.loads(line) for line in meta_path.open(encoding="utf-8")]
        print(f"Уже скачано: {len(articles)}")
    seen = {a["title"] for a in articles}

    while len(articles) < args.count:
        for title in random_titles(args.lang, 50):
            if len(articles) >= args.count or title in seen:
                continue
            seen.add(title)
            article = fetch_article(args.lang, title)
            time.sleep(1)
            if article is None or len(article["text"]) < args.min_chars:
                continue
            articles.append(article)
            path = out_dir / f"{article['id']}_{safe_filename(article['title'])}.txt"
            path.write_text(article["text"], encoding="utf-8")
            with meta_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(article, ensure_ascii=False) + "\n")
            print(f"[{len(articles)}/{args.count}] {article['title']} ({len(article['text'])} симв.)")

    print(f"Готово: {len(articles)} статей в {out_dir}")


if __name__ == "__main__":
    main()
