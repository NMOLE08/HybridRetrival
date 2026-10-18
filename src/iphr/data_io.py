"""Corpus loading and stable corpus identity."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path


def load_corpus(path):
    with Path(path).open(encoding="utf-8") as f:
        docs = [json.loads(line) for line in f if line.strip()]
    if not docs:
        raise ValueError("Corpus is empty")
    ids = [d.get("doc_id") for d in docs]
    if any(not isinstance(x,str) or not x for x in ids) or len(set(ids)) != len(ids):
        raise ValueError("Corpus document IDs must be unique non-empty strings")
    if any(not isinstance(d.get("title"),str) or not isinstance(d.get("text"),str) for d in docs):
        raise ValueError("Every document must have title and text strings")
    return docs


def document_text(doc):
    return doc["title"] + "\n" + doc["text"]


def corpus_hash(docs):
    payload = [{"doc_id": d["doc_id"], "text": document_text(d)} for d in docs]
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
