# IEEE-style paper outline (pilot; not a claim of publication readiness)

## Title
Evaluating Identifier-Preserving Hybrid Retrieval for Technical Document Search

## Abstract outline
Technical searches often contain identifiers where a close variant may refer to a different entity. We evaluate a training-free exact-identifier adjustment over TF-IDF and pretrained MiniLM reciprocal rank fusion on a small source-backed pilot. With the predeclared development tie-break, the selected weights are zero and selected test MRR@10 equals RRF at 0.875 over ten identifier queries. A separately frozen nonzero exploratory setting obtains 1.0 on this pilot, but its paired bootstrap interval for the MRR difference includes zero and the dataset is small, source-conditioned and not independently judged. Do not claim a general improvement.

## I. Introduction
Motivate precise identifiers, close variants and the tension between lexical matching and semantic retrieval. State the narrow question: how does a transparent post-fusion adjustment behave relative to standard RRF under this pilot protocol? Describe the intended contribution as a reproducible implementation and cautious pilot evaluation, not a new model or established state-of-the-art.

## II. Related work
Use the verified bibliographic entries in [RELATED_WORK.md](RELATED_WORK.md) for Sentence-BERT, reciprocal rank fusion, BEIR, sparse/dense hybrid retrieval, exact lexical matching and entity-centric retrieval. More targeted review is required before any novelty claim. Cite the original model card and source dataset provenance as well as papers.

## III. Methodology
Describe title-plus-text passage representation, corpus-only TF-IDF, frozen MiniLM CPU cosine retrieval, RRF with k=60, identifier extraction and match/conflict adjustment using [METHODS.md](METHODS.md). Include `outputs/figures/architecture.svg`, the equations, tie handling and unsupported identifier classes. Explicitly identify the no-op selected configuration and distinguish the exploratory fixed settings.

## IV. Dataset and annotations
Explain 21 CVE and 10 Espressif passages, 6 dev and 12 test queries, query/label construction, source revisions and rights, relevant cross-reference, judged versus unjudged pairs, and lack of independent review. Cite [DATASET_CARD.md](DATASET_CARD.md), the provenance CSV, source licenses and judgment evidence. Report the query split separately from shared documents. This is not a benchmark representative of technical search.

## V. Baselines and experimental settings
List TF-IDF, MiniLM, RRF, selected match-only, selected full, and separately labeled exploratory nonzero match-only/full variants. Give frozen model revision, hashes, CPU, candidate policy, development-only selection, seed, k and cutoffs. Define known-positive Recall@5, MRR@10, binary nDCG@10 and bounded WrongIdentifier@1. Explain paired-query bootstrap and timing conditions.

## VI. Results and ablation
Use the stored `outputs/tables/identifier_metrics.tex` and plots, with n=10 identifier queries and uncertainty. Report selected full = RRF (MRR 0.875; Recall 1.0); distinguish exploratory 1.0 MRR with delta 0.125 and 95% paired bootstrap interval [0, 0.3]. The exploratory match-only and full results coincide, so there is no observed aggregate penalty contribution. Present `case_studies.tex` and error bounds; never fill unknown qrels as negatives. Separate n=2 natural-query results. Only report SciFact if its saved run actually completes, as a general-domain check, not evidence of identifier accuracy.

## VII. Discussion and limitations
Discuss small sample size, agent-created source-conditioned labels, missing judgments, CVE cross-references, dev tie and zero parameters, restricted regex coverage, model truncation and one-machine timing. Report that no fixed-variant MRR deterioration was observed on this sample without assuming it cannot occur. Identify independent annotation, broader corpora and a new untouched test set as necessary follow-up.

## VIII. Conclusion
Conclude that the pipeline and reproducibility framework are implemented and that the chosen primary setting reproduces RRF; the small exploratory sensitivity result suggests a question for a properly powered independent study rather than proving an improvement.

## References
Use the sourced entries in [RELATED_WORK.md](RELATED_WORK.md), the MiniLM model card, CVE/Espressif source records and applicable dataset notices. Verify venue formatting and publication metadata before submission; do not invent citations.
