from pathlib import Path
from tempfile import TemporaryDirectory
import numpy as np
import pytest
from iphr.data_io import corpus_hash
from iphr.dense import DenseRetriever


class FakeEncoder:
    def __init__(self): self.document_calls = 0
    def encode_document(self, texts, **kwargs):
        self.document_calls += 1
        return np.array([[1, 0], [1, 0], [0, 1]], dtype=np.float32)
    def encode_query(self, query, **kwargs): return np.array([1, 0],dtype=np.float32)


DOCS = [
    {"doc_id":"b","title":"One","text":"Alpha","source_url":"https://example.org/b"},
    {"doc_id":"a","title":"Two","text":"Alpha","source_url":"https://example.org/a"},
    {"doc_id":"c","title":"Three","text":"Beta","source_url":"https://example.org/c"},
]


def test_dense_stable_ranking_and_cache():
    Path("cache").mkdir(exist_ok=True)
    with TemporaryDirectory(dir="cache") as cache:
        model=FakeEncoder()
        retriever=DenseRetriever(DOCS,cache_dir=cache,model=model,model_id="fake",revision="fixed")
        assert [r["doc_id"] for r in retriever.search("alpha", 3)] == ["a","b","c"]
        assert retriever.search("alpha", 3) == retriever.search("alpha", 3)
        assert model.document_calls == 1
        second=DenseRetriever(DOCS,cache_dir=cache,model=model,model_id="fake",revision="fixed")
        assert second.cache_hit and model.document_calls == 1
        with pytest.raises(ValueError): second.search(" ")
        with pytest.raises(ValueError): second.search("x",0)


def test_corpus_identity_includes_document_text_and_order():
    assert corpus_hash(DOCS) != corpus_hash(list(reversed(DOCS)))
    assert corpus_hash(DOCS) != corpus_hash([{**DOCS[0], "text":"different"}, *DOCS[1:]])
