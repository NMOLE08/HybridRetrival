"""Compute per-query metrics, grouped summaries and paired bootstrap intervals."""
from __future__ import annotations
from collections import defaultdict
import numpy as np
from .metrics import recall_at_k, reciprocal_rank_at_k, ndcg_at_k, wrong_identifier_at_1
from .identifiers import extract_identifiers


def evaluate_query(query, ranked_ids, judgments, docs):
    if len(ranked_ids) != len(set(ranked_ids)): raise ValueError("Ranking contains duplicate IDs")
    relevant={doc for doc,rel in judgments.items() if rel==1}
    top=docs[ranked_ids[0]] if ranked_ids else None
    eligible=query.get("query_type") in {"identifier","near_miss"} and bool(extract_identifiers(query["text"]))
    return {"query_id":query["query_id"],"query_type":query["query_type"],"identifier_family":query["identifier_family"],"recall_at_5":recall_at_k(ranked_ids,relevant,5),"mrr_at_10":reciprocal_rank_at_k(ranked_ids,relevant,10),"ndcg_at_10":ndcg_at_k(ranked_ids,relevant,10),"known_relevant":len(relevant),"wrong_id_eligible":eligible,"wrong_id_at_1":wrong_identifier_at_1(query,top,judgments) if eligible else None}


def summarize(rows):
    n=len(rows)
    result={"n_queries":n}
    for metric in ("recall_at_5","mrr_at_10","ndcg_at_10"):
        result[metric]=sum(x[metric] for x in rows)/n if n else None
    eligible=[r for r in rows if r["wrong_id_eligible"]]
    known=[r["wrong_id_at_1"] for r in eligible if r["wrong_id_at_1"] is not None]
    wrong=sum(known); unknown=len(eligible)-len(known)
    result["wrong_id_at_1"]={"eligible":len(eligible),"wrong":wrong,"unknown":unknown,"adjudicated":len(known),"lower_bound":wrong/len(eligible) if eligible else None,"upper_bound":(wrong+unknown)/len(eligible) if eligible else None,"rate_among_known":wrong/len(known) if known else None}
    return result


def group_summaries(rows):
    groups=defaultdict(list)
    for row in rows:
        groups['all'].append(row);groups['type:'+row['query_type']].append(row);groups['family:'+row['identifier_family']].append(row)
    return {name:summarize(items) for name,items in sorted(groups.items())}


def paired_bootstrap(values_a, values_b, seed=42, samples=10000):
    a=np.asarray(values_a,dtype=float);b=np.asarray(values_b,dtype=float)
    if a.shape != b.shape or a.ndim != 1: raise ValueError("Paired inputs must be equal-length vectors")
    if len(a)<2: return None
    delta=a-b; rng=np.random.default_rng(seed)
    means=delta[rng.integers(0,len(delta),size=(samples,len(delta)))].mean(axis=1)
    return {"n":len(delta),"difference":float(delta.mean()),"low":float(np.quantile(means,.025)),"high":float(np.quantile(means,.975)),"samples":samples,"seed":seed}
