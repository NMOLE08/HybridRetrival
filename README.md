# Identifier-preserving hybrid retrieval

Research in progress. See [UPDATES.md](UPDATES.md) and [protocol](docs/EXPERIMENT_PROTOCOL.md). Uses a pretrained MiniLM encoder without training, TF-IDF, RRF and an experimental identifier-aware adjustment. Results are not yet available.

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
