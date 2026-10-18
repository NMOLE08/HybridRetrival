"""Recompute metrics from saved rankings and qrels without loading models."""
from __future__ import annotations
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from iphr.data_io import load_corpus
from iphr.evaluation import evaluate_query,group_summaries


def evaluate_file(ranking_path, split, dataset_dir, output_dir):
    root=Path(dataset_dir); output=Path(output_dir);output.mkdir(parents=True,exist_ok=True)
    docs={x["doc_id"]:x for x in load_corpus(root/"corpus.jsonl")}
    queries={x["query_id"]:x for x in (json.loads(l) for l in (root/f"queries_{split}.jsonl").read_text(encoding="utf-8").splitlines() if l.strip())}
    judgments=defaultdict(dict)
    with (root/f"qrels_{split}.tsv").open(encoding="utf-8",newline="") as f:
        for r in csv.DictReader(f,delimiter="\t"): judgments[r["query_id"]][r["doc_id"]]=int(r["relevance"])
    grouped=defaultdict(list)
    with Path(ranking_path).open(encoding="utf-8",newline="") as f:
        for r in csv.DictReader(f):
            if r["split"] != split: raise ValueError("Ranking file contains an unexpected split")
            if r["query_id"] not in queries or r["doc_id"] not in docs: raise ValueError("Unknown query or document ID")
            grouped[(r["method"],r["query_id"])].append((int(r["rank"]),r["doc_id"]))
    methods=sorted({method for method,_ in grouped})
    if not methods: raise ValueError("No rankings")
    rows=[]
    for method in methods:
        for qid,q in queries.items():
            items=sorted(grouped.get((method,qid),[]))
            if not items or [x[0] for x in items] != list(range(1,len(items)+1)): raise ValueError(f"Missing or invalid ranks: {method}/{qid}")
            metrics=evaluate_query(q,[x[1] for x in items],judgments[qid],docs)
            rows.append({"dataset":"technical","split":split,"method":method,**metrics})
    summaries={method:group_summaries([r for r in rows if r["method"]==method]) for method in methods}
    with (output/"per_query.csv").open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n");writer.writeheader();writer.writerows(rows)
    (output/"metrics.json").write_text(json.dumps({"dataset":"technical","split":split,"methods":summaries,"note":"Recall uses known positives. WrongIdentifier@1 reports unknown conflicting unjudged tops and bounds."},indent=2)+"\n",encoding="utf-8")
    return summaries


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rankings",required=True);p.add_argument("--split",choices=["dev","test"],required=True);p.add_argument("--dataset-dir",default="data/technical");p.add_argument("--output-dir",required=True)
    args=p.parse_args();result=evaluate_file(args.rankings,args.split,args.dataset_dir,args.output_dir)
    print(json.dumps({"methods":list(result),"split":args.split},indent=2))

if __name__=="__main__":main()
