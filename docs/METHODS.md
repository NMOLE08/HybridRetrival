# Methodology

## Data and retrieval

The experiment uses a common set of 31 passages: 21 CVE CNA descriptions and 10 Espressif SoC capability header excerpts. Each passage is represented by its title, a newline, and its extracted text. Six development queries and twelve held-out test queries have disjoint query IDs and exact texts; documents are shared by design. See [the dataset card](DATASET_CARD.md), evidence tables and provenance files for the source revisions, restrictions and annotation limitations.

The lexical baseline fits scikit-learn's default word-level TF-IDF on the corpus alone and returns cosine similarities. It lowercases and uses the default token pattern, so punctuation in IDs is split. The semantic baseline encodes the same passages and queries with the existing `sentence-transformers/all-MiniLM-L6-v2`, immutable revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`, using normalized embeddings and cosine similarity on CPU; no model training is performed. Both systems rank the full 31-document corpus, breaking score ties by document ID.

For retrieval lists L and one-based rank r, standard reciprocal rank fusion is

\[
S_{RRF}(d)=\sum_{L:d\in L}\frac{1}{k+r_L(d)},\quad k=60.
\]

A missing document contributes zero to that list. For this small corpus both lists are full; the optional SciFact check uses the union of each retriever's top 100 candidates instead.

## Identifier-aware adjustment

The parser extracts explicit CVEs and ESP32 C/S/H/P numeric variants, normalizes case and supported Unicode dashes, and retains original spans. Generic ESP32 is a distinct identifier. It does not support all possible identifiers, IEEE standards, or implicit references. Let Q and D be the sets of canonical extracted query and passage IDs. The exact-match fraction is \(m=|Q\cap D|/|Q|\) when Q is nonempty and zero otherwise. A binary conflict c is one when a document contains an explicit conflicting same-family variant and no requested variant from that family; generic ESP32 by itself is not a wrong variant. Multiple-ID and cross-reference cases are handled conservatively. The proposed score is

\[
S(d)=S_{RRF}(d)+\lambda_m m(q,d)-\lambda_c c(q,d).
\]

When Q is empty, the implementation preserves baseline scores and order exactly. It exposes query/document identifiers and every score component. In the predeclared development grid all 12 settings tied, and the predeclared smallest-weight tie-break selected \(\lambda_m=\lambda_c=0\). Therefore the selected proposed method is **exactly RRF**, including on test. Before test access, fixed exploratory variants with (0.003, 0) and (0.003, 0.003) were also frozen to show sensitivity; these were chosen after observing the dev tie and are not independent confirmatory hypotheses. [The frozen config](../configs/final.yaml) and [development record](../outputs/manifests/dev_freeze.json) contain the exact settings.

## Metrics and uncertainty

For known positive set R and a ranked list, Recall@5 is \(|R\cap L_5|/|R|\); MRR@10 is the inverse position of the first known positive within ten, or zero. Binary nDCG@10 divides \(\sum_{i\le 10}\mathbf{1}[d_i\in R]/\log_2(i+1)\) by the ideal ordering's DCG. These are known-positive metrics, not estimates against a fully judged corpus. The overall score is the mean across queries.

WrongIdentifier@1 is computed for supported identifier-bearing queries only. A top result is counted as wrong only when it has a same-family conflict and an explicit negative judgment. A conflicting, unjudged top result is unknown; the lower bound is observed wrong / eligible, and the upper bound adds unknown / eligible. A positive judgment or no detected conflict is counted as not wrong by this operational definition; lack of a detected conflict does not prove semantic relevance. Natural queries are excluded from this denominator.

Differences versus RRF use a paired query-level bootstrap of 10,000 resamples and seed 42, with percentile 2.5% and 97.5% intervals; the tiny sample makes intervals unstable. Timings are individual warmed sequential CPU components, three samples per query, not a measured end-to-end latency; model load and indexing are separately recorded. The first uncached document embedding build was measured in an earlier run, whereas the final run used cached embeddings. Runtime conditions, platform and pinned packages appear in the manifests.

Primary rankings are stored before test judgments are evaluated and were generated twice to check repeat order. The final configuration, queries, qrels, source corpus, model weights and run commit hashes are recorded in `outputs/manifests/`. See `outputs/final/` for complete rankings, explanations, per-query data, timing samples and bootstrap results.
