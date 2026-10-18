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
