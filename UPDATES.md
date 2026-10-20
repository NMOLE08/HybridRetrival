# Project updates

This file is the plain-language status log. Detailed stage records and commands are in [docs/PROGRESS.md](docs/PROGRESS.md).

## 2026-10-18 — Stage 00 complete
Read the full project blueprint and checked the machine and official research references. Established the research question, comparison methods, held-out evaluation rules, error definition, and development-only tuning policy. No model has been trained or experiment run. Next: initialize the reproducible Python environment and Git workspace, then build a licensed and auditable benchmark before any modeling.

## 2026-10-18 — Stage 01 complete
Initialized Git and saved Stage 00 as commit 5044286. Created the package skeleton and a Python virtual environment, installed dependencies, verified imports and CLI help, and passed the initial smoke test (1 passed). Recorded dependency and machine details. Dataset creation and retrieval experiments have not yet started. Next: Stage 02, source-backed benchmark and relevance review.

## 2026-10-18 — Stage 02 started, not yet complete
Located 31 candidate records from official CVE and Espressif repositories, pinned their source revisions, and recorded SHA-256 hashes. Created a repeatable source fetcher and a validator for dataset structure; the test suite currently has 3 passing tests. The source records are not yet a benchmark: the short passages, relevance judgments, separate development and test queries, rights notices, and test freeze still need to be completed and reviewed. No model, baseline or experimental result exists yet.

## 2026-10-18 — Stage 02 pilot completed
Built and froze a small, auditable benchmark: 31 source-derived passages, 6 development queries and 12 test queries. Source links, notices, hashes, judgments and evidence are included. A related Log4j record was correctly included as an additional positive instead of assuming only the source passage was relevant. Structural validation and five tests pass; rebuilding produces identical file hashes.

This is a smoke-test pilot, not a paper-sized dataset: queries and labels are agent-created and have not received independent human review, and many document pairs are unjudged. The held-out test set must remain untouched until the scoring method and parameters are frozen. Next: Stage 03, reproduce pretrained MiniLM retrieval.

## 2026-10-18 — Stage 03 complete
Downloaded and verified the existing pretrained MiniLM model, recorded its revision and weight hash, and implemented deterministic CPU semantic search with cached document embeddings. An equivalent toy example and one development query produced stable rankings; the known source passage ranked first for that query. This is a smoke test, not a performance claim. Seven tests pass. Next: the TF-IDF baseline.

## 2026-10-18 — Stage 04 complete
Implemented and tested TF-IDF search on the same 31 passages as MiniLM. On the first development example both methods place the known source first but produce different lower-ranked results; this single query is not an overall comparison. Nine tests pass. Next: standard RRF hybrid retrieval.

## 2026-10-18 — Stage 05 complete
Implemented and hand-checked standard RRF hybrid retrieval. Saved all three baseline rankings for six development queries; TF-IDF and MiniLM disagree at the top on two of them. Eleven tests pass. The test split remains held out. Next: identifier extraction and conflict detection.

## 2026-10-18 — Stage 06 complete
Added and tested identifier extraction for CVEs and ESP32 variants, including Unicode dashes, original text spans, generic-vs-variant distinction, and conservative same-family conflicts. Fourteen tests pass. This stage changes no rankings. Next: the explainable scoring adjustment.

## 2026-10-18 — Stage 07 complete
Added the proposed explainable match bonus and optional conflict penalty over RRF. Tests confirm identifier-free queries retain the exact baseline scores and order, and explanations reproduce the adjusted score. Seventeen tests pass; example weights are illustrative and have not been tuned. Next: evaluation metrics.

## 2026-10-18 — Stage 08 complete
Implemented and tested retrieval metrics, paired confidence-interval machinery, timing support, and reconstruction of metrics from saved rankings. Wrong-identifier errors require an explicit negative judgment; unjudged contradictory results are reported as unknown with bounds. Twenty-one tests pass. Next: select weights using the development set only.

## 2026-10-18 — Stage 09 complete
Ran the predeclared development grid and froze the configuration. All 12 settings tied on the selected metrics; the conservative rule selected zero bonus and zero penalty, so the primary proposed method will be identical to RRF. Before looking at test results, also recorded a fixed nonzero exploratory sensitivity comparison to show how the adjustment behaves. The test split remains held out; 21 tests pass. Next: one frozen held-out evaluation.

## 2026-10-18 — Stage 10 primary gate complete; secondary check deferred
Ran all frozen methods on 12 held-out pilot queries and repeated each ranking successfully. The primary selected method is identical to RRF by design. On the 10 identifier queries, RRF and the selected method each have MRR@10 0.875 and Recall@5 1.0; wrong-ID outcomes are 1 observed, 1 unknown, out of 10 eligible. The nonzero sensitivity setting is exploratory and must not be confused with the selected method. Saved raw results and reconstructed metrics independently. The optional SciFact archive is checksum-verified. All 21 tests still pass.

The primary stage gate passed. SciFact was deferred after its one-time CPU indexing continued for over 15 minutes without reaching the query phase. The process was stopped; no SciFact scores were produced. Its verified data and evaluation script remain available to rerun.

## 2026-10-18 — Stage 11 complete
Generated five research figures in PNG and SVG, metrics and case-study tables in CSV and LaTeX, and written methods, interpretation and limitations. They trace back to saved results. The selected method is a no-op, and the exploratory match bonus and full method give identical aggregate metrics here, so no separate penalty benefit is demonstrated. The case studies include a real baseline failure and a natural-query no-change example. All 21 tests pass. Next: paper outline, handoff, command-line search and clean-install/reproducibility verification.

## 2026-10-18 — Stage 12 primary bundle complete
Added the paper outline, exact setup and reproduction instructions, a search CLI with match/conflict explanations, and a command that reruns the experiment in a separate directory. A clean package reinstall succeeded; 21 tests pass; a fresh full rerun reproduced all 2,604 recorded ranking rows and the metric summaries and regenerated the figures. The search demo correctly returned the ESP32-S3 source and showed the selected zero weights. SciFact remains an optional, CPU-expensive secondary run; the pilot still needs independent human review and a much larger new held-out benchmark before broad research conclusions are justified.

## 2026-10-19 — Phase 2 Stage 13 complete after checkpoint
Created a separate `phase2` branch and audited the Phase 1 reference. All 21 tests passed (one pytest-cache write warning); an offline full rerun reproduced all 2,604 ranks and metric summaries. Fifty-four protected Phase 1 artifacts match the reference commit. The new protocol states the research question, source rights, target sample, review requirements, dev-only tuning grid and human-review stopping rule before any Phase 2 evaluation. No new data or Phase 2 measurements have yet been produced. Next: collect and document a new source-backed benchmark, then prepare independent review.

## 2026-10-19 — Phase 2 Stage 14 in progress
Drafted 70 possible new information needs before reading new source passages or rankings, with development/test group assignments and origin recorded. These are unreviewed agent drafts, not verified labels or human-authored questions. An initial allocation was retained and revised before source collection to reduce shared hardware topics. Next: fetch and validate source-backed passages, check the draft questions and build a review package.

## 2026-10-19 — Phase 2 Stage 14 provisional; independent review needed
Built a 150-passage draft corpus from 90 pinned CVE records and 60 excerpts of 10 licensed Espressif source files. Saved source files, rights notices, hashes and provenance. The 70 question-first drafts and 241 candidate pairs are unreviewed; no new relevance labels, rankings, tuning or test results exist. Automated integrity checks passed, and 23 tests passed, but Stage 14 is **not complete**: three hardware questions lack initial source evidence, two development questions resemble Phase 1 test questions, and only two cross-reference candidates were found against a target of five. The independent review package and exact instructions are in `data/phase2/review/` and `docs/PHASE2_ANNOTATION_GUIDELINES.md`. A real independent reviewer must review the questions and candidates before the data can be repaired and frozen.
## 2026-10-19 — Stage 14B: Evidence repair and human review preparation

**Progress:** A versioned review package is ready for independent review, but the benchmark remains provisional. The full original draft has been retained. We audited all 70 original questions and 241 candidate pairs for source consistency and review risks, and prepared 70 questions with 273 unjudged candidate pairs in the new workbook. Seven development questions are proposed replacements, including six that echo Phase 1 test topics; their source-conditioned origin and older versions are recorded. All reviewer fields are blank.

**How:** Checked each original pair against its retained source, corpus, provenance and SHA-256; investigated the three missing hardware macros against complete source headers and external vendor documentation; inventoried genuine CVE references and same-year identifier near misses without creating artificial examples; added source-based candidates and built a validator plus workbook. The AI-assisted audit is a triage aid, not a human relevance review. The complete findings and linked evidence are in `docs/PHASE2_AI_PREREVIEW.md`.

**Checks:** 26 automated tests passed. All 54 protected Phase 1 artifacts matched the reference commit. The blank workbook correctly validates as blocked: 0/70 question decisions, 0/273 pair decisions, and no independently reviewed positives. No Phase 2 rankings, tuning or effectiveness measurements were produced.

**Pending:** A genuinely independent human must complete `data/phase2/review_v2/phase2_human_review.xlsx` using `docs/PHASE2_REVIEW_V2_INSTRUCTIONS.md`, including evidence, uncertainty, identity, independence and UTC timestamps. The reviewer must resolve the three hardware needs, proposed rewrites, split independence, coverage and CVE cross-reference judgments. The initial pool is not complete; subsequent blinded pooling remains subject to the research protocol. Stop before Stage 15 until the completed review is returned.
