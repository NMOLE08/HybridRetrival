"""Safeguards for source-backed, still-unreviewed Phase 2 draft data."""
import csv
import hashlib
import json
from pathlib import Path

ROOT=Path('data/phase2')


def jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def test_draft_sources_are_auditable_and_old_test_text_is_not_reused():
    docs=jsonl(ROOT/'corpus.jsonl');needs=jsonl(ROOT/'needs_draft.jsonl')
    old=jsonl(Path('data/technical/queries_test.jsonl'))
    with (ROOT/'provenance.csv').open(encoding='utf-8',newline='') as f:provenance=list(csv.DictReader(f))
    assert len({d['doc_id'] for d in docs})==len(docs)
    assert set(d['doc_id'] for d in docs)==set(p['doc_id'] for p in provenance)
    assert not {q['query'].casefold().strip() for q in needs}&{q['text'].casefold().strip() for q in old}
    for p in provenance:
        assert hashlib.sha256(Path(p['raw_path']).read_bytes()).hexdigest()==p['raw_sha256']
        assert p['origin_url'].startswith('https://') and p['origin_revision'] and p['rights']


def test_unreviewed_candidates_are_not_human_judgments():
    with (ROOT/'review/candidate_pairs.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
    needs={q['need_id'] for q in jsonl(ROOT/'needs_draft.jsonl')}
    docs={d['doc_id'] for d in jsonl(ROOT/'corpus.jsonl')}
    assert rows
    assert all(r['need_id'] in needs and r['doc_id'] in docs for r in rows)
    assert all(r['proposed_relevance']=='unjudged' and not r['human_relevance'] and not r['reviewer_id'] for r in rows)
