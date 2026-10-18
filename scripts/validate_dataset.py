"""Validate the structural contract of a proposed technical benchmark.

This cannot establish that relevance judgments are correct or complete; human or
agent review of source passages is still necessary before the Stage 02 gate.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

CORPUS_FIELDS = {"doc_id", "title", "text", "source_url", "source_type", "license_note", "family"}
QUERY_FIELDS = {"query_id", "text", "query_type", "identifier_family", "origin", "annotation_note"}


def jsonl(path):
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def unique_rows(rows, field, required, label, errors):
    seen = set()
    for row in rows:
        missing = required - row.keys()
        if missing:
            errors.append(f"{label}: missing fields {sorted(missing)}")
        identifier = row.get(field)
        if not identifier or identifier in seen:
            errors.append(f"{label}: empty or duplicate {field}: {identifier}")
        seen.add(identifier)
    return seen


def validate(root):
    root = Path(root)
    errors = []
    files = ["corpus.jsonl", "queries_dev.jsonl", "queries_test.jsonl", "qrels_dev.tsv", "qrels_test.tsv", "provenance.csv"]
    missing = [name for name in files if not (root / name).is_file()]
    if missing:
        return {"valid": False, "errors": [f"missing file: {name}" for name in missing]}
    corpus = jsonl(root / "corpus.jsonl")
    docs = unique_rows(corpus, "doc_id", CORPUS_FIELDS, "corpus", errors)
    if not corpus:
        errors.append("corpus: empty")
    texts = [" ".join(x.get("text", "").casefold().split()) for x in corpus]
    if any(not text for text in texts) or len(set(texts)) != len(texts):
        errors.append("corpus: empty or duplicate text")
    splits, qtexts, counts = {}, {}, {}
    for split in ("dev", "test"):
        queries = jsonl(root / f"queries_{split}.jsonl")
        ids = unique_rows(queries, "query_id", QUERY_FIELDS, split, errors)
        splits[split] = ids
        qtexts[split] = {" ".join(q.get("text", "").casefold().split()) for q in queries}
        counts[split] = dict(Counter(q.get("query_type") for q in queries))
        if not queries or any(not q.get("text", "").strip() for q in queries):
            errors.append(f"{split}: empty queries or query text")
        if not {"identifier", "natural"}.issubset(counts[split]):
            errors.append(f"{split}: missing identifier or natural queries")
        with (root / f"qrels_{split}.tsv").open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f, delimiter="\t"))
        positives, pairs = set(), set()
        for row in rows:
            q, d, rel = row.get("query_id"), row.get("doc_id"), row.get("relevance")
            if q not in ids or d not in docs or rel not in {"0", "1"}:
                errors.append(f"{split}: invalid qrel {row}")
            if (q, d) in pairs:
                errors.append(f"{split}: duplicate qrel {q}/{d}")
            pairs.add((q, d))
            if rel == "1":
                positives.add(q)
        if ids - positives:
            errors.append(f"{split}: queries without positive qrels: {sorted(ids - positives)}")
    if splits["dev"] & splits["test"] or qtexts["dev"] & qtexts["test"]:
        errors.append("dev/test: overlapping query IDs or normalized query texts")
    with (root / "provenance.csv").open(encoding="utf-8", newline="") as f:
        provenance = list(csv.DictReader(f))
    pids = [row.get("doc_id") for row in provenance]
    if set(pids) != docs or len(pids) != len(set(pids)):
        errors.append("provenance: missing, extra, or duplicate document IDs")
    if any(not all(row.get(k, "").strip() for k in ("doc_id", "origin_url", "rights", "hash", "extraction_method")) for row in provenance):
        errors.append("provenance: required field missing")
    hashes = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in files}
    return {"valid": not errors, "errors": errors, "documents": len(corpus), "query_types": counts, "sha256": hashes, "note": "Structural validation cannot verify near-duplicates, source rights, or relevance completeness."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    result = validate(args.directory)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
