# Phase 2 exploratory protocol amendment

**Effective 2026-10-21.** This amendment preserves, but does not overwrite,
the preregistered [Phase 2 protocol](PHASE2_PROTOCOL.md), the v1–v3 review
materials, source provenance, prior decisions, and all prior experiment history.

## Scope change

The original protocol required independent human relevance review before any
paper-grade effectiveness evaluation. That requirement cannot be met with the
available returned material: the 273 existing labels have no independent-review
provenance, source-specific reviewer notes, or second-rater agreement. The study
is therefore changed to an **author-annotated exploratory empirical study**.

This amendment is made after dataset construction and inspection of preliminary
author judgments, but before any Phase 2 retrieval ranking, parameter tuning, or
held-out Phase 2 effectiveness result. It is not a retrospective change to a
result. The held-out split constrains configuration selection, but it does not
make the annotations independent or confirmatory.

## Label status and eligibility policy

The project author assigned the 273 original labels: 102 `relevant` and 171
`irrelevant`. Their semantic accuracy is not independently verified. The v3
normalized materials are the operational input; v2 and all original labels stay
immutable.

An exploratory query is eligible only if all of the following were determined
without retrieval output:

1. The submitted question decision is `yes`.
2. It has an author-labeled positive candidate.
3. The full pinned raw source for that candidate contains the query target. For a
   CVE query, a source record whose own canonical CVE identifier equals the
   target qualifies; a cross-reference qualifies only when the requested target
   is present in the full retained source.
4. The candidate has valid recorded provenance and SHA-256 evidence.

All other label-`1` rows are retained as author annotations but become
`unknown` in the derived exploratory qrels unless they meet the source-evidence
condition. They are not silently converted to negatives. An explicit author
`0` remains an author-produced negative and is reported as such. Unjudged pairs
remain unknown. A query without an eligible positive is excluded for
answerability/coverage, never because of a retrieval result.

The 152 v3 additional candidates are retained as unjudged source-backed leads.
They are not automatically promoted. They are not needed to establish the
conservative eligible subset; adjudicating them would be required only to
recover excluded queries in a later versioned author-annotation update.

## Methods and split discipline

Use the unchanged Phase 1 implementation: pretrained `all-MiniLM-L6-v2`, word
TF-IDF, RRF with `k=60`, and identifier-aware reranking. No training,
fine-tuning, query rewriting, or corpus modification is allowed. Select weights
only on the eligible development queries over match weights `{0, .003, .006,
.012}` and conflict weights `{0, .003, .006}` with the original lexicographic
criteria. Freeze the selected configuration, code, corpus, eligible-query/qrel
hashes, model identity, random seed, and environment before reading held-out
test metrics.

Test evaluation reports MRR@10, Recall@5, nDCG@10, wrong-identifier observed
bounds, per-query outcomes, timing, paired bootstrap intervals (10,000
resamples, seed 42), gains/losses/ties, and failures. It treats unknown pairs as
unknown. Results must be called exploratory throughout.

## Interpretation limits

The dataset is small, author-created, author-annotated, incomplete in candidate
coverage, and narrowed by evidence eligibility. It has no independent agreement
estimate. Its test split prevents direct test-tuning leakage but cannot validate
annotation accuracy or establish statistical generalization. Phase 1 results are
historical pilot results and must be shown separately from Phase 2 outcomes.
