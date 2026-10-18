import csv
import json
from pathlib import Path
from importlib.util import module_from_spec, spec_from_file_location

ROOT = Path(__file__).resolve().parents[1]


def test_pilot_structure_and_cross_reference():
    spec = spec_from_file_location("validator", ROOT / "scripts" / "validate_dataset.py")
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    result = mod.validate(ROOT / "data" / "technical")
    assert result["valid"], result["errors"]
    assert result["documents"] == 31
    with (ROOT / "data/technical/qrels_test.tsv").open(encoding="utf-8", newline="") as f:
        positives = {(r["query_id"], r["doc_id"]) for r in csv.DictReader(f, delimiter="\t") if r["relevance"] == "1"}
    assert ("test01", "cve-2021-44228") in positives
    assert ("test01", "cve-2021-45046") in positives


def test_passages_have_attribution_and_explicit_origin():
    root = ROOT / "data/technical"
    for row in map(json.loads, (root / "corpus.jsonl").read_text(encoding="utf-8").splitlines()):
        assert row["source_url"].startswith("https://raw.githubusercontent.com/")
        assert row["license_note"] and row["text"].strip()
    for split in ("dev", "test"):
        for q in map(json.loads, (root / f"queries_{split}.jsonl").read_text(encoding="utf-8").splitlines()):
            assert q["origin"] == "agent_authored"
