# inspect_topics.py
import json
from collections import Counter

# Read your metadata file
with open("metadata.jsonl") as f:
    topics = [json.loads(line).get("topic", "Unknown") for line in f]

# Count occurrences
counts = Counter(topics)
for topic, cnt in counts.items():
    print(f"{topic}: {cnt}")
