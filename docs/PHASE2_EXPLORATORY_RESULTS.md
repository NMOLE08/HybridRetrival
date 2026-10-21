# Phase 2 exploratory held-out results

These are results for the frozen author-annotated `phase2_exploratory_v1` subset: 18 CVE identifier queries, 150 documents, and 32 source-evidenced author positives. They are **not** independently reviewed benchmark results.

| System | MRR@10 | Recall@5 | nDCG@10 | WrongIdentifier@1 observed bounds |
|---|---:|---:|---:|---:|
| TF-IDF | 0.8667 | 0.8889 | 0.8844 | 0/18 to 3/18 |
| MiniLM | 0.7278 | 0.8333 | 0.7801 | 0/18 to 7/18 |
| RRF (k=60) | 0.8074 | 1.0000 | 0.8544 | 0/18 to 5/18 |
| Match-only (`0,0`) | 0.8074 | 1.0000 | 0.8544 | 0/18 to 5/18 |
| Identifier-aware (`0,.003`) | 1.0000 | 1.0000 | 1.0000 | 0/18 to 0/18 |

The selected method improves held-out MRR@10 over RRF by 0.1926; its paired percentile-bootstrap 95% interval is [0.0556, 0.3481] over 18 queries. It has five MRR gains, zero losses, and thirteen ties. Its Recall@5 difference is zero. This interval is a descriptive resampling result for this small, source-filtered, author-annotated sample. It is not evidence of statistically significant general-purpose improvement or independent validation.

TF-IDF has higher MRR@10 than RRF by 0.0593, with bootstrap interval [-0.0333, 0.1704]; MiniLM is lower by 0.0796, with interval [-0.1791, -0.0009]. Those contrasts also remain exploratory. Exact per-query results, derived qrels policy, bootstrap output, and timing samples are in [`outputs/phase2/stage17/`](../outputs/phase2/stage17/).

Timing is component-level CPU timing, after warm-up, rather than end-to-end latency. Median/P95 milliseconds are 1.62/1.83 TF-IDF, 21.12/23.36 query embedding, 0.31/0.40 dense ranking, 0.34/0.40 RRF, and 21.80/25.80 identifier reranking. Model load was 14.67 seconds and the embedding cache was a hit.

The results have no natural-language or ESP32 eligible queries. Candidate coverage is incomplete, 70 author-positive labels were downgraded to unknown in the derived qrels for lack of target evidence, and only four explicit author negatives occur in the eligible subset. These constraints can make the identifier-aware effect appear stronger or weaker than it would under complete, independently produced judgments.
