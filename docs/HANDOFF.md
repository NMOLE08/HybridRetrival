# Handoff and reproducibility

Run commands from the repository root. The repository includes the small technical corpus, query split, judgments, source attribution, frozen configuration, raw rankings, outputs, and figures. Model weights, virtual environments, downloaded source cache and SciFact corpus are not committed.

## Install

The tested environment was Windows, Python 3.12.8 and CPU; package versions are recorded in `requirements.lock.txt` and `outputs/manifests/environment.json`. With Python 3.11+ and network access in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -c requirements.lock.txt -e '.[dev]'
python -m pytest -q
```

On Bash use `source .venv/bin/activate` instead. The version snapshot is not a wheel-hash lock and OS-specific wheels and numeric differences can affect reproduction. The pinned MiniLM revision is downloaded automatically on first use; no model training or credential is needed. Access to Hugging Face and upstream source hosts is required for downloads.

## One command to reproduce the technical experiment and figures

```powershell
python scripts/reproduce.py
```

This checks frozen test/config hashes, reruns the CPU retrieval, saves ranks, explanations, metrics, timing and plots in a new timestamped `cache/reproductions/` directory, and compares ranks and metric summaries with the committed reference run. It never overwrites the reference outputs. The model download and initial uncached embedding build may take time; run-time timings vary. A ranking mismatch is reported rather than hidden and the new files remain available for diagnosis. Use `--output PATH` for a new, nonexistent destination. The optional SciFact check is separate.

## Search demo

```powershell
python -m iphr.cli search --query 'ESP32-S3 Wi-Fi CSI' --method proposed --top-k 5 --explain
```

The returned JSON includes source URLs, RRF-derived scores, extracted identifiers, and the match/conflict decisions. The actual selected frozen weights are zero, so the proposed order equals RRF; this CLI does not silently substitute exploratory weights.

## Rebuild the technical corpus from upstream

First preserve any local edits: the builder rewrites tracked dataset files and the collector rewrites its source manifest. With a clean checkout and network access:

```powershell
python scripts/collect_technical_corpus.py
python scripts/build_benchmark.py
python scripts/validate_dataset.py
git diff -- data/technical outputs/manifests/dataset_summary.json
```

Compare the generated content hashes with `outputs/manifests/dataset_summary.json` and inspect any difference before use. Source revisions, raw hashes, extraction and rights are in `data/technical/provenance.csv`, `NOTICE.md` and `LICENSES/`. Upstream source changes or removal must be investigated; do not replace source material silently.

## Optional SciFact check

The official archive is retrieved over TLS using the system trust store, checked against BEIR's published MD5, and locally recorded with SHA-256 and file hashes. `data/scifact/` is ignored and the fetcher refuses to overwrite it. Run only if it does not exist:

```powershell
python scripts/fetch_scifact.py
python scripts/run_scifact.py
```

Indexing 5,183 documents on CPU can take substantial time. The run writes `outputs/final/scifact_*` and should not be presented as evidence of technical identifier accuracy. Save or move any previous SciFact output before rerunning, since that runner writes the same output names. Its source/license manifest is `outputs/manifests/scifact_download.json`.

## Identity and outputs

- Technical experiment code revision: `080b8aba659bf8885bdb954e19ff73cbef106911` as recorded in `outputs/manifests/final_run.json`; later commits add reporting and reproducibility tooling. The current revision is available from `git rev-parse HEAD`.
- Frozen config SHA-256: `834a5e7781ad996e4f08799f43feb1e274376c53232b4ae914ac9a44f6918193`.
- Test query SHA-256: `6c213d02451e013acdb16ba506d24af2b00c8f79eadf67ae52f905f52f14823e`; qrels SHA-256: `8dc288044e4a561ff4004a77d2ff3de51f540d06347e8b12ab938eb196fe2f3e`.
- Model revision: `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`; recorded model weights SHA-256: `53aa51172d142c89d9012cce15ae4d6cc0ca6895895114379cacb4fab128d9db`.
- Dataset file hashes and normalized corpus hash are in `outputs/manifests/dataset_summary.json` and `final_run.json`. Raw technical rankings, per-query judgments and summaries are in `outputs/final/`; generated figures and paper tables are in `outputs/figures/` and `outputs/tables/`.

Read [LIMITATIONS.md](LIMITATIONS.md), [METHODS.md](METHODS.md), [RESULTS_INTERPRETATION.md](RESULTS_INTERPRETATION.md) and [PAPER_OUTLINE.md](PAPER_OUTLINE.md). Independent human annotation, a larger representative benchmark, broad identifier coverage and an independent new held-out test were not run. The current pilot is insufficient for a general performance or novelty claim.
