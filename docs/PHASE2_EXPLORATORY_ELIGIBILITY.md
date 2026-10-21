# Phase 2 exploratory eligibility audit

## Result

The frozen `phase2_exploratory_v1` subset has **30 eligible author-annotated
identifier queries**: 12 development and 18 held-out test queries. All are CVE
information needs. It contains 32 source-evidenced author positives: one
canonical record for 28 needs and canonical plus an explicitly target-containing
cross-reference for each of `cve-21` and `cve-35`.

This is a conservative answerability subset, not a corrected human benchmark.
The retained corpus remains 150 documents. The query composition is narrowed
because no ESP32 query has an author-labeled positive with the required retained
source evidence.

## Eligibility policy applied before retrieval

The policy in [the exploratory amendment](PHASE2_EXPLORATORY_PROTOCOL.md)
requires author validity `yes`, an author label `1`, valid pinned provenance,
and the requested target in the full raw source. For CVE records, the canonical
record itself is accepted as source evidence even when the short corpus excerpt
does not repeat the CVE string. This was applied prior to running any Phase 2
ranker.

The query-level evidence table is
[`query_eligibility.csv`](../outputs/phase2/stage15_exploratory/query_eligibility.csv).
It excludes 16 author-invalid natural questions and 24 valid questions without a
source-evidenced author positive: six CVE, sixteen ESP32, and two natural
questions. Exclusion is based solely on answerability/evidence, not on
retrieval performance.

## Author-label audit

The original immutable labels contain 102 author `1` rows and 171 author `0`
rows. The full audit found 32 `1` rows whose raw source contains the query
target. Seventy author-positive rows do not meet that condition; the derived
exploratory qrels record them as `unknown`, rather than falsely treating them as
negative or deleting the originals. The 171 author negatives remain explicitly
author-produced negatives, though only four occur for the eligible subset.

Two retained positives are genuine source-text cross-references: `pair-0192`
for `cve-35` and `pair-0220` for `cve-21`. Candidate-title similarity and a
nearby/confusable CVE identifier alone do not satisfy the policy. The detailed
row-level dispositions are in
[`label_evidence_audit.csv`](../outputs/phase2/stage15_exploratory/label_evidence_audit.csv).

## Unresolved material

The 152 source-backed v3 candidates remain completely unjudged. They are not
needed to support the 30-query frozen subset and are not promoted to qrels. A
future author-adjudication version would be required to recover excluded ESP32,
natural, or six unsupported CVE queries. The results therefore cannot claim
coverage of ESP32 variants, natural-language needs, or exhaustive relevance.
