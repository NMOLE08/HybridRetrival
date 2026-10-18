import pytest
from iphr.lexical import LexicalRetriever

DOCS=[
 {"doc_id":"z","title":"ESP32-C3","text":"single core RISC-V chip", "source_url":"https://example.org/z"},
 {"doc_id":"a","title":"ESP32-S3","text":"dual core Xtensa processor", "source_url":"https://example.org/a"},
 {"doc_id":"b","title":"CVE-2024-3094","text":"malicious xz library", "source_url":"https://example.org/b"},
]

def test_exact_match_and_oov_ties():
    r=LexicalRetriever(DOCS)
    assert r.search("CVE-2024-3094 malicious xz")[0]["doc_id"] == "b"
    oov=r.search("zzzzzzzz-not-in-vocabulary",3)
    assert [x["doc_id"] for x in oov] == ["a","b","z"]
    assert all(x["score"] == 0 for x in oov)
    assert [x["rank"] for x in oov] == [1,2,3]

def test_invalid_inputs():
    with pytest.raises(ValueError): LexicalRetriever([])
    r=LexicalRetriever(DOCS)
    with pytest.raises(ValueError): r.search(" ")
    with pytest.raises(ValueError): r.search("x",0)
