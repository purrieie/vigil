import chromadb
import json
from chromadb.utils import embedding_functions
from core.config import settings

client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
embedder = embedding_functions.DefaultEmbeddingFunction()

collection = client.get_or_create_collection(
    name="scam_scripts",
    embedding_function=embedder
)

def seed_scripts():
    with open("data/scam_scripts_seed.json") as f:
        scripts = json.load(f)

    existing = collection.count()
    if existing >= len(scripts):
        return

    collection.add(
        ids=[s["id"] for s in scripts],
        documents=[s["pattern"] for s in scripts],
        metadatas=[{"category": s["category"]} for s in scripts]
    )

def match_patterns(transcript: str, top_k: int = 3):
    results = collection.query(query_texts=[transcript], n_results=top_k)
    matches = []
    for doc, dist in zip(results["documents"][0], results["distances"][0]):
        similarity = 1 - dist
        if similarity > 0.3:
            matches.append(doc)
    return matches