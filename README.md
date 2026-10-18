# Identifier-preserving hybrid retrieval

This repository contains a reproducible pilot of technical search using pretrained MiniLM without training, TF-IDF, standard RRF and an explainable identifier-aware adjustment. The 31-passage dataset and 12-query held-out test are small and agent-annotated; they do not support a general performance claim. The development-selected identifier weights are zero, so the primary proposed method matches RRF. Fixed nonzero variants are reported separately as exploratory.

See [UPDATES.md](UPDATES.md) for progress, [results](docs/RESULTS_INTERPRETATION.md), [methodology](docs/METHODS.md), [limitations](docs/LIMITATIONS.md), the [paper outline](docs/PAPER_OUTLINE.md), and [handoff](docs/HANDOFF.md). Data provenance and source notices are included in `data/technical/`.

## Setup

Python 3.11+ and network access for dependency and model downloads are required. PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
python -m pytest -q
python -m iphr.cli --help
```

Bash:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q
python -m iphr.cli --help
```

The recorded dependency snapshot will capture the tested environment; exact cross-platform reproduction may require matching the OS and Python version. No API credentials are needed.

To recreate the recorded Windows/Python 3.12 dependency versions, use `python -m pip install -c requirements.lock.txt -e ".[dev]"`. The snapshot does not lock wheel hashes and may not apply to other platforms.

## Reproduce and search

```powershell
python scripts/reproduce.py
python -m iphr.cli search --query 'ESP32-S3 Wi-Fi CSI' --method proposed --top-k 5 --explain
```

The reproduction command creates a new run in ignored `cache/reproductions/`, compares its ranking and metrics with the stored reference, and generates figures without overwriting the original outputs. `outputs/final/` contains the recorded rankings, judgments-derived summaries, confidence intervals and timing samples; `outputs/figures/` and `outputs/tables/` contain the paper artifacts. See the handoff for source rebuilding, hashes, and the optional SciFact check.
