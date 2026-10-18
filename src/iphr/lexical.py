"""Corpus-only scikit-learn word TF-IDF and cosine retrieval."""
from __future__ import annotations
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from .data_io import document_text

class LexicalRetriever:
    def __init__(self, docs):
        if not docs: raise ValueError("Corpus is empty")
        self.docs=list(docs)
        ids=[d["doc_id"] for d in docs]
        if len(set(ids)) != len(ids): raise ValueError("Duplicate document IDs")
        # sklearn defaults: lowercasing; word analyzer; token pattern >= 2 word chars;
        # L2-normalized tf-idf, so sparse dot products are cosine similarities.
        self.vectorizer=TfidfVectorizer()
        self.matrix=self.vectorizer.fit_transform([document_text(d) for d in self.docs])

    def search(self,query,top_k=5):
        if not isinstance(query,str) or not query.strip(): raise ValueError("Query must not be empty")
        if top_k < 1: raise ValueError("top_k must be positive")
        scores=np.asarray((self.matrix @ self.vectorizer.transform([query]).T).toarray()).ravel()
        order=sorted(range(len(self.docs)),key=lambda i:(-float(scores[i]),self.docs[i]["doc_id"]))[:top_k]
        return [{"doc_id":self.docs[i]["doc_id"],"title":self.docs[i]["title"],"source_url":self.docs[i].get("source_url", ""),"rank":rank,"score":float(scores[i])} for rank,i in enumerate(order,1)]
