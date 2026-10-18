# TERRA EXECUTION BLUEPRINT

**Research project:** Evaluating Identifier-Preserving Hybrid Retrieval for Technical Document Search  
**Prepared:** 18 October 2026  
**Execution style:** Agent-led, stage-gated, reproducible, local-first  
**Primary language:** Python 3.11+  
**Primary model:** `sentence-transformers/all-MiniLM-L6-v2` (pretrained; **no fine-tuning**)  
**Original repository inspiration:** https://github.com/huggingface/sentence-transformers  
**Runnable reference:** https://github.com/huggingface/sentence-transformers/blob/main/examples/sentence_transformer/applications/semantic-search/semantic_search.py

> **Scope of claim:** This is an experimental extension to established lexical, dense, and hybrid retrieval. Do **not** claim to have invented hybrid retrieval, RRF, identifier matching, or MiniLM. The study tests a specific lightweight, reproducible identifier-preserving reranker in a defined technical-document setting. Novelty in the global research literature is **not guaranteed**.

---

## 0. Context for the coding agent (read this first)

### 0.1 Why this project exists

The user needs an academically defensible AI research project that can be implemented relatively quickly using a working open-source foundation. The primary deliverable is **experimental evidence and a research-paper-ready package**, not a polished commercial app. The user intends to run the work through the Terra 5.6 coding agent with broad workspace permissions. Work incrementally, minimize external services, and preserve a complete trail of what was done.

### 0.2 Problem statement

Semantic retrievers can find conceptually related documents but sometimes conflate technical identifiers with nearby variants; lexical retrieval excels at exact strings but misses semantic paraphrases. Examples: `ESP32-S3` versus `ESP32-C3`; `CVE-2024-3094` versus a different CVE; `IEEE 802.11ax` versus other Wi-Fi standards. Can a **lightweight identifier-preserving ranking adjustment**, layered on a standard lexical–semantic hybrid, improve retrieval for identifier-sensitive technical queries while leaving general queries largely unaffected?

This is a hypothesis, not an assumed finding. A null result is publishable as an honest course-paper result.

### 0.3 What belongs to prior work vs. our work

**Reused:** pretrained MiniLM embeddings, TF-IDF feature extraction, cosine similarity, reciprocal rank fusion (RRF), known evaluation metrics, public documentation and datasets. Attribute each source accurately.  
**Implemented and evaluated here:** technical-identifier normalization/extraction, explicit same-family conflict detection, small rank adjustment, reproducible benchmark construction/validation, controlled baselines, ablations, efficiency and error analysis.  
**Not in scope:** model pretraining, deep learning fine-tuning, vector database, production API, React UI, LLM chatbot, RAG answer generation, paid APIs, giant web crawls, benchmark leaderboard claims.

### 0.4 Research hypotheses

- **H1:** The proposed identifier-aware reranker has a higher MRR@10 or Recall@5 on identifier-sensitive queries than standard RRF.
- **H2:** The method lowers a carefully defined *wrong-identifier@1* rate relative to standard RRF.
- **H3 (constraint):** On identifier-free natural-language queries, retrieval rankings should be identical to unmodified RRF; measured average query latency should remain practical. This identity should hold by construction when no supported identifier is extracted.

H1/H2 may fail: report actual results, avoid invented numbers, and show failures.

### 0.5 Research questions

1. How do TF-IDF, MiniLM, and unmodified RRF compare for technical identifiers and ordinary technical queries?
2. Does a limited exact-identifier reward improve top-ranked document relevance and reduce wrong-variant retrieval?
3. Do mismatch penalties improve results beyond exact-match boosting alone?
4. What is the runtime overhead and which queries fail?

### 0.6 Non-negotiable rules

1. Do not fabricate data, citations, measurements, correctness labels, file hashes, or model-training claims.
2. Never use final held-out test queries/labels to develop regex rules, tune hyperparameters, or redesign the reranker. It is acceptable to use the **development** set. If any final test errors trigger changes, mark prior test as exploratory and construct a fresh held-out set before making confirmatory claims.
3. No train/test near-duplicate query leakage; fixed documents are shared across dev/test by design in retrieval benchmarks, but queries must be split by identifier families/topic where feasible.
4. Every query has an explicit human-reviewable source and relevance evidence. An agent-generated query and its source passage are not independently evaluated truth; clearly flag synthetic vs authored labels and do manual verification when possible.
5. Set deterministic seeds, record Python/library/model versions and machine CPU/GPU; keep raw outputs.
6. Reuse model weights without pretending to train the model.
7. Keep technical content and benchmark sources within permitted licenses; avoid mass scraping, paywalled sources, credentials, and proprietary user data.
8. Prefer CPU-compatible, lightweight code. Do not introduce infrastructure not needed to test the research hypotheses.
9. At each stage: implement -> test -> compare with prior checkpoint -> save stage summary and outputs -> commit (if git configured) -> advance **only if gate passes**.
10. If something is blocked, record the actual error, try the smallest practical workaround, and explain deviations in `docs/DECISIONS.md`; don't report a failed stage as complete.
11. If you are about to alter, delete, or send user/private data outside the project, stop and request explicit approval. Workspace access does not authorize unrestricted destructive operations.

---

## 1. Repository structure (target)

```text
identifier-preserving-retrieval/
├── README.md
├── pyproject.toml               # or requirements.txt + pinned lock snapshot
├── .gitignore
├── .env.example                 # only if unavoidable; no credentials required
├── configs/
│   ├── base.yaml
│   └── experiment_grid.yaml
├── src/iphr/
│   ├── __init__.py
│   ├── schemas.py
│   ├── data_io.py
│   ├── normalization.py
│   ├── lexical.py
│   ├── dense.py
│   ├── hybrid.py
│   ├── identifiers.py
│   ├── reranker.py
│   ├── metrics.py
│   ├── evaluation.py
│   ├── timing.py
│   └── cli.py
├── scripts/
│   ├── collect_technical_corpus.py
│   ├── build_benchmark.py
│   ├── validate_dataset.py
│   ├── fetch_scifact.py
│   ├── run_experiments.py
│   ├── make_figures.py
│   └── export_paper_tables.py
├── data/
│   ├── seed/                     # tiny checked-in hand-auditable sample
│   ├── technical/
│   │   ├── corpus.jsonl
│   │   ├── queries_dev.jsonl
│   │   ├── qrels_dev.tsv
│   │   ├── queries_test.jsonl
│   │   ├── qrels_test.tsv
│   │   ├── provenance.csv
│   │   └── annotation_guidelines.md
│   └── scifact/                  # downloaded; subject to license
├── cache/                        # local TF-IDF indices/embeddings, gitignored
├── tests/
│   ├── test_data.py
│   ├── test_identifiers.py
│   ├── test_retrieval.py
│   ├── test_reranker.py
│   └── test_metrics.py
├── outputs/
│   ├── dev/
│   ├── final/
│   ├── figures/
│   ├── tables/
│   ├── examples/
│   └── manifests/
└── docs/
    ├── PROJECT_CONTEXT.md
    ├── RELATED_WORK.md
    ├── METHODS.md
    ├── DATASET_CARD.md
    ├── EXPERIMENT_PROTOCOL.md
    ├── DECISIONS.md
    ├── PROGRESS.md
    ├── RESULTS_INTERPRETATION.md
    ├── LIMITATIONS.md
    ├── PAPER_OUTLINE.md
    └── HANDOFF.md
```

Gitignore downloaded model/cache and large datasets as appropriate, but keep reproducible retrieval scripts, source lists, hashes, and result CSV/JSON. Choose exact filenames once at Stage 1 and use consistently. Everything should run from a clean clone after documented downloads.

### 1.1 Contract for data files

`corpus.jsonl`: each line has `doc_id` (unique stable string), `title`, `text`, `source_url`, `source_type`, `license_note`, `family` (e.g. esp32/cve/ieee). For ranking, use a consistent `title + '\n' + text` concatenation; store both original and normalized text if useful.  
`queries_{dev,test}.jsonl`: each line has `query_id`, `text`, `query_type` (`identifier`, `natural`, optionally `near_miss`), `identifier_family`, `origin` (`human_authored`, `human_reviewed_synthetic`), and `annotation_note`.  
`qrels_{dev,test}.tsv`: `query_id`, `doc_id`, `relevance` with positive relevance `1`, non-relevant `0` for explicit audited negatives; retrieval metrics treat **unjudged documents cautiously** and acknowledge incomplete judgments.  
`provenance.csv`: `doc_id`, origin URL/commit/date, rights, local file/hash, extraction method, processing notes.  
`outputs/*/rankings.csv`: `run_id`, `dataset`, `split`, `query_id`, `method`, `doc_id`, `rank`, `raw_score`.  
`outputs/*/metrics.json`: aggregate and group-level metrics; `outputs/*/per_query.csv` for audit.

### 1.2 Model/config freeze

Default:
- Embedder: `sentence-transformers/all-MiniLM-L6-v2`, model revision/hash recorded in manifest.
- Semantic: `SentenceTransformer(...).encode_document()` and `.encode_query()`; use normalized embeddings/cosine.
- Lexical: `sklearn.feature_extraction.text.TfidfVectorizer`, fit on corpus only; optionally a char n-gram experiment **only as extra ablation**, not a silently changed main baseline.
- Hybrid: RRF with `k=60` and top-K candidate union, or full rank aggregation if small enough. Use identical document universe for every method.
- Proposed: base RRF + bounded exact-identifier reward (and optional version-family conflict penalty). Select any parameters on dev only.
- Sorting ties: stable by `doc_id` for reproducibility.

---

## 2. Stage-gated implementation plan

### STAGE 00 — Scope, feasibility, and related work | ~45–75 min
**Goal:** Lock the research question before coding.

**Tasks**
1. Read this brief and inspect current machine (Python version, available RAM, available disk, CPU/GPU, OS, existing project files).
2. Verify the official Sentence Transformers example and model license.
3. Record at least 5 real related works with exact author/title/year/URL/DOI and 2-sentence relevance/overlap; start from MiniLM/Sentence-BERT, RRF (SIGIR 2009), BEIR, hybrid retrieval, exact identifier handling.
4. Create `PROJECT_CONTEXT.md`, `RELATED_WORK.md`, `EXPERIMENT_PROTOCOL.md`, and `DECISIONS.md`.
5. Lock **primary** evaluation to a small curated technical corpus, with **secondary** SciFact if feasible. No claim that SciFact itself measures technical identifier errors.
6. Predefine selection of ranking metrics, evaluation groups, and what constitutes a mistake.

**Artifacts:** `docs/PROJECT_CONTEXT.md`, `docs/RELATED_WORK.md`, `docs/EXPERIMENT_PROTOCOL.md`, `docs/DECISIONS.md`.  
**Gate:** Another researcher could describe the question, baseline, proposed variation, datasets, and measurements without ambiguity.  
**Agent instruction:** Do not proceed to modeling without this documentation. Cite sources; distinguish established methods from experimental contributions.

### STAGE 01 — Initialize reproducible Python workspace | ~30–45 min
**Goal:** A clean local package that anyone can run.

**Tasks**
1. Create a Python virtual environment; choose compatible package versions after checking installed Python.
2. Install `sentence-transformers`, `scikit-learn`, `numpy`, `pandas`, `matplotlib`, `pytest`, `pyyaml`; optional `beir` only if needed (otherwise parse standard BEIR JSONL and qrels directly).
3. Add `pyproject.toml`, `README.md`, `.gitignore`, package skeleton and a `python -m iphr.cli --help` entrypoint.
4. Include CPU mode, seed 42, deterministic sort, and clean error messages if a model download is unavailable.
5. Save `outputs/manifests/environment.json` and dependency snapshot. Ensure no secrets or private OS paths are committed.
6. Set up git; use a short commit per completed stage.

**Commands to support (exact syntax may be refined in code):**
```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q
python -m iphr.cli --help
```
**Artifacts:** installable repository, docs for both PowerShell and Bash, manifest.  
**Gate:** Imports, CLI help, and placeholder unit tests pass; fresh-install steps are documented.

### STAGE 02 — Build auditable benchmark, seed dataset first | ~2–5 h (main uncertainty)
**Goal:** Ground-truth labels decided before model comparison.

**Design**
- **MVP feasibility milestone:** 30–50 curated passages, 6 development queries, 12 held-out queries, spanning at least 2 identifier families; this is a *pipeline smoke-test*, not sufficient evidence for strong research conclusions.
- **Target for paper:** approximately **120–250 short passages** from public documentation, **60–80 reviewed queries**: ~15–20 dev, ~45–60 final test. Include at least 20–30 identifier-sensitive test queries, 10–15 natural-language queries, and version/confusable hard negatives. If effort cannot meet targets, proceed as a smaller pilot study and explicitly state dataset size limitations.
- Suggest starting families: **Espressif chip variants** (`ESP32-S3`, `ESP32-C3`, `ESP32-S2`), **CVE identifiers** (e.g. `CVE-2024-3094` and *different valid examples*), optionally **IEEE 802.11 variants**. Do not force unfamiliar identifier families merely to increase counts.

**Tasks**
1. Find appropriately licensed and publicly retrievable primary sources. Prefer official documentation, repository READMEs with suitable licenses, or openly licensed excerpts. Record URL/date/license for every passage. Don't invent texts and then portray them as scraped documents.
2. Collect, trim, de-duplicate, and annotate passages; preserve family and source. Create confusable passages from real documentation and retain provenance, not adversarial fake facts.
3. Build queries independently of ranking predictions; query phrasing can be authored but must be clearly labeled. At least some queries should be paraphrases rather than literal doc titles.
4. Create qrels with an explicitly written relevance rubric: `relevance=1` only if the passage provides information addressing the exact requested entity/variant; a similarly named but different version alone is not relevant. A passage referencing both variants **can** be relevant if it directly answers the query.
5. For each query, review plausible documents (e.g., with simple keyword candidate pooling) and record all relevant docs found. Do **not** label merely the originating passage as the only positive; that would bias Recall and MRR.
6. Split by queries with careful control for near-duplicate paraphrases/identifier variants; avoid putting nearly identical queries into dev and test. Freeze and hash the test files before tuning.
7. Validate schema, all IDs, duplicate detection, missing documents, positive qrels, provenance, group distribution, and query/text overlap statistics. Save counts.
8. Record annotation and incompleteness limitations honestly in `DATASET_CARD.md`.

**Artifacts:** `data/technical/*`, `docs/DATASET_CARD.md`, `outputs/manifests/dataset_summary.json`, file SHA-256 hashes.  
**Gate:** All query IDs and document IDs resolve; dev/test disjoint; no unlabeled positives in intended qrels; all test queries frozen; provenance complete; both identifier and general queries present.

### STAGE 03 — Reproduce MiniLM semantic retrieval | ~45–75 min
**Goal:** A working pretrained dense baseline.

**Tasks**
1. Implement `dense.py` using official `SentenceTransformer` API. Cache document embeddings once by corpus SHA-256 and model revision.
2. Encode all queries, compute cosine similarity against the entire corpus (acceptable at this scale), stable top-K sorted by score then doc_id.
3. Write a CLI that prints a query's top 5 docs including title, URL, score, and rank.
4. Run first on the nine-sentence official toy example (or equivalent small sample); then use the local technical seed corpus.
5. Record model ID, dimension, hash/revision, CPU device, data hash and total embedding preprocessing time. Verify rank invariance on repeated calls.

**Artifacts:** `src/iphr/dense.py`, tests, sample `outputs/examples/dense_demo.json`, cache manifest.  
**Gate:** Model loads, top-K returns valid unique IDs in rank order, repeated tests match, and no fine-tuning occurs.

### STAGE 04 — Implement lexical TF-IDF baseline | ~30–60 min
**Goal:** Search by explicit terms using the same document corpus.

**Tasks**
1. Implement a fixed `TfidfVectorizer` using the same concatenated document text as dense retrieval. Document tokenizer/lowercasing and potential loss of hyphenated identifier boundaries.
2. Build sparse document vectors, transform query, rank with cosine similarity.
3. Implement consistent top-K result object and deterministic handling for out-of-vocabulary/zero-vector queries.
4. Add tests: exact-match query should rank exact-containing passage reasonably; OOV query doesn't crash; empty input is rejected; ties consistent.

**Artifacts:** `src/iphr/lexical.py`, unit tests, sample output, basic dataset results.  
**Gate:** Same I/O schema as dense; no ground-truth labels used by vectorizer.

### STAGE 05 — Implement unmodified hybrid baseline (RRF) | ~30–60 min
**Goal:** Establish a strong, honest comparison with existing techniques.

**Tasks**
1. Implement reciprocal rank fusion: `RRF(d,q) = 1/(k + r_lexical) + 1/(k + r_dense)` for docs present in both; missing-list contributions are 0. Use 1-based ranks and `k=60` predeclared. Candidate pool size: top 100 from each method or full lists for tiny corpora; document this choice.
2. Ensure duplicate candidates appear once, rank ties deterministic, and all baseline methods use the same corpus and cutoffs.
3. Save a top-10 comparison for at least 5 *development* queries (technical, natural, confusable).
4. Make a table showing cases where individual baseline rankings differ.

**Artifacts:** `src/iphr/hybrid.py`, unit tests and saved baseline rank files.  
**Gate:** Hand-calculated RRF examples exactly match the implementation; RRF is clearly attributed to Cormack et al. (2009).

### STAGE 06 — Technical identifier parser + normalizer | ~60–90 min
**Goal:** Reliably detect selected identifiers **without** retraining anything.

**Tasks**
1. In `normalization.py`, unify Unicode dash characters and whitespace, case-fold when appropriate, but **never** discard meaningful suffix/version information.
2. In `identifiers.py`, define narrowly scoped regex parsers for the **supported families only**: CVE IDs (e.g. `CVE-2024-3094`); Espressif model IDs (e.g. `ESP32-S3`, `ESP32-C3`, `ESP32-S2`); optionally IEEE Wi-Fi standards (e.g. `802.11ax`) if enough corpus coverage. Keep generic `ESP32` family distinct from an explicit S3/C3 variant.
3. Extract *canonical identifier*, *family*, *variant*, source text span. Prevent partial matching: `ESP32-S3` is not the same as `ESP32-S2`, and a document containing only `ESP32` must not count as an exact `ESP32-S3` match.
4. Detect same-family **conflicts** only if the queried exact ID is absent and the candidate document has different supported variant(s); don't over-penalize a doc mentioning multiple models including the correct model.
5. Return no extracted IDs for ordinary questions (such as “How do computers learn?”); do not infer unmentioned model IDs.

**Minimum tests**
- Detect `ESP32-S3`, `ESP32-C3`, `CVE-2024-3094`, `IEEE 802.11ax` if enabled.
- Normalize Unicode hyphen / uppercase variants.
- Do not confuse `ESP32` with `ESP32-S3`; `CVE-2024-3094` with `CVE-2024-3095`.
- Empty text / multiple identifiers / identical repeated identifiers / punctuation boundaries.
- Natural-language query -> empty identifier list.

**Artifacts:** `src/iphr/normalization.py`, `identifiers.py`, parser tests and error examples.  
**Gate:** Parser tests pass; every supported family has positive and negative examples; known limitations documented.

### STAGE 07 — Proposed identifier-aware reranker | ~45–90 min
**Goal:** Implement the one original experimental variation.

**Starting formula (design choice, not literature-discovered optimum)**

Let `H(q,d)` = unmodified hybrid RRF score. Let `M(q,d)` = fraction of explicitly queried supported identifiers exactly matched by document `d`; if none supported, define both adjustment terms as zero. Let `C(q,d)` = 1 only for an explicit same-family *wrong variant without the requested variant*, otherwise 0.

```
S_proposed(q,d) = H(q,d) + lambda_match * M(q,d) - lambda_conflict * C(q,d)
```

- `lambda_match` and `lambda_conflict` are small compared to observed RRF scale, and must be tuned on development data only.
- For **identifier-free** queries: `S_proposed(q,d) == H(q,d)` exactly.
- If all identifiers are absent from a document, **do not** assume the document is irrelevant; the underlying semantic/hybrid relevance remains. Consider a penalty only for clear contradictory same-family variants.
- Do not use manually labeled relevance or test qrels in the scorer.
- Avoid broad global score normalization that changes document ordering unpredictably. Record all final score components per result for interpretability.

**Tasks**
1. Implement exact-match bonus first (`lambda_conflict=0`); use it as an ablation.
2. Add cautiously scoped conflict handling behind a switch.
3. Provide `explain(query, document)` returning identifiers extracted from query/doc, RRF score, match fraction, conflict decision, and final score.
4. Build tests for positive/negative/confusable docs, multi-ID query, and natural-language invariant.

**Artifacts:** `src/iphr/reranker.py`, tests, `outputs/examples/reranker_explanations.json`.  
**Gate:** Reranker never changes rankings for query with zero supported identifiers; explanation reproduces final score; no model fine-tuning.

### STAGE 08 — Evaluation framework and metrics | ~60–90 min
**Goal:** Independent evaluation, not manually selected success screenshots.

**Metrics**
- `Recall@5`: for each query, fraction of **known relevant** docs found in top 5, then macro average across queries. State that incomplete qrels limit interpretation.
- `MRR@10`: reciprocal rank of the first relevant document in top 10, 0 if none, then average.
- `nDCG@10`: optional but useful with graded qrels; binary relevance is acceptable.
- `WrongIdentifier@1`: fraction of *eligible identifier-sensitive* queries whose first retrieved document contains a verified contradictory supported identifier **without the requested identifier**, and is adjudicated as a wrong-variant outcome. Clearly document the annotation policy. Report denominator; don't assume “no exact string” always means wrong.
- `Latency`: median/p95 across repeated runs, distinguishing corpus preprocessing, model load, query embedding, candidate retrieval, and extra reranking cost; state hardware, warmed/cold distinction.

**Tasks**
1. Implement metrics on artificial hand-checkable rankings first, with unit tests.
2. Save all retrieved doc IDs per query/method; ensure method results are exactly reproducible from qrels and rankings.
3. Compute group slices for identifier queries vs natural queries (and family-specific results if counts sufficient).
4. Add bootstrap confidence interval for paired query differences if sample size allows; describe small-sample limits. Do not claim statistical significance from point estimates alone.
5. Add regression tests: zero-relevant query does not throw; ties deterministic; relevant doc outside top K counted correctly.

**Artifacts:** `src/iphr/metrics.py`, `evaluation.py`, `timing.py`, tests.  
**Gate:** Every metric matches simple manually computed toy cases; no test split used to fit/tune.

### STAGE 09 — Development-only pilot and parameter selection | ~45–90 min
**Goal:** Tune the proposed method **once** without peeking at final test data.

**Tasks**
1. Run TF-IDF, MiniLM, RRF on the **dev split**; store per-query baseline rankings/metrics.
2. Try a small, predefined grid for `lambda_match`, `lambda_conflict` **on dev only**, e.g. `{0, 0.003, 0.006, 0.012}` for match and `{0, 0.003, 0.006}` for conflict, recognizing RRF scores are typically on the order of hundredths. Never choose values using final test performance.
3. Compare proposed model to RRF on dev, with desired high ranking quality and low wrong-variant rate. Evaluate the absolute effect on natural-language queries (should be exactly zero when no identifiers).
4. Decide final settings before seeing test metrics; record selection rule, including tie-breaking and how an inconclusive dev result is handled.
5. Freeze `configs/final.yaml` with SHA-256 and commit. If no improvements: keep most conservative setting and report null results, including no-op as a valid control.

**Artifacts:** `outputs/dev/grid.csv`, `outputs/dev/*.json`, `configs/final.yaml`, stage summary.  
**Gate:** Frozen config and source code version are recorded prior to final evaluation; dev-only tuning is verifiable.

### STAGE 10 — Final held-out experiments and SciFact check | ~45–90 min
**Goal:** Produce the principal evidence for the paper.

**Primary evaluation: technical documents (test only)**
1. Reuse frozen model, corpus, split, hyperparameters and seeds.
2. Run at least **five** methods (below) once per finalized test split:
   - A — TF-IDF only
   - B — MiniLM only
   - C — RRF hybrid
   - D — RRF + exact-match bonus only
   - E — RRF + exact-match bonus + conflict penalty (proposed full method)
3. Evaluate main metrics overall, by identifier vs natural query, optionally by family.
4. Compare delta to RRF, bootstrap paired-query CIs if justified, and include adverse cases.
5. Save raw rankings, per-query metrics, metric summaries, environment/data/model hashes and machine details.

**Secondary robustness check: BEIR SciFact (if dependency/data available)**
1. Download SciFact using the *official BEIR dataset link* or load its standard corpus/queries/qrels files; record source/version/license.
2. Run TF-IDF, MiniLM, RRF and proposed scoring without modifying the frozen implementation or selecting new weights on SciFact test labels.
3. Since most SciFact queries are general scientific claims rather than the target technical identifiers, identifier-aware reranking may not trigger. Report **coverage** (`% queries where parser fires`) and unchanged results honestly; never present SciFact as direct evidence of technical identifier improvement.
4. If SciFact is unavailable or would introduce major installation overhead, skip it with a documented reason; do not block primary research.

**Artifacts:** `outputs/final/metrics.json`, `outputs/final/per_query.csv`, `outputs/final/rankings.csv`, `outputs/final/scifact_*` (optional), `outputs/manifests/final_run.json`.  
**Gate:** Final run can be repeated from frozen config and produces same ranks (allow small platform-specific timing noise). No invented gains.

### STAGE 11 — Figures, ablations, errors, limitations | ~60–120 min
**Goal:** Convert raw results into defensible figures and reportable observations.

**Required research figures**
1. Architecture flow diagram (MiniLM + TF-IDF -> RRF -> parser/reranker -> rankings).
2. Grouped bar chart of Recall@5 / MRR@10 for methods on identifier-sensitive test queries (separate metric panels or figures; do not combine unrelated units on same axis).
3. WrongIdentifier@1 across RRF, bonus only, proposed full method (with denominator).
4. Latency comparison distinguishing query runtime from one-time embedding/index cost.
5. At least one per-query **case-study table** with a success, a failure, and a natural-query no-change example.

**Required ablations**
- RRF only
- + exact-match bonus
- + conflict penalty
- zero-supported-ID queries should match original RRF exactly

**Tasks**
1. Generate figures directly from saved CSV/JSON; no hand-entered result numbers.
2. Export high-resolution SVG/PNG and LaTeX/CSV tables with axis labels, sample sizes, seeds.
3. Summarize what improved and **what became worse**. Identify artifacts of dataset sampling, qrel incompleteness, regex family coverage, and small-sample uncertainty.
4. Produce `docs/RESULTS_INTERPRETATION.md`, `LIMITATIONS.md`, and `METHODS.md` complete with equations and reproducibility parameters.

**Artifacts:** `outputs/figures/*`, `outputs/tables/*`, interpretive docs.  
**Gate:** Every plotted number traces back to a stored run file; no graph represents hypothetical numbers as real.

### STAGE 12 — Paper-ready reproducibility bundle, optional tiny demo | ~60–120 min
**Goal:** Hand over the finished research project, ready to become an IEEE-style report.

**Tasks**
1. Write `docs/PAPER_OUTLINE.md` with: Abstract outline (fill numerical claims only from results), Introduction, Related Work, Methodology, Dataset/Annotations, Baselines, Experimental Settings, Results/Ablation, Discussion, Limitations, Conclusion, References.
2. Write `docs/HANDOFF.md`: exact install/setup commands; how to rebuild technical dataset; how to download SciFact; one command to reproduce all metrics/figures; data/model/code checksums; list of known limitations; what was not run.
3. Add `python -m iphr.cli search --query 'ESP32-S3 Wi-Fi CSI' --method proposed --top-k 5 --explain` (or equivalent) using the indexed corpus. Print identifiers, sources, scores and match decisions.
4. Run test suite and reproducibility smoke test from a clean venv or clean package reinstall.
5. Optional one-page Streamlit demo **only if all research gates pass and user wants it**. Do not spend research time building UI by default.
6. Produce concise end-of-project status: method actually implemented, dataset sizes, baseline/proposed measurements (actual), all output locations, limitations, and paper content ready.

**Artifacts:** documentation, command-line demo, complete output bundle, git commit.  
**Gate:** Clean-install instructions run; paper outline maps to actual datasets/experiments; all factual claims are supportable.

---

## 3. Checkpoint and logging contract

At the end of **every** stage `NN`, update `docs/PROGRESS.md` with:

```markdown
### Stage NN — <name>
- Status: PASS | BLOCKED | PARTIAL
- Date/time:
- Work completed:
- Files created/modified:
- Commands executed:
- Test command and output summary:
- Measured results (if any):
- New decisions / deviations from scope:
- Risks and unresolved problems:
- Next exact stage:
- Commit hash (if Git available):
```

Save machine-readable `outputs/manifests/stage_NN.json` with the same information where possible. On a `BLOCKED` gate, do not silently skip to subsequent modeling and claim success. If a contingency is needed, document it first.

**Suggested Git tags**: `checkpoint/00-scope`, `checkpoint/02-data`, `checkpoint/05-baselines`, `checkpoint/07-reranker`, `checkpoint/09-frozen`, `checkpoint/10-results`, `checkpoint/12-final` (use normal names or commits if slash-containing tags are inconvenient).

---

## 4. Minimum acceptance checklist

- [ ] Official pretrained MiniLM loads and ranks documents; no model training was performed.
- [ ] TF-IDF and MiniLM run against **the same corpus** with identical document IDs.
- [ ] RRF baseline is implemented and passes hand-verified ranking tests.
- [ ] Technical identifier parser is correct for supported IDs and wrong variants.
- [ ] Proposed reranker is deterministic and explainable.
- [ ] Identifier-free queries produce the **same ranking** under RRF and proposed method.
- [ ] Technical dataset has actual public-source provenance and documented relevance labels.
- [ ] Dev/test queries are disjoint and final test was held out until freeze.
- [ ] Comparisons include TF-IDF, MiniLM, RRF, bonus-only and bonus+conflict.
- [ ] Results include Recall@5, MRR@10, wrong-identifier@1, and latency, with denominators.
- [ ] Outputs include saved per-query rankings, metrics, plots, tables, environment and hashes.
- [ ] A failure case and an adverse result are reported, if any.
- [ ] IEEE paper outline distinguishes cited background from work executed here.
- [ ] Clean setup and reproduction commands are included.

---

## 5. Planned time budget (estimates, not promises)

| Stage | Estimate | Main risk |
|---|---:|---|
| 00 Scope & literature | 0.75–1.25 h | Distinguishing prior work |
| 01 Environment | 0.5–0.75 h | OS/Python packages |
| 02 Benchmark/data | 2–5 h | Rights, labeling quality, difficult negatives |
| 03 MiniLM | 0.75–1.25 h | Initial model download |
| 04 TF-IDF | 0.5–1 h | Text normalization |
| 05 RRF | 0.5–1 h | Candidate pooling |
| 06 Parser | 1–1.5 h | Confusable versions |
| 07 Reranker | 0.75–1.5 h | Bonus scale/conflicts |
| 08 Metrics | 1–1.5 h | Qrel interpretation |
| 09 Dev tuning | 0.75–1.5 h | Selection without peeking |
| 10 Test runs | 0.75–1.5 h | Evaluation reproducibility |
| 11 Figures & interpretation | 1–2 h | Honest failure analysis |
| 12 Paper-ready handoff | 1–2 h | Packaging |
| **Total** | **~11–22 h** | **Data curation may take longer** |

The earlier 10–16-hour estimate is plausible for an MVP, but **a credible labeled benchmark and final paper bundle can take longer**, especially if human adjudication is needed. Avoid optimizing for an arbitrary deadline at the cost of evidence quality.

---

## 6. Ready-to-paste Terra controller prompt

Paste the block below into Terra with this entire Markdown file available to it:

```text
You are the engineering and research execution agent for the project
"Evaluating Identifier-Preserving Hybrid Retrieval for Technical Document Search."

Read TERRA_RESEARCH_PROJECT_PLAN.md from start to finish, especially the
scope-of-claim, dataset-labeling, held-out-evaluation, and checkpoint rules.

Implement the project in the current workspace, sequentially, using stages
00 through 12. Treat each stage as a gated mini-deliverable.

FOR EVERY STAGE:
1. Read its exact objective, tasks, artifacts, tests, and PASS gate.
2. Inspect existing code/data before modifying anything.
3. Implement the smallest complete working change.
4. Run relevant tests; fix failures; do not fake success.
5. Save raw evidence, outputs, and progress in the specified project paths.
6. Update docs/PROGRESS.md and docs/DECISIONS.md with actual commands,
   test results, limitations, and next stage.
7. Commit a coherent checkpoint if Git is configured.
8. Advance to the next stage only when the current gate passes.

Prioritize a CPU-compatible research pipeline, not UI polish. Start with
MiniLM + TF-IDF + unmodified RRF, then implement the identifier-aware
reranker. Use a small auditable technical benchmark, freeze held-out test
queries before parameter tuning, and never tune on final test labels.

Do not invent research results, sources, citations, labeled qrels, or
training procedures. Include negative/failure cases and unchanged queries.
Do not claim semantic search, hybrid fusion, identifier preservation, or RRF
is newly invented. No paid services, secrets, destructive operations,
or proprietary data. Any use of downloaded content needs provenance and
license review. If access is insufficient for independent human relevance
adjudication, report the dataset as agent-curated/pilot and its limitations.

Begin with Stage 00. At each checkpoint, give a concise completion report
and the exact next action. Continue independently through the next stage
when permitted and the PASS gate is satisfied; otherwise stop at the blocker
and document it. At completion provide executable reproduction commands,
summary metrics read from files, and locations of all research artifacts.
```

### Optional stage-specific prompt for manual control

If you want to limit the agent to one stage per run, paste:

```text
Use TERRA_RESEARCH_PROJECT_PLAN.md as the single implementation contract.
Execute ONLY STAGE [NN]. First inspect the previous stage's artifacts and
PASS gate. Implement all tasks for this stage, run its tests, save all outputs,
update PROGRESS.md / DECISIONS.md, and make a checkpoint commit. Then stop
and report exact file paths, tests, status, blockers, and the next stage.
Do not start Stage [NN+1] until asked.
```

---

## 7. Initial package references and bibliography seeds

Use actual authors/DOIs verified from publisher/official source. Start here:

1. Sentence Transformers official GitHub: https://github.com/huggingface/sentence-transformers
2. Official semantic search example: https://github.com/huggingface/sentence-transformers/blob/main/examples/sentence_transformer/applications/semantic-search/semantic_search.py
3. `all-MiniLM-L6-v2` model card and license: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
4. Current encode-query and encode-document API: https://www.sbert.net/docs/package_reference/sentence_transformer/SentenceTransformer.html
5. BEIR repository: https://github.com/beir-cellar/beir
6. BEIR datasets (SciFact): https://github.com/beir-cellar/beir/wiki/Datasets-available
7. SciFact dataset card: https://huggingface.co/datasets/BeIR/scifact
8. RRF: Cormack, Clarke & Buettcher, SIGIR 2009, https://doi.org/10.1145/1571941.1572114

**Literature-search terms:** `technical identifier retrieval exact match dense sparse`, `entity-aware hybrid retrieval`, `version-sensitive retrieval`, `lexical semantic fusion`, `robustness document search technical ids`, `query adaptive dense sparse retrieval`. Prior-art evaluation must predate claims of novelty. Do not invent or pad references.

---

## 8. Definition of "done"

The project is done only when **code, data, labels, evaluation, comparisons, plots, limitations, and reproducibility instructions** exist and agree with one another. An attractive CLI/demo without held-out evidence is not a finished research project. Strong results are not required; valid results are.
