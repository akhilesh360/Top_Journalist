import os
import json
import re
from glob import glob

import openai
import faiss
import numpy as np

# ── Load OpenAI API key ──
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise RuntimeError("OPENAI_API_KEY not set in environment")

# CONFIG
RAW_FOLDER   = "raw-articles"
INDEX_PATH   = "journalist.index"
META_PATH    = "metadata.jsonl"
EMBED_MODEL  = "text-embedding-ada-002"

# Full list of 50 topic labels
TOPIC_LABELS = [
    "AI","Machine Learning","Data Science","Crypto","Blockchain",
    "Cybersecurity","Big Data","FinTech","IoT","Cloud Computing",
    "NLP","Robotics","Computer Vision","Virtual Reality","Augmented Reality",
    "5G","Quantum Computing","DevOps","Edge Computing","Autonomous Vehicles",
    "Biotech","Health Tech","Renewable Energy","Smart Cities","Digital Marketing",
    "E-commerce","Social Media","Gaming","Entertainment Tech","EdTech",
    "Legal Tech","GovTech","MarTech","InsurTech","HR Tech",
    "RegTech","AdTech","Sport Tech","AgriTech","NanoTech",
    "Clean Tech","Space Tech","Satellite Tech","Wearables","Chatbots",
    "Voice Assistants","Genetic Engineering","Drug Discovery","Telemedicine","Precision Medicine"
]

def embed_text(text: str) -> np.ndarray:
    """Get embedding for up to 2000 chars of text."""
    resp = openai.Embedding.create(model=EMBED_MODEL, input=text[:2000])
    return np.array(resp["data"][0]["embedding"], dtype=np.float32)


def detect_topic(text: str, url: str) -> str:
    """
    Use URL patterns first, then keyword matching via regex on text.
    """
    u = url.lower()
    # URL-based hints
    if re.search(r"tag/data-science|datasciencecentral|towardsdatascience", u):
        return "Data Science"
    if re.search(r"tag/blockchain|cointelegraph.com|decrypt.co", u):
        return "Blockchain"
    if re.search(r"coindesk.com.*crypto|\bcrypto\b", u):
        return "Crypto"

    # Text-based regex matching for each label
    for label in TOPIC_LABELS:
        # word-boundary, case-insensitive
        pattern = re.compile(rf"\b{re.escape(label.lower())}\b", re.IGNORECASE)
        if pattern.search(text.lower()):
            return label
    return "Other"


def main():
    files = glob(f"{RAW_FOLDER}/*.json")
    if not files:
        print(f"No files in {RAW_FOLDER}. Run the scraper first.")
        return

    embeddings = []
    metadata   = []

    for fp in files:
        doc  = json.load(open(fp))
        text = doc.get("text", "")
        url  = doc.get("url", "")
        vec  = embed_text(text)
        embeddings.append(vec)

        topic_label  = detect_topic(text, url)
        authors      = doc.get("authors") or []
        first_author = authors[0].strip() if authors else ""

        metadata.append({
            "journalist": first_author,
            "url":         url,
            "topic":       topic_label
        })

    # Build and save FAISS index
    embeddings = np.stack(embeddings)
    dim        = embeddings.shape[1]
    index      = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    faiss.write_index(index, INDEX_PATH)
    print(f"✅ FAISS index saved to {INDEX_PATH}")

    # Write metadata aligned with index vectors
    with open(META_PATH, "w") as f:
        for m in metadata:
            f.write(json.dumps(m) + "\n")
    print(f"✅ Metadata written to {META_PATH}")


if __name__ == "__main__":
    main()
