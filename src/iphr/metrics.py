"""Hand-checkable binary relevance metrics and conservative error accounting."""
from __future__ import annotations
import math
from .identifiers import extract_identifiers, conflicts
from .data_io import document_text


def recall_at_k(ranked_ids, relevant, k=5):
    relevant=set(relevant)
    if not relevant: return 0.0
    return len(set(ranked_ids[:k]) & relevant)/len(relevant)


def reciprocal_rank_at_k(ranked_ids, relevant, k=10):
    relevant=set(relevant)
    return next((1.0/i for i,d in enumerate(ranked_ids[:k],1) if d in relevant),0.0)


def ndcg_at_k(ranked_ids, relevant, k=10):
    relevant=set(relevant)
    dcg=sum(1/math.log2(i+1) for i,d in enumerate(ranked_ids[:k],1) if d in relevant)
    ideal=sum(1/math.log2(i+1) for i in range(1,min(len(relevant),k)+1))
    return dcg/ideal if ideal else 0.0


def wrong_identifier_at_1(query, top_doc, judgments):
    """Return 0, 1 or None (contradictory but unjudged); non-eligible returns None.

    Only an explicit audited negative with same-family conflict counts as wrong.
    Unjudged conflicting top documents are unknown, not correct negatives.
    """
    qids=extract_identifiers(query.get("text", ""))
    if query.get("query_type") not in {"identifier", "near_miss"} or not qids:
        return None
    if top_doc is None: return 0
    if not conflicts(qids,extract_identifiers(document_text(top_doc))): return 0
    value=judgments.get(top_doc["doc_id"])
    if value == 0: return 1
    if value == 1: return 0
    return None
