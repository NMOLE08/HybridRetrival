# Decisions and deviations

## 2026-10-18 — Stage 00
- Use CPU, pretrained MiniLM, word TF-IDF and standard RRF with k=60. No training or fine-tuning.
- Primary study is a source-attributed curated technical pilot; SciFact is optional and is not evidence about identifier errors.
- Agent-created query labels are not independent human judgments. Dataset review and any constraints will be disclosed.
- The workspace initially contained no project files or Git repository. Git is installed but identity is not configured; do not impersonate a user. Git was initialized in Stage 01; checkpoint commits use a clearly labeled local Codex author, without modifying global Git settings.
- Primary outcomes, wrong-identifier policy, and development-only selection rule are in EXPERIMENT_PROTOCOL.md, before results.

## 2026-10-18 — Stage 01
- CPU environment imported successfully; versions captured in requirements.lock.txt and environment manifest, excluding local editable-install path. Dependency snapshot is not a hash-locked cross-platform build.
- Model download, unavailable-model errors and deterministic ranking are implementation-stage checks, not represented as already completed.

## 2026-10-18 — Stage 02 source discovery
- Use immutable upstream commits for source discovery; candidate raw files are cached locally and can be fetched again by the collector. They are not benchmark data or labels.
- CVE terms require preserving the copyright designation and license in redistributed copies. The Espressif copyright summary expressly discusses source code, so documentation text is not automatically treated as licensed under its code terms; ten candidate source headers carry explicit Apache-2.0 OR MIT SPDX headers. Confirm notices and suitability during corpus curation.
- Initial pytest `tmp_path` failed with WinError 5 on the existing OS temp directory; the affected test no longer needs temp files and now passes. No system permissions or private files were altered.
- Stage 02 remains partial; no retrieval or tuning work is permitted before the benchmark gate passes. Query origin must truthfully indicate agent authorship rather than incorrectly claiming human review; document any necessary schema deviation.

## 2026-10-18 — Stage 02 pilot freeze
- Proceed with a 31-passage pilot, not a paper-sized benchmark. Six development and twelve test queries are agent-authored, source-conditioned, and not independently reviewed; this is an explicit origin-schema extension. The benchmark is at high risk of construction bias and findings must be limited accordingly.
- The Log4j cross-reference was included as a second positive for test01 during dataset construction. Other pairs without explicit relevance assessments remain unjudged; the dataset does not establish complete relevance judgments.
- Current CVE terms were inspected through the public website bundle and matched the archived license/disclaimer; the license, copyright designation, Espressif headers and MIT terms are included. UTF-8 LF is used for benchmark tabular files to keep their frozen byte hashes stable across Git checkouts.
- Preserve frozen test files and source code design; do not use final labels to select or revise scoring rules.

## 2026-10-18 — Stage 03
- Pinned official all-MiniLM-L6-v2 revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`; verified the downloaded safetensors hash in the manifest. Normalized embeddings run on CPU; no training. Cache identity includes corpus content, model revision and library versions.

## 2026-10-18 — Stage 04
- Fix scikit-learn default word TF-IDF with L2 normalization. Tokenization splits hyphenated IDs and drops one-character tokens; do not silently alter the main baseline.

## 2026-10-18 — Stage 05
- RRF k=60 and full ranks are used for this 31-document pilot; compare identical document universes. No tuning is performed by this baseline.

## 2026-10-18 — Stage 06
- Support only explicit CVEs and ESP32 model variants of C/S/H/P plus numeric suffix; IEEE 802.11 is outside this pilot. Deduplicate repeated canonical IDs, preserve first original span. A same-family conflict requires explicit variants on both sides and no requested variant from that family in the document. The generic ESP32 alone never constitutes an explicit wrong variant.

## 2026-10-18 — Stage 07
- Match fraction uses distinct canonical query IDs; conflict is a binary indicator of at least one explicitly contradictory family. Scores are directly adjusted without global normalization. For identifier-free queries retain original order and exact scores. Example weights are illustrative, not selected settings.

## 2026-10-18 — Stage 08
- A contradictory unjudged top result is unknown for wrong-identifier@1, not a negative or correct outcome. Report observed count, eligible denominator and lower/upper bounds. Before dev tuning, use the conservative upper bound in the previously declared wrong-ID selection tie-break.

## 2026-10-18 — Stage 09
- All 12 grid settings tied on selected development metrics, so the prespecified conservative rule selects (0, 0), making primary proposed scores identical to RRF. Before test evaluation, added fixed smallest nonzero grid values (0.003, 0.003) as an explicitly exploratory sensitivity contrast, not a replacement for the selected setting. No test ranks or metrics were viewed.

## 2026-10-18 — Stage 10 primary run
- Completed held-out rankings with the frozen no-op primary and the previously specified nonzero exploratory variants. Test ranks were repeated before judgments were read; metrics were reconstructed independently. No scorer or parameter changes were made. SciFact secondary check is in progress.
- BEIR SciFact download initially failed certificate verification with Python default TLS; using the installed truststore package with the OS certificate store succeeded without disabling TLS verification. The archive matches the BEIR published MD5.

## 2026-10-19 — Phase 2 Stage 13
- Begin from immutable Phase 1 commit 60405f7 on a separate `phase2` branch. Phase 1 test results are historical only; they do not choose Phase 2 weights. An audit records local hashes of 54 protected tracked artifacts and confirms no Git content differences against the reference.
- Lock the Phase 2 protocol before new data collection or evaluation. The primary endpoint is identifier-subset MRR@10 versus RRF; tune on reviewed new development queries only. The old nonzero setting is a fixed illustrative comparison, not an automatic selection.
- Target 150 source-backed passages and 70 new queries with evidence-backed confusables and explicit domain balance. Source rights, target shortfalls, author provenance, semantic overlap and human review must be documented; target counts are not a power claim. No new identifier families or model training are planned.
- Actual independent human review is required before paper-grade held-out evaluation. If unavailable, stop at the review gate; unjudged and ambiguous pairs remain unknown. Source-conditioned questions and agent labels must be identified honestly.

## 2026-10-19 — Stage 14 question-first draft
- Drafted 70 possible information needs before reading newly collected Phase 2 passage content or rankings. These are agent-authored hypotheses, not fact-checked questions or relevance labels. The initial draft was retained after adjusting the dev/test allocation of hardware feature topics before any source acquisition.
- Query counts reach the prospective target but do not establish data quality, semantic independence or target-case coverage. Source-supported validation and independent reviewer correction are required; do not freeze or treat these drafts as reviewed judgments.

## 2026-10-19 — Stage 14 provisional corpus and review gate
- Collected 90 pinned official CVE records and retained 10 exact Espressif source files, producing 150 passages and full source/hash provenance. This is a convenience sample; CVE distractors from three year/ID folders are not representative, and six contiguous chunks per SoC source may omit preprocessor context.
- The first distractor pass unexpectedly selected all 54 distractors from 2022 because year lists were concatenated. Preserved the first attempt and corrected selection to interleave the year lists before model retrieval or relevance judgment; the final draft has 18 distractors each from 2022, 2023 and 2024. This correction is not evidence of representativeness.
- Prepared 241 blinded, unjudged candidate pairs; no relevance or reviewer has been fabricated, and no retrieval rankings were used. Retained the first 232-pair package after improving context for missing-macro queries.
- Stop at the independent-review checkpoint: three target questions lack initial source evidence, two dev questions resemble Phase 1 test questions, and only two cross-reference-query candidates were found. These shortfalls mean Stage 14 is provisional and its gate is unmet even though numeric sample targets were reached. Do not tune on these drafts or present them as an independently validated held-out study.
## 2026-10-19 — Stage 14B evidence repair
- Preserve all v1 review artifacts and source corpus; v2 changes only proposed unreviewed review materials. Preserve original IDs, record prior question-to-pair mapping in v1, and explicitly record seven source-conditioned dev question proposals and the risk of selection bias.
- Do not infer hardware absence from a missing `SOC_*` definition. Distinguish internal DAC from usable DAC peripheral, USB Serial/JTAG from OTG, and unresolved vendor-vs-community claims about C61 RMT. External official documentation is linked, not silently inserted into the licensed corpus. An externally supported factual answer does not establish a reviewed positive inside the corpus.
- Retain exactly two directed in-corpus CVE cross-references and ten real same-year edit-distance-two query-document cases; do not manufacture more or count them as relevant/irrelevant. Add actual source candidates without using rankings.
- All 70 questions and 273 candidate pairs remain unjudged; labels, identity, independence, evidence, uncertainty and timestamps must come from a real reviewer. Automated metadata checks are necessary but cannot verify independence or establish scientific validity. Human adjudication and coverage gates remain mandatory; do not run Stage 15, tuning, or test evaluation yet.

## 2026-10-21 — Stage 15 intake rejection
- Do not convert the submitted numeric question values (`1`/`0`) into schema validity values or infer reviewer provenance. Treat them as an incomplete, unverified submission because every required reviewer metadata and evidence field is blank.
- Preserve all submitted pair labels exactly but do not use them as qrels: 33 needs lack a positive, and no reviewer evidence establishes the labelled positives, negatives, or cross-references. Keep the review gate blocked and do not begin pooling, dev selection, or test evaluation.

## 2026-10-21 — Stage 15 follow-up normalization and coverage repair
- A derived v3 copy maps the submitted question decisions to `yes`/`no` without changing their meaning. The original workbook is not modified, and all 273 submitted pair labels are preserved exactly.
- Macro-name matching against the retained pinned corpus can prepare review leads but cannot create a relevance label. The 152 added candidates remain blank/unjudged; source-context cases and unsupported needs require explicit human correction, exclusion, or new versioned evidence.
- Reviewer pseudonym, independence declaration, actual UTC time, confidence, source-specific reason, and uncertainty must be supplied by a genuine independent reviewer. Blank metadata is not repaired by automation. The Stage 15/16/17 gates remain blocked.

## 2026-10-21 — Exploratory amendment and conservative evidence subset
- The user explicitly authorized replacing the unavailable independent-review gate with an author-annotated exploratory protocol. Preserve the old protocol and state the amendment date, timing, and scope in every relevant report.
- Freeze only queries with author validity `yes` and an author-positive pair whose pinned raw source contains the target. This produced 30 CVE-only queries (12 dev, 18 test) and 32 positives before any Phase 2 ranking. The resulting family imbalance is a limitation, not a result to repair using retrieval output.
- Preserve all original labels. In derived qrels, author-positive pairs without target evidence are `unknown`; this avoids treating suspicious positives as negatives. Retain author `0` labels as author-produced negatives and disclose their incomplete coverage. The 152 unjudged follow-up candidates are excluded from qrels.
