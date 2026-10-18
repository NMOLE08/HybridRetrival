# Project context

Research question: Does a bounded exact-identifier reward, with an optional same-family conflict penalty on top of TF-IDF/MiniLM RRF, improve retrieval of technical passages without changing identifier-free rankings? This is a testable hypothesis, not a claim of improvement or global novelty.

Primary data: a small, auditable, publicly sourced technical passage benchmark with separate development and held-out test queries. Shared documents are intentional; query topics and identifier variants should be separated where practical. An optional SciFact check is secondary and does not measure technical identifier errors. Synthetic queries and agent-created judgments must be identified as such; independent human review is not assumed.

Baselines: corpus-only scikit-learn word TF-IDF, pretrained `sentence-transformers/all-MiniLM-L6-v2` (no training), and RRF with k=60 on the same corpus. Proposed method adds an exact supported-ID match fraction reward and optional explicit same-family conflict penalty. No supported query ID means exactly the same scores and order as RRF. Evaluation uses Recall@5, MRR@10, adjudicated wrong-identifier@1, timings, and group-level comparisons; known qrels may be incomplete.

Machine observed 2026-10-18: Windows 10 Pro 10.0.19045, Python 3.12.8, AMD Ryzen 5 3500U (4 cores/8 logical processors), 19,262,910,464 bytes RAM, AMD Radeon Vega 8, D drive 733,357,776,896 bytes free. CPU is the target; no GPU acceleration assumed. Workspace was empty and not a Git repository. Git 2.56.0 is installed but no user identity was configured.

The official [semantic-search example](https://github.com/huggingface/sentence-transformers/blob/main/examples/sentence_transformer/applications/semantic-search/semantic_search.py) was accessible on 2026-10-18; the [model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) identifies Apache-2.0. Model availability and actual immutable revision still require verification at the dense-baseline stage.
