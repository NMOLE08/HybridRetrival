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
