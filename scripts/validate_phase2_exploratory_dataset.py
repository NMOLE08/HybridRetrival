"""Validate the frozen derived author-annotated exploratory subset."""
import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path('data/phase2/exploratory_v1')

def rows(path):
    with path.open(encoding='utf-8', newline='') as handle: return list(csv.DictReader(handle))
def jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--root', type=Path, default=ROOT); ap.add_argument('--output', type=Path)
    args = ap.parse_args(); root = args.root
    errors = []
    manifest = json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    dev, test = jsonl(root/'queries_dev.jsonl'), jsonl(root/'queries_test.jsonl')
    qrels = rows(root/'qrels.csv'); ids = {q['query_id'] for q in dev + test}
    if len(ids) != len(dev) + len(test): errors.append('query IDs overlap across development and test')
    if any(q.get('split') != 'dev' for q in dev) or any(q.get('split') != 'test' for q in test): errors.append('split labels do not match query files')
    if any(q.get('query_type') != 'identifier' for q in dev + test): errors.append('eligible subset must retain its documented identifier-only composition')
    if any(r['query_id'] not in ids for r in qrels): errors.append('qrels reference excluded or unknown query')
    positives = {q: 0 for q in ids}
    for row in qrels:
        if row['relevance'] not in {'0','1','unknown'}: errors.append(f"invalid qrel relevance: {row}")
        if row['relevance'] == '1':
            positives[row['query_id']] += 1
            if row['evidence_disposition'] != 'retained_positive_with_source_evidence': errors.append('positive lacks source-evidence disposition')
    missing = sorted(q for q, count in positives.items() if count == 0)
    if missing: errors.append('eligible query missing known positive: '+', '.join(missing))
    for name, expected in manifest['files'].items():
        actual = digest(root/name)
        if actual != expected: errors.append(f'hash mismatch: {name}')
    result = {'status':'PASS' if not errors else 'FAIL','queries':len(ids),'dev_queries':len(dev),'test_queries':len(test),
              'qrels':len(qrels),'positives':sum(positives.values()),'queries_without_positive':missing,
              'errors':errors,'limitations':manifest['limitations']}
    text=json.dumps(result,indent=2)+'\n'
    if args.output: args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(text,encoding='utf-8')
    print(text,end=''); return 0 if not errors else 1
if __name__ == '__main__': sys.exit(main())
