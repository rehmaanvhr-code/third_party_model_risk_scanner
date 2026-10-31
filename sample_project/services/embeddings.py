from sentence_transformers import SentenceTransformer
from transformers import pipeline

embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")


def embed(texts):
    return embedder.encode(texts)
