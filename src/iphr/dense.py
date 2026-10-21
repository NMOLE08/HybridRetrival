"""Frozen pretrained sentence-transformer cosine retrieval on CPU."""
from __future__ import annotations
import hashlib
from importlib.metadata import PackageNotFoundError, version
import json
import time
from pathlib import Path
import numpy as np
from .data_io import corpus_hash, document_text

MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"


class DenseRetriever:
    def __init__(self, docs, cache_dir="cache/embeddings", model=None, model_id=MODEL_ID, revision=MODEL_REVISION):
        if not docs:
            raise ValueError("Corpus is empty")
        self.docs = list(docs)
        ids = [d["doc_id"] for d in self.docs]
        if len(set(ids)) != len(ids):
            raise ValueError("Duplicate document IDs")
        self.model_id, self.revision = model_id, revision
        self.corpus_hash = corpus_hash(self.docs)
        start = time.perf_counter()
        if model is None:
            try:
                from sentence_transformers import SentenceTransformer
                # The declared model revision is already cached and verified by the
                # project.  Never let a benchmark run fetch mutable Hub metadata.
                model = SentenceTransformer(model_id, revision=revision, device="cpu", local_files_only=True)
            except Exception as exc:
                raise RuntimeError(f"Could not load pretrained {model_id} at revision {revision}; check network access or populate the Hugging Face cache. Original error: {exc}") from exc
        self.model_load_seconds = time.perf_counter() - start
        self.model = model
        versions = {}
        for package in ("sentence-transformers", "transformers", "torch"):
            try: versions[package] = version(package)
            except PackageNotFoundError: versions[package] = "unavailable"
        identity = {"model": model_id, "revision": revision, "corpus_hash": self.corpus_hash, "normalized": True, "packages": versions}
        key = hashlib.sha256(json.dumps(identity,sort_keys=True).encode("utf-8")).hexdigest()
        cache = Path(cache_dir); cache.mkdir(parents=True, exist_ok=True)
        path = cache / (key + ".npz")
        start = time.perf_counter()
        self.cache_hit = path.is_file()
        if self.cache_hit:
            with np.load(path, allow_pickle=False) as stored:
                matrix = stored["embeddings"]
        else:
            matrix = np.asarray(self.model.encode_document([document_text(d) for d in self.docs], normalize_embeddings=True, show_progress_bar=False),dtype=np.float32)
            np.savez_compressed(path, embeddings=matrix)
        if matrix.ndim != 2 or matrix.shape[0] != len(self.docs) or not np.isfinite(matrix).all():
            raise ValueError(f"Invalid embedding cache {path}; remove only this project cache file and retry")
        self.embeddings = matrix
        self.preprocessing_seconds = time.perf_counter() - start
        self.cache_key = key

    def search(self, query, top_k=5):
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query must not be empty")
        if top_k < 1:
            raise ValueError("top_k must be positive")
        vector = np.asarray(self.model.encode_query(query, normalize_embeddings=True, show_progress_bar=False),dtype=np.float32).reshape(-1)
        if vector.shape[0] != self.embeddings.shape[1] or not np.isfinite(vector).all():
            raise ValueError("Invalid query embedding")
        scores = self.embeddings @ vector
        order = sorted(range(len(self.docs)), key=lambda i: (-float(scores[i]), self.docs[i]["doc_id"]))[:top_k]
        return [{"doc_id":self.docs[i]["doc_id"],"title":self.docs[i]["title"],"source_url":self.docs[i].get("source_url", ""),"rank":rank,"score":float(scores[i])} for rank,i in enumerate(order,1)]
