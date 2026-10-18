import math
import pytest
from iphr.metrics import recall_at_k,reciprocal_rank_at_k,ndcg_at_k,wrong_identifier_at_1
from iphr.evaluation import evaluate_query,summarize,paired_bootstrap


def test_metrics_hand_calculated():
    ranking=["x","a","z","b","c","d"]
    relevant={"a","b","d"}
    assert recall_at_k(ranking,relevant,5)==pytest.approx(2/3)
    assert reciprocal_rank_at_k(ranking,relevant,10)==.5
    expected=(1/math.log2(3)+1/math.log2(5)+1/math.log2(7))/(1+1/math.log2(3)+1/math.log2(4))
    assert ndcg_at_k(ranking,relevant,10)==pytest.approx(expected)
    assert recall_at_k(ranking,set())==0
    assert reciprocal_rank_at_k(ranking,{"outside"})==0
    assert ndcg_at_k(ranking,set())==0
    assert recall_at_k(["x"]*5+["a"],{"a"},5)==0


def test_wrong_identifier_requires_audited_negative():
    q={"query_id":"q","text":"ESP32-S3 GPIO","query_type":"identifier","identifier_family":"esp32"}
    doc={"doc_id":"wrong","title":"ESP32-C3","text":"GPIO"}
    assert wrong_identifier_at_1(q,doc,{"wrong":0})==1
    assert wrong_identifier_at_1(q,doc,{"wrong":1})==0
    assert wrong_identifier_at_1(q,doc,{}) is None
    mixed={"doc_id":"mixed","title":"ESP32-S3 and ESP32-C3","text":"GPIO"}
    assert wrong_identifier_at_1(q,mixed,{})==0
    natural={**q,"query_type":"natural","text":"GPIO controllers"}
    assert wrong_identifier_at_1(natural,doc,{"wrong":0}) is None
    row=evaluate_query(q,["wrong"],{}, {"wrong":doc})
    summary=summarize([row])["wrong_id_at_1"]
    assert summary == {"eligible":1,"wrong":0,"unknown":1,"adjudicated":0,"lower_bound":0.0,"upper_bound":1.0,"rate_among_known":None}


def test_paired_bootstrap_deterministic():
    a=[1,.5,0];b=[.5,.5,0]
    assert paired_bootstrap(a,b,seed=42,samples=1000)==paired_bootstrap(a,b,seed=42,samples=1000)
    assert paired_bootstrap([1],[0]) is None
    with pytest.raises(ValueError): paired_bootstrap([1,2],[1])
