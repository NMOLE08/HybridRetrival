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
