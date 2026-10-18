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
