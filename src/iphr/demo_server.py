"""Local browser demo for the frozen Phase 2 exploratory retrieval configuration."""
from __future__ import annotations
import json
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import numpy as np
import yaml
from .data_io import load_corpus
from .dense import DenseRetriever
from .hybrid import reciprocal_rank_fusion
from .lexical import LexicalRetriever
from .reranker import rerank


class DemoEngine:
    def __init__(self, corpus_path: Path, config_path: Path):
        self.docs = load_corpus(corpus_path)
        self.config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        self.lexical = LexicalRetriever(self.docs)
        self.dense = DenseRetriever(self.docs, model_id=self.config["model"], revision=self.config["model_revision"])

    @staticmethod
    def _compact(row):
        value = {"doc_id": row["doc_id"], "title": row.get("title", ""), "source_url": row.get("source_url", ""), "rank": row["rank"], "score": round(float(row["score"]), 6)}
        if "explanation" in row:
            value["explanation"] = row["explanation"]
        return value

    def search(self, query: str, top_k: int = 5):
        query = query.strip()
        if not query:
            raise ValueError("Enter a technical search query.")
        if len(query) > 600:
            raise ValueError("Use a query shorter than 600 characters.")
        top_k = max(1, min(int(top_k), 10))
        lexical = self.lexical.search(query, len(self.docs))
        vector = np.asarray(self.dense.model.encode_query(query, normalize_embeddings=True, show_progress_bar=False), dtype=np.float32).reshape(-1)
        scores = self.dense.embeddings @ vector
        order = sorted(range(len(self.docs)), key=lambda index: (-float(scores[index]), self.docs[index]["doc_id"]))
        dense = [{"doc_id": self.docs[index]["doc_id"], "title": self.docs[index]["title"], "source_url": self.docs[index].get("source_url", ""), "rank": rank, "score": float(scores[index])} for rank, index in enumerate(order, 1)]
        rrf = reciprocal_rank_fusion([lexical, dense], k=self.config["rrf_k"])
        aware = rerank(query, rrf, self.docs, self.config["lambda_match"], self.config["lambda_conflict"])
        rrf_ranks = {row["doc_id"]: row["rank"] for row in rrf}
        return {
            "query": query,
            "configuration": {"rrf_k": self.config["rrf_k"], "lambda_match": self.config["lambda_match"], "lambda_conflict": self.config["lambda_conflict"], "model": self.config["model"], "model_revision": self.config["model_revision"], "corpus_documents": len(self.docs)},
            "methods": {
                "tfidf": [self._compact(row) for row in lexical[:top_k]],
                "minilm": [self._compact(row) for row in dense[:top_k]],
                "rrf": [self._compact(row) for row in rrf[:top_k]],
                "identifier_aware": [{**self._compact(row), "rrf_rank": rrf_ranks[row["doc_id"]], "rank_change": rrf_ranks[row["doc_id"]] - row["rank"]} for row in aware[:top_k]],
            },
        }


def handler_factory(engine: DemoEngine, static_dir: Path):
    class DemoHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(static_dir), **kwargs)
        def _json(self, payload, status=HTTPStatus.OK):
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status); self.send_header("Content-Type", "application/json; charset=utf-8"); self.send_header("Content-Length", str(len(data))); self.send_header("Cache-Control", "no-store"); self.end_headers(); self.wfile.write(data)
        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path == "/api/health":
                return self._json({"status": "ready", "documents": len(engine.docs), "model_cache_hit": engine.dense.cache_hit})
            if parsed.path == "/api/search":
                args = parse_qs(parsed.query)
                try:
                    return self._json(engine.search(args.get("q", [""])[0], args.get("top_k", [5])[0]))
                except (ValueError, TypeError) as exc:
                    return self._json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
            return super().do_GET()
        def log_message(self, fmt, *args):
            print("demo:", fmt % args)
    return DemoHandler


def serve(host: str, port: int, corpus_path: Path, config_path: Path, static_dir: Path):
    engine = DemoEngine(corpus_path, config_path)
    server = ThreadingHTTPServer((host, port), handler_factory(engine, static_dir))
    print("Phase 2 demo ready at http://" + host + ":" + str(port))
    print("Using the frozen author-annotated exploratory configuration; no network access is required.")
    server.serve_forever()
