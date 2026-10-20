"""Serialize the unjudged CSV templates for the workbook builder."""
import argparse
import csv
import json
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('output', type=Path)
    args = ap.parse_args()
    base = Path('data/phase2/review_v2')
    data = {}
    for key, name in [('questions','question_review.csv'), ('pairs','candidate_pairs.csv')]:
        with (base/name).open(encoding='utf-8-sig', newline='') as f:
            data[key] = list(csv.DictReader(f))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

if __name__ == '__main__': main()
