"""Explainable, bounded adjustment on top of an existing RRF ranking."""
from __future__ import annotations
import math
from .data_io import document_text
from .identifiers import extract_identifiers, conflicts


def explain(query, doc, base_score, lambda_match=0.0, lambda_conflict=0.0):
    if any(not math.isfinite(v) or v < 0 for v in (lambda_match,lambda_conflict)):
        raise ValueError("Adjustment weights must be finite and nonnegative")
    qids=extract_identifiers(query)
    dids=extract_identifiers(document_text(doc))
    wanted={x.canonical for x in qids}; actual={x.canonical for x in dids}
    matched=sorted(wanted & actual)
    fraction=len(matched)/len(wanted) if wanted else 0.0
    families=conflicts(qids,dids) if wanted else []
    conflict=bool(families)
    bonus=lambda_match*fraction
    penalty=lambda_conflict*int(conflict)
    return {"query_identifiers":[x.to_dict() for x in qids],"document_identifiers":[x.to_dict() for x in dids],"matched_identifiers":matched,"match_fraction":fraction,"conflict_families":families,"conflict":conflict,"rrf_score":float(base_score),"match_bonus":bonus,"conflict_penalty":penalty,"final_score":float(base_score)+bonus-penalty}


def rerank(query, ranking, docs, lambda_match=0.0, lambda_conflict=0.0):
    by_id={d["doc_id"]:d for d in docs}
    if len(by_id)!=len(docs): raise ValueError("Duplicate corpus document IDs")
    if len({r["doc_id"] for r in ranking}) != len(ranking): raise ValueError("Duplicate ranking document IDs")
    rows=[]
    for item in ranking:
        detail=explain(query,by_id[item["doc_id"]],item["score"],lambda_match,lambda_conflict)
        rows.append({**item,"score":detail["final_score"],"explanation":detail})
    # Return existing order and exact floating-point scores if no ID is found.
    if not extract_identifiers(query): return rows
    rows.sort(key=lambda x:(-x["score"],x["doc_id"]))
    for rank,row in enumerate(rows,1): row["rank"]=rank
    return rows
