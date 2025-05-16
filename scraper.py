import os
import sys
import json
import logging
from urllib.parse import urlparse
from newspaper import Article

# CONFIG
RAW_FOLDER  = "raw-articles"
URLS_FILE   = sys.argv[1] if len(sys.argv) > 1 else "urls.txt"
FAIL_FILE   = "failed_urls.txt"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)

def scrape_and_save(url):
    logging.info(f"🔍 Scraping {url}")
    article = Article(url)
    article.download()
    article.parse()

    data = {
        "url":             url,
        "title":           article.title,
        "authors":         article.authors,
        "publication_date": (
            article.publish_date.isoformat() if article.publish_date else None
        ),
        "text":            article.text
    }

    # build a filename that’s unlikely to collide
    parsed    = urlparse(url)
    slug      = parsed.path.strip("/").replace("/", "_") or "root"
    safe_name = f"{parsed.netloc.replace('.', '_')}_{slug}.json"

    os.makedirs(RAW_FOLDER, exist_ok=True)
    out_path = os.path.join(RAW_FOLDER, safe_name)

    with open(out_path, "w") as f:
        json.dump(data, f)
    logging.info(f"💾 Saved {out_path}")

def main():
    with open(URLS_FILE) as f:
        urls = [u.strip() for u in f if u.strip()]

    failures = []
    for url in urls:
        try:
            scrape_and_save(url)
        except Exception as e:
            logging.error(f"❌ Failed {url}: {e}")
            failures.append(url)

    # write failed URLs
    if failures:
        with open(FAIL_FILE, "w") as f:
            f.write("\n".join(failures))
        logging.info(f"⚠️  {len(failures)} URLs failed; see {FAIL_FILE}")

    total = len(urls)
    success = total - len(failures)
    logging.info(f"🏁 Done. {success}/{total} succeeded, {len(failures)} failed.")

if __name__ == "__main__":
    main()
