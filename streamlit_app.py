import sys, subprocess
subprocess.check_call([sys.executable, "-m", "pip", "install", "openai"])
import streamlit as st
import subprocess
import json
from dotenv import load_dotenv
load_dotenv()
# ── 50 Topic Keywords ──
TOPICS = [
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

def get_top_journalists(topic: str, k: int):
    """Call your query script and parse its output."""
    cmd = ["python", "query_top_journalists.py", topic, str(k)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        st.error("Error running query:\n" + result.stderr)
        return []
    lines = result.stdout.splitlines()[1:]  # skip header line
    out = []
    for line in lines:
        parts = line.split(" — ")
        if len(parts) != 2:
            continue
        rank_name, mentions = parts
        _, name = rank_name.split(". ", 1)
        count = int(mentions.split()[0])
        out.append({"Journalist": name, "Mentions": count})
    return out

st.set_page_config(page_title="Top Journalists Leaderboard", layout="wide")
st.title("🏆 Top Journalists Leaderboard")

# Searchable dropdown of 50 topics
topic = st.selectbox(
    "Select a topic", 
    TOPICS, 
    index=0, 
    help="Type to filter the list"
)

k = st.slider("How many journalists to show?", 1, 10)

if st.button("Run"):
    with st.spinner(f"Querying for top {k} in “{topic}”…"):
        leaders = get_top_journalists(topic, k)
    if leaders:
        st.subheader(f"Top {k} journalists for “{topic}”")
        st.table(leaders)
    else:
        st.write("No results found. Try a different topic or increase K.")
