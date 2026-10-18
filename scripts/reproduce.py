"""Rerun frozen technical evaluation in a new directory and compare saved ranks/metrics."""
from __future__ import annotations
import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def read_ranks(path):
    with path.open(encoding='utf-8',newline='') as f:
        return [(r['query_id'],r['method'],r['doc_id'],int(r['rank'])) for r in csv.DictReader(f)]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',help='New empty run directory; default is a timestamped directory in cache/reproductions')
    args=parser.parse_args()
    root=Path(args.output) if args.output else Path('cache/reproductions')/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    if root.exists(): raise SystemExit(f'Refusing to overwrite an existing directory: {root}')
    root.mkdir(parents=True)
    final=root/'final';figures=root/'figures';tables=root/'tables'
    def run(*argv):
        print('+', ' '.join(map(str,argv)),flush=True)
        subprocess.run([sys.executable,*map(str,argv)],check=True)
    run('scripts/run_experiments.py','--output-dir',final,'--manifest-path',root/'final_run.json')
    if read_ranks(final/'rankings.csv') != read_ranks(Path('outputs/final/rankings.csv')):
        raise SystemExit(f'Ranking mismatch; inspect preserved output at {root}')
    actual=json.loads((final/'metrics.json').read_text(encoding='utf-8'))
    expected=json.loads(Path('outputs/final/metrics.json').read_text(encoding='utf-8'))
    if actual != expected: raise SystemExit(f'Metric mismatch; inspect preserved output at {root}')
    run('scripts/make_paper_artifacts.py','--results',final,'--figures',figures,'--tables',tables)
    print(f'PASS: recorded ranks and metrics reproduced; new run and figures: {root}')


if __name__=='__main__': main()
