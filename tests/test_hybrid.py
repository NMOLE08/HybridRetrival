import pytest
from iphr.hybrid import reciprocal_rank_fusion


def row(doc): return {"doc_id":doc,"title":doc,"score":1.0}

def test_rrf_hand_calculation_and_tie_order():
    out=reciprocal_rank_fusion([[row("a"),row("b")],[row("b"),row("a")]],k=60)
    assert [r["doc_id"] for r in out] == ["a","b"]
    assert out[0]["score"] == pytest.approx(1/61 + 1/62)
    assert out[1]["score"] == pytest.approx(1/62 + 1/61)

def test_rrf_partial_lists_and_duplicates():
    out=reciprocal_rank_fusion([[row("a"),row("c")],[row("b")]],k=60)
    assert [x["doc_id"] for x in out] == ["a","b","c"]
    assert out[2]["score"] == pytest.approx(1/62)
    with pytest.raises(ValueError): reciprocal_rank_fusion([[row("a"),row("a")]])
