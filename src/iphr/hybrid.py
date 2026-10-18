"""Unmodified reciprocal rank fusion (Cormack, Clarke and Buettcher 2009)."""
from __future__ import annotations
from .dense import DenseRetriever
from .lexical import LexicalRetriever


def reciprocal_rank_fusion(rankings, k=60, top_k=None):
    if k < 0: raise ValueError("k must be non-negative")
    if top_k is not None and top_k < 1: raise ValueError("top_k must be positive")
    scores, metadata = {}, {}
    for ranking in rankings:
        seen = set()
        for rank, result in enumerate(ranking, 1):
            doc_id=result["doc_id"]
            if doc_id in seen: raise ValueError(f"Duplicate candidate in ranked list: {doc_id}")
            seen.add(doc_id)
            scores[doc_id]=scores.get(doc_id,0.0)+1.0/(k+rank)
            metadata.setdefault(doc_id,result)
    ordered=sorted(scores,key=lambda doc_id:(-scores[doc_id],doc_id))
    if top_k is not None: ordered=ordered[:top_k]
    return [{"doc_id":doc_id,"title":metadata[doc_id].get("title", ""),"source_url":metadata[doc_id].get("source_url", ""),"rank":rank,"score":scores[doc_id]} for rank,doc_id in enumerate(ordered,1)]


class HybridRetriever:
    def __init__(self, docs, k=60, dense=None, lexical=None):
        self.docs=list(docs)
        if not self.docs: raise ValueError("Corpus is empty")
        self.k=k
        self.dense=dense or DenseRetriever(self.docs)
        self.lexical=lexical or LexicalRetriever(self.docs)

    def search(self,query,top_k=5):
        if top_k < 1: raise ValueError("top_k must be positive")
        n=len(self.docs)
        return reciprocal_rank_fusion([self.lexical.search(query,n),self.dense.search(query,n)],k=self.k,top_k=top_k)
