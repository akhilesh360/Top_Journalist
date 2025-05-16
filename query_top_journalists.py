import os
import sys
import json

import openai
import faiss
import numpy as np
from collections import Counter

# ── Load OpenAI API key ──
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise RuntimeError("OPENAI_API_KEY not set in environment")

# CONFIG
INDEX_PATH  = "journalist.index"
META_PATH   = "metadata.jsonl"
EMBED_MODEL = "text-embedding-ada-002"
SEARCH_K    = 500   # neighbors to fetch before filtering

# Load FAISS index and metadata
index    = faiss.read_index(INDEX_PATH)
metadata = [json.loads(line) for line in open(META_PATH)]

def embed_query(text: str) -> np.ndarray:
    """Return embedding for the query text."""
    resp = openai.Embedding.create(model=EMBED_MODEL, input=text[:2000])
    return np.array(resp["data"][0]["embedding"], dtype=np.float32)

def top_journalists(topic: str, k: int = 5):
    # 1) Embed the topic prompt
    q_emb = embed_query(topic + " news headlines")
    # 2) Find nearest neighbors
    _, ids = index.search(np.expand_dims(q_emb, axis=0), SEARCH_K)
    # 3) Strict filter by topic label & non-empty author
    hits = [
        metadata[i]["journalist"]
        for i in ids[0]
        if metadata[i].get("topic") == topic
        and metadata[i].get("journalist")
    ]
    # 4) Fallback if no strict matches
    if not hits:
        hits = [
            metadata[i]["journalist"]
            for i in ids[0]
            if metadata[i].get("journalist")
        ]
    return Counter(hits).most_common(k)

def main():
    if len(sys.argv) < 2:
        print("Usage: python query_top_journalists.py <topic> [k]")
        sys.exit(1)

    topic = sys.argv[1]
    k     = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    results = top_journalists(topic, k)
    print(f"\nTop {k} journalists for “{topic}”:")
    for rank, (journalist, cnt) in enumerate(results, start=1):
        print(f"{rank}. {journalist} — {cnt} mentions")

if __name__ == "__main__":
    main()
