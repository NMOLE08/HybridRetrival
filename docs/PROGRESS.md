# Progress

### Stage 00 — Scope, feasibility, and related work
- Status: PASS
- Date/time: 2026-10-18 (Asia/Kolkata)
- Work completed: Read full blueprint, inspected workspace and machine; verified official example and model-card license; documented research scope, seven related works and protocol before implementation.
- Files created: PROJECT_CONTEXT.md, RELATED_WORK.md, EXPERIMENT_PROTOCOL.md, DECISIONS.md, PROGRESS.md, UPDATES.md, outputs/manifests/stage_00.json.
- Commands: `python --version`; `git --version`; Windows CIM machine, processor, GPU and disk queries; web checks of official sources.
- Verification: Documentation covers research question, datasets, baselines, formula, metrics, mistake policy and holdout; five or more independently attributable papers documented. No measurements or dataset judgments asserted.
- Measured results: Hardware and storage only, in PROJECT_CONTEXT.md.
- Decisions: CPU; no training; technical primary, optional SciFact; development-only selection; prior art not claimed as novel.
- Risks: Human independent review unavailable so far; dataset sourcing and model download remain unverified.
- Next exact stage: Stage 01 reproducible workspace.
- Commit hash: 5044286 (Git initialized subsequently with a local Codex checkpoint author).

### Stage 01 — Reproducible Python workspace
- Status: PASS (workspace gate); model download and deterministic ranking are validated at their implementation stages.
- Date/time: 2026-10-18 (Asia/Kolkata)
- Work completed: Initialized Git and virtual environment; installed package and dependencies; documented PowerShell/Bash setup and recorded dependency/environment snapshot. CPU and seed defaults are configured.
- Files created/modified: pyproject.toml, README.md, .gitignore, configs/base.yaml, src/iphr/, tests/test_smoke.py, requirements.lock.txt, outputs/manifests/environment.json, docs/IMPLEMENTATION_PLAN.md, UPDATES.md.
- Commands: `python -m venv .venv`; `.venv\Scripts\python.exe -m pip install -e '.[dev]'`; `python -m pip freeze`; imports of all declared dependencies; `python -m iphr.cli --help`.
- Test: `.venv\Scripts\python.exe -m pytest -q` — 1 passed; CLI help and all imports succeeded; sentence-transformers 5.7.0 and torch 2.14.1+cpu imported.
- Measured results: no retrieval measurements.
- Decisions / deviations: Snapshot excludes the local editable install path. Git uses a local Codex author because user identity is unset; no global Git settings changed. Model loading and ranking error handling cannot be verified until Stage 03.
- Risks: pip installation was unusually slow; full clean reinstall remains for Stage 12. Model and source availability remain untested.
- Next exact stage: Stage 02 benchmark and provenance.
- Commit hash: see Git history (stage checkpoint).

### Stage 02 — Auditable benchmark (work in progress)
- Status: PARTIAL; gate not met.
- Date/time: 2026-10-18 (Asia/Kolkata).
- Work completed: Inspected official CVE repository and rights notice; identified ten Espressif SoC source files with explicit `Apache-2.0 OR MIT` headers. Fetched 21 CVE records and 10 SoC header files at fixed commits into ignored local cache, recorded source URLs and SHA-256 hashes. Built a structural dataset validator and source fetcher. These source files are candidates, not a corpus or relevance judgments.
- Files created/modified: scripts/collect_technical_corpus.py, scripts/validate_dataset.py, tests/test_source_discovery.py, tests/test_data_validation.py, outputs/manifests/source_discovery.json, UPDATES.md.
- Commands: `.venv\Scripts\python.exe scripts\collect_technical_corpus.py`; `.venv\Scripts\python.exe scripts\validate_dataset.py data\technical`; `.venv\Scripts\python.exe -m pytest -q`.
- Test results: collector fetched 31 records; pytest 3 passed. Validator correctly rejected the currently absent benchmark files. Initial pytest run encountered WinError 5 accessing an existing system temporary directory; changed test to avoid requiring that directory and reran successfully.
- Measured results: none; no retrieval experiments run.
- Decisions: CVE content is not assumed public domain; preserve applicable terms and copyright notices before redistributing. Espressif documentation license was not assumed from source-code notices; candidate source headers have explicit SPDX declarations. Candidate source list is exploratory and not a frozen benchmark.
- Risks and unresolved problems: No curated passages, source-specific redistribution notices, relevance judgments, query split, near-duplicate audit, held-out hashes, or independent human review exist. The candidate records include code as well as technical vulnerability descriptions and require assessment for study suitability. Structural validation cannot confirm semantic correctness or exhaustive judgments.
- Next exact action: Review source rights and 31 candidates; construct a small short-passage pilot and explicitly agent-authored dev/test queries; review every plausible positive and hard negative against evidence; complete provenance, freeze and hash the test split, and pass the Stage 02 validation and review gate before Stage 03.
- Commit: see Git history for partial checkpoint.

### Stage 02 — Pilot benchmark freeze
- Status: PASS for the plan's small pilot gate, with incomplete judgments and no independent review; not a paper-scale benchmark.
- Date/time: 2026-10-18 (Asia/Kolkata).
- Work completed: Created 31 source-derived passages, 6 dev and 12 held-out test queries, source-backed positive and audited negative qrels, annotation evidence, provenance and license notices. Assessed exact CVE cross-references across the corpus and added the Log4j cross-reference as a second positive. Per-chip source-code snippets retain their original lines. Recorded dev/test query overlap, hashes and limitations before any model or ranking comparisons.
- Files: data/technical/, docs/DATASET_CARD.md, scripts/build_benchmark.py, tests/test_pilot_data.py, .gitattributes, outputs/manifests/dataset_summary.json.
- Commands: `python scripts/collect_technical_corpus.py`; `python scripts/build_benchmark.py`; `python scripts/validate_dataset.py data/technical`; `python -m pytest -q`; rebuilt and checked every recorded file hash.
- Verification: Validator passed, 5 tests passed, rebuilt files matched recorded SHA-256 hashes. No repeated query IDs or exact text between splits; maximum token Jaccard 0.3125, not proof of semantic independence.
- Measured results: 31 passages; dev 5 identifier / 1 natural, test 10 identifier / 2 natural. Dev has 6 positive and 10 explicit negative judgments; test has 13 positive and 17 explicit negatives; all other pairs are unjudged. No retrieval measurements.
- Decisions / limitations: Pilot below paper target; agent-authored, source-conditioned queries and non-independent labels; source code snippets in addition to prose. Exact corpus coverage does not prove all relevant judgments have been found; unjudged pairs are not treated as explicit negatives. CVE current terms were checked in site bundle and notices included. The plan's human-origin-only schema was extended with `agent_authored` to avoid misrepresentation.
- Next exact stage: Stage 03 pretrained MiniLM semantic baseline; test split and qrels remain frozen and unused for model/rule design or tuning.
- Commit hash: see Git history for Stage 02 freeze checkpoint.

### Stage 03 — Pretrained MiniLM semantic baseline
- Status: PASS.
- Date/time: 2026-10-18 (Asia/Kolkata).
- Work completed: Implemented CPU sentence-transformer retrieval with normalized document/query embeddings, stable doc_id ties, corpus/model/library-version keyed cache and search CLI. Loaded the unmodified pretrained model, ran an equivalent nine-sentence synthetic toy and one development query twice; no training or final-test labels used.
- Files: src/iphr/dense.py, data_io.py, cli.py, scripts/dense_demo.py, tests/test_dense.py, outputs/examples/dense_demo.json, outputs/manifests/dense_cache.json and stage_03.json.
- Commands: `python scripts/dense_demo.py`; `python -m iphr.cli search --query <dev-query> --method dense --top-k 5`; `python -m pytest -q`.
- Test results: 7 passed. Nine-sentence toy returned unique ranked IDs; repeated development query order matched in-process and in separate CLI execution.
- Measured results: dimension 384; initial local cached-model load 1.468 s and technical preprocessing 3.779 s on CPU (single run, not a latency benchmark). Development query dev01 ranked its known source passage first. No prior retrieval baseline exists yet and this example is not aggregate evidence.
- Decisions: Model revision and safetensors SHA-256 recorded in dense_cache.json; cache is ignored. Model fetch used public unauthenticated access; Windows symlink warning did not prevent download.
- Risks: Small biased pilot and incomplete judgments; MiniLM truncates long inputs according to its model configuration; true latency will be measured later.
- Next exact stage: Stage 04 TF-IDF baseline.
- Commit: see Git history.

### Stage 04 — Lexical TF-IDF baseline
- Status: PASS.
- Date/time: 2026-10-18 (Asia/Kolkata).
- Work completed: Added corpus-only scikit-learn TF-IDF and cosine scoring with the same title/newline/text representation and result schema as dense retrieval; CLI supports lexical search. Default word tokenizer lowercases and splits hyphenated identifiers, a known limitation.
- Files: src/iphr/lexical.py, cli.py, tests/test_lexical.py, outputs/examples/lexical_demo.json, outputs/manifests/stage_04.json.
- Commands and tests: `python -m pytest -q` (9 passed); lexical CLI query and development smoke-test saved to lexical_demo.json. Exact-containing passage ranked first in unit test; OOV scores tie at zero and sort by ID; empty input rejected.
- Baseline comparison: for dev01 both TF-IDF and the prior MiniLM example rank the known source first; their fourth and fifth results differ. This is one example, not a measured improvement or aggregate study.
- Decisions / risks: Vectorizer fits only the corpus without qrels, default two-character word tokenization; test labels remain untouched. No broad effectiveness conclusions.
- Next exact stage: Stage 05 standard RRF.
- Commit: see Git history.

### Stage 05 — Unmodified RRF hybrid baseline
- Status: PASS.
- Date/time: 2026-10-18 (Asia/Kolkata).
- Work completed: Implemented standard RRF with 1-based ranks, k=60, full rankings over the 31-document universe, zero contribution for missing lists, and deterministic doc_id tie breaks. Saved complete lexical, MiniLM and RRF rankings for all six development queries plus a top-10 comparison and top-1 table.
- Files: src/iphr/hybrid.py, tests/test_hybrid.py, scripts/run_dev_baselines.py, outputs/dev/baseline_rankings.csv, baseline_comparisons.json, baseline_top1_comparison.csv.
- Commands/tests: `python -m pytest -q` (11 passed); `python scripts/run_dev_baselines.py` (558 ranking rows). Hand-computed RRF scores and partial-list behavior passed.
- Comparison: TF-IDF and MiniLM top results differ on 2/6 development queries; for dev04 their first IDs differ and RRF ranks the corresponding known source first. This is a tiny descriptive pilot observation, not final evaluation.
- Decisions: Full lists used at this corpus size; RRF attributed to Cormack, Clarke and Buettcher (2009). No final-test labels used.
- Risks: Source-conditioned queries and incomplete qrels; performance is not established by this comparison.
- Next exact stage: Stage 06 supported identifier parsing.
- Commit: see Git history.

### Stage 06 — Identifier parser and conflict rules
- Status: PASS.
- Date/time: 2026-10-18 (Asia/Kolkata).
- Work completed: Implemented one-codepoint Unicode-dash normalization and extraction of explicit CVEs and ESP32 C/S/H/P numeric variants, including a distinct generic ESP32 token and original source spans. Repeated identifiers are deduplicated. Added conservative same-family conflict checks; a generic ESP32 is not an explicit wrong variant and a passage containing any requested family variant is not penalized for mentioning others.
- Files: src/iphr/normalization.py, identifiers.py, tests/test_identifiers.py, outputs/examples/identifier_examples.json, outputs/manifests/stage_06.json.
- Commands/tests: `python -m pytest -q` (14 passed); saved parser examples. Tests cover Unicode dashes, case, spans, CVE and ESP variants, malformed suffix boundaries, duplicates, multiple IDs and natural language.
- Baseline comparison: No ranking scores changed in this stage; the RRF checkpoint remains intact.
- Decisions / limitations: IEEE Wi-Fi identifiers and arbitrary devices are not supported; parser does not infer identifiers. Family-level handling deliberately avoids conflict for a multi-ID query when at least one requested ID of that family occurs. Generic ID matching is distinct from variant matching.
- Next exact stage: Stage 07 identifier-aware score adjustment.
- Commit: see Git history.

### Stage 07 — Identifier-aware reranker
- Status: PASS.
- Date/time: 2026-10-18 (Asia/Kolkata).
- Work completed: Added explainable RRF + match-fraction bonus − same-family conflict penalty, with independently selectable nonnegative weights. Explanation records extracted identifiers, match fraction, conflict, base score and score components. Relevance labels never enter the scorer.
- Files: src/iphr/reranker.py, tests/test_reranker.py, outputs/examples/reranker_explanations.json, outputs/manifests/stage_07.json.
- Commands/tests: `python -m pytest -q` (17 passed); generated two dev-only explanations using illustrative 0.003 weights. Positive, confusable, generic, multiple-ID and natural-query cases verified.
- Baseline comparison: for dev04 the illustrative adjustment changes the RRF full order; for identifier-free dev06 it preserves the entire RRF ordering. This is a functional demonstration, not parameter selection or an effectiveness claim.
- Decisions / risks: Weights in the example are illustrative; no hyperparameters selected. Family-level conflicts are deliberately conservative. Test labels remain held out.
- Next exact stage: Stage 08 metrics and evaluation infrastructure.
- Commit: see Git history.

### Stage 08 — Metrics and evaluation
- Status: PASS.
- Date/time: 2026-10-18 (Asia/Kolkata).
- Work completed: Implemented known-positive Recall@5, MRR@10, binary nDCG@10, adjudicated wrong-identifier@1, grouped summaries, paired bootstrap and warmed wall-clock timing. Added a command that regenerates metrics from saved rankings and qrels.
- Files: src/iphr/metrics.py, evaluation.py, timing.py, scripts/evaluate_rankings.py, tests/test_metrics.py, tests/test_evaluation_io.py, outputs/manifests/stage_08.json.
- Commands/tests: `python -m pytest -q` (21 passed). Hand calculations cover cutoffs, no positives, reciprocal rank, nDCG, unknown/adjudicated wrong variants and reproducible paired bootstrap; a toy saved ranking was evaluated twice with byte-identical metric output.
- Baseline comparison: Framework only; no aggregate development or test evaluation performed in this stage.
- Decisions: Contradictory but unjudged top documents are explicitly unknown; report lower/upper wrong-identifier bounds and denominator. Before grid tuning, clarified that the existing wrong-ID tie-break uses the conservative upper bound.
- Risks: Incomplete qrels and tiny per-group samples severely limit confidence interval and error-rate interpretation. No test tuning or model training.
- Next exact stage: Stage 09 development-only grid and parameter freeze.
- Commit: see Git history.

### Stage 09 — Development-only grid and freeze
- Status: PASS.
- Date/time: 2026-10-18 (Asia/Kolkata).
- Work completed: Evaluated 12 predeclared weight pairs on the six dev queries, verified identifier-free invariance at every pair, applied the predeclared tie-break, and froze config and hashes before any test evaluation. Saved development rankings, per-query metrics, group summaries and grid.
- Files: scripts/run_dev_grid.py, configs/final.yaml, outputs/dev/grid.csv, rankings.csv, per_query.csv, metrics.json, outputs/manifests/dev_freeze.json and stage_09.json.
- Commands/tests: `python scripts/run_dev_grid.py`; `python -m pytest -q` (21 passed). Test files checked by SHA-256 only.
- Measured dev results: On five identifier queries, RRF MRR@10 = 1.0 and Recall@5 = 1.0, wrong-ID upper bound = 0/5. All 12 weight pairs tie on these selection metrics; conservative tie-break chooses lambda_match = 0 and lambda_conflict = 0. Thus the selected proposed scorer is a no-op; no gain can be inferred.
- Decision: Before test evaluation, also freeze the smallest nonzero grid weights (0.003, 0.003) for explicitly exploratory match-only and match+penalty sensitivity contrasts. The selected no-op remains the primary method. This exploratory addition was made after observing the dev tie and must not be represented as an independent confirmatory test.
- Risks: Only five identifier dev queries and one natural query; perfect dev scores and agent-created labels give no basis to infer generalization.
- Next exact stage: Stage 10 held-out evaluation using this committed config and implementation.
- Commit: see Git history for the config freeze commit.

### Stage 10 — Held-out experiments and optional SciFact check
- Status: PASS for the primary acceptance gate; the optional secondary evaluation was stopped and deferred due to substantial CPU indexing time.
- Date/time: 2026-10-18 (Asia/Kolkata).
- Work completed: Ran the frozen methods on all 12 held-out technical queries; repeated all rankings before reading test judgments and reconstructed the metric summaries from the stored ranking file. Downloaded the official SciFact archive with TLS verification through the system trust store, checked the published MD5 and recorded SHA-256 hashes.
- Files: `scripts/run_experiments.py`, `scripts/evaluate_rankings.py`, `scripts/fetch_scifact.py`, `scripts/run_scifact.py`, `outputs/final/`, and the final-run and SciFact download manifests.
- Commands/tests: `python scripts/run_experiments.py`, `python scripts/evaluate_rankings.py` (separate reconstruction), `python scripts/fetch_scifact.py`, `python scripts/run_scifact.py` (stopped during CPU indexing after more than 15 minutes without query results), and `python -m pytest -q` (21 passed).
- Primary results: On the 10 identifier queries, RRF and the selected proposed method both have MRR@10 0.875, Recall@5 1.0, and one observed wrong identifier with one unknown outcome. The dev-selected weights are both zero. The fixed nonzero sensitivity method has MRR@10 1.0, but is exploratory; its paired bootstrap MRR difference against RRF is 0.125 with percentile interval [0, 0.3] across only 10 queries.
- Risks: The pilot's agent-authored, source-conditioned queries and non-independently reviewed, incomplete labels limit generalization. Timing is sequential CPU component timing, not end-to-end latency. SciFact is not direct evidence about technical identifiers.
- Next exact stage: Stage 11 figures and analysis. The optional SciFact run may be restarted separately; its completion is not required for the primary acceptance gate.
- Commit: see Git history for the frozen runner and primary results checkpoints.

### Stage 11 — Figures, ablations, cases and limitations
- Status: PASS.
- Date/time: 2026-10-18 (Asia/Kolkata).
- Work completed: Generated five SVG/PNG figures and CSV/LaTeX tables directly from saved run files; documented mathematical methods, observed comparisons, error cases and limitations. The case table includes an RRF failure, exploratory success and natural-query invariance. Inspected the rendered architecture and effectiveness charts.
- Files: `scripts/make_paper_artifacts.py`, `outputs/figures/`, `outputs/tables/`, `docs/METHODS.md`, `docs/RESULTS_INTERPRETATION.md`, `docs/LIMITATIONS.md`, `outputs/manifests/stage_11.json`.
- Commands/tests: `python scripts/make_paper_artifacts.py` (all artifacts generated), `python -m pytest -q` (21 passed).
- Measured results: Selected full and bonus methods exactly match RRF; both exploratory nonzero variants yield the same pilot metrics. The experimental penalty has no demonstrated incremental benefit. Paired exploratory MRR interval [0, 0.3] includes zero.
- Decisions / risks: No fixed-variant decrease in per-query MRR is observed on these few queries; it would be misleading to fabricate one. A real selected-method failure is shown instead. Graphs report wrong-ID uncertainty and distinguish measured component and one-time timings.
- Next exact stage: Stage 12 CLI, paper outline, handoff, installation and reproducibility checks. Optional SciFact CPU run is deferred.
- Commit: see Git history.

### Stage 12 — Reproducibility bundle and handoff
- Status: PASS for the primary research bundle; optional SciFact remains deferred as described in Stage 10.
- Date/time: 2026-10-18 (Asia/Kolkata).
- Work completed: Added IEEE-style paper outline, complete handoff, an explainable proposed-method CLI and a one-command rerun that writes to a new directory, verifies frozen hashes, compares reference rankings/metrics and regenerates figures. Updated README and references. No user interface was requested or added.
- Files: `docs/PAPER_OUTLINE.md`, `docs/HANDOFF.md`, `README.md`, `src/iphr/cli.py`, `scripts/reproduce.py`, the output-directory support in experiment/figure runners, and `outputs/manifests/repro_verification.json`.
- Commands/tests: `python -m pip install -e . --no-deps` (clean package reinstall using installed dependencies), `python -m pytest -q` (21 passed), `python scripts/reproduce.py` (2,604 rankings and metrics reproduced, figures generated), and `python -m iphr.cli search --query 'ESP32-S3 Wi-Fi CSI' --method proposed --top-k 5 --explain` (passed; top result esp32s3 and decisions shown).
- Measured results: The primary selected method remains identical to RRF; numerical findings and exploratory bounds remain those recorded in Stage 10.
- Risks: This verifies a clean package reinstall, not an entirely new machine. The technical pilot and its non-independent annotations are not sufficient for broad paper claims. Optional SciFact indexing requires substantial CPU time and is not required by the primary gate.
- Next exact step: independent human annotation, expanded benchmark and new untouched final test for any paper-grade effectiveness claim; complete SciFact separately if desired.
- Commit: see Git history.

### Stage 13 — Phase 1 audit and Phase 2 protocol
- Status: PASS after the protocol checkpoint is committed; the Phase 1 baseline reproduction matched.
- Date/time: 2026-10-19 12:07 (Asia/Kolkata).
- Work completed: Created `phase2` from reference `60405f7`; audited 54 protected tracked Phase 1 artifacts; wrote preregistered hypothesis, sample targets, source rights policy, split and annotation rules, development-only grid and review gates.
- Files: `docs/PHASE2_PROTOCOL.md`, `docs/PHASE2_HISTORY.md`, `configs/phase2_protocol.yaml`, `scripts/audit_phase1.py`, `outputs/phase2/manifests/`, `outputs/phase2/logs/`, `.gitattributes`, decisions and updates.
- Commands/tests: `.venv\Scripts\python.exe -m pytest -q` (21 passed; one pytest-cache permission warning); offline `.venv\Scripts\python.exe` execution of `scripts/reproduce.py` (2,604 rows and metric summaries matched, figures regenerated); `python scripts/audit_phase1.py` (54 protected files match reference); YAML/grid/target assertions passed.
- Comparison: The Phase 1 reproduction matches stored rankings and metrics. No Phase 2 retrieval or tuning has occurred. Previous selected weights remain (0,0), and the prior nonzero pilot comparison remains exploratory.
- Sources/rights: Prospective CVE and Espressif materials require source-specific verified reuse rights and preserved notices; uncertain rights are excluded. No new documents have been acquired.
- Risks: Independent human review is not yet available or assumed. The original test was inspected and cannot serve as the Phase 2 holdout. The full dataset and query targets are prospective only.
- Next exact stage: Stage 14 only after the protocol is committed; then source collection, new split and review package before any dev selection.
- Commit: see the Stage 13 Git checkpoint.

### Stage 14 — Enlarged benchmark (in progress)
- Status: IN PROGRESS; no acceptance gate claimed.
- Date/time: 2026-10-19 (Asia/Kolkata).
- Work completed: Before inspecting newly collected source passages or rankings, drafted 70 agent-authored information needs (18 identifier/6 natural dev, 34 identifier/12 natural test); selected new CVE entities and split ESP variants. Queries are explicitly unreviewed and their factual premises, topic separation and relevance remain unverified. An initial draft was preserved when hardware-topic allocation was revised before source access.
- Files: `scripts/draft_phase2_needs.py`, `data/phase2/needs_draft.jsonl`, `outputs/phase2/drafts/needs_initial.jsonl`.
- Commands/tests: `python scripts/draft_phase2_needs.py`; draft counts inspected. No Phase 2 retrieval was run.
- Source rights: Official CVE repository points to CVE Program terms; Espressif per-file license headers must be checked for each source. No new passages collected yet.
- Risks: Draft wording is agent-authored, so it is not independent human query authorship or independent relevance judgment; may contain false assumptions or semantic overlap. The Apache CVE pair stays within test but must be checked for cross-references.
- Next exact action: checkpoint these question-first drafts, then collect and hash official sources and validate evidence and licensing. Never infer relevance from draft query text.
- Commit: see Phase 2 Git history.
