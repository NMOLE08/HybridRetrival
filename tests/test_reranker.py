import pytest
from iphr.reranker import explain,rerank

DOCS=[
 {"doc_id":"a","title":"ESP32-C3","text":"technical chip"},
 {"doc_id":"b","title":"ESP32-S3","text":"target chip"},
 {"doc_id":"c","title":"ESP32","text":"generic family"},
 {"doc_id":"d","title":"ESP32-S3 and ESP32-C3","text":"comparison"},
]
RANK=[{"doc_id":d["doc_id"],"rank":i+1,"score":v} for i,(d,v) in enumerate(zip(DOCS,[.032,.030,.029,.028]))]

def test_match_and_conflict_explanations():
    wrong=explain("ESP32-S3",DOCS[0],.032,.003,.002)
    exact=explain("ESP32-S3",DOCS[1],.030,.003,.002)
    both=explain("ESP32-S3",DOCS[3],.028,.003,.002)
    assert wrong["conflict"] and wrong["final_score"] == pytest.approx(.030)
    assert exact["match_fraction"]==1 and exact["final_score"] == pytest.approx(.033)
    assert not both["conflict"] and both["match_fraction"]==1
    assert not explain("ESP32-S3",DOCS[2],.029,.003,.002)["conflict"]
    assert [x["doc_id"] for x in rerank("ESP32-S3",RANK,DOCS,.003,.002)][0]=="b"

def test_natural_query_identical_and_multi_id_fraction():
    result=rerank("How do computers learn?",RANK,DOCS,.012,.006)
    assert [(r["doc_id"],r["rank"],r["score"]) for r in result] == [(r["doc_id"],r["rank"],r["score"]) for r in RANK]
    multi=explain("ESP32-S3 CVE-2024-3094",DOCS[1],.03,.006,.003)
    assert multi["match_fraction"] == .5
    assert multi["final_score"] == pytest.approx(multi["rrf_score"]+multi["match_bonus"]-multi["conflict_penalty"])

def test_invalid_weights():
    with pytest.raises(ValueError): explain("x",DOCS[0],.1,-1,0)
