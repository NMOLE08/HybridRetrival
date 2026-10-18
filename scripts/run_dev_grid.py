"""Select scoring weights solely from the frozen development split."""
from __future__ import annotations
import csv,hashlib,json,subprocess
from collections import defaultdict
from pathlib import Path
import yaml
from iphr.data_io import load_corpus
from iphr.reranker import rerank
from iphr.evaluation import evaluate_query,group_summaries
from evaluate_rankings import evaluate_file

MATCH=(0.0,0.003,0.006,0.012)
CONFLICT=(0.0,0.003,0.006)


def main():
    docs=load_corpus("data/technical/corpus.jsonl"); by_id={d["doc_id"]:d for d in docs}
    queries=[json.loads(line) for line in Path("data/technical/queries_dev.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    qrels=defaultdict(dict)
    with Path("data/technical/qrels_dev.tsv").open(encoding="utf-8",newline="") as f:
        for r in csv.DictReader(f,delimiter="\t"):qrels[r["query_id"]][r["doc_id"]]=int(r["relevance"])
    source=[]
    with Path("outputs/dev/baseline_rankings.csv").open(encoding="utf-8",newline="") as f:source=list(csv.DictReader(f))
    original={q["query_id"]:[{"doc_id":r["doc_id"],"rank":int(r["rank"]),"score":float(r["raw_score"])} for r in source if r["method"]=="rrf" and r["query_id"]==q["query_id"]] for q in queries}
    grid=[]
    for lm in MATCH:
        for lc in CONFLICT:
            rows=[]
            for q in queries:
                baseline=original[q["query_id"]];out=rerank(q["text"],baseline,docs,lm,lc)
                if q["query_type"]=="natural" and [(x["doc_id"],x["score"]) for x in out] != [(x["doc_id"],x["score"]) for x in baseline]: raise RuntimeError("Natural-query invariant failed")
                rows.append(evaluate_query(q,[x["doc_id"] for x in out],qrels[q["query_id"]],by_id))
            summary=group_summaries(rows)["type:identifier"]
            wrong=summary["wrong_id_at_1"]
            if not wrong["eligible"]:raise ValueError("No eligible identifier development queries")
            grid.append({"lambda_match":lm,"lambda_conflict":lc,"identifier_mrr_at_10":summary["mrr_at_10"],"identifier_wrong_upper":wrong["upper_bound"],"identifier_wrong_count":wrong["wrong"],"identifier_unknown_count":wrong["unknown"],"identifier_recall_at_5":summary["recall_at_5"]})
    def key(x):return (-x["identifier_mrr_at_10"],x["identifier_wrong_upper"],-x["identifier_recall_at_5"],x["lambda_match"]+x["lambda_conflict"],x["lambda_match"],x["lambda_conflict"])
    chosen=min(grid,key=key)
    for x in grid:x["selected"]=(x is chosen)
    out=Path("outputs/dev");out.mkdir(parents=True,exist_ok=True)
    with (out/"grid.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(grid[0]),lineterminator="\n");w.writeheader();w.writerows(grid)
    config={"seed":42,"model":"sentence-transformers/all-MiniLM-L6-v2","model_revision":"1110a243fdf4706b3f48f1d95db1a4f5529b4d41","device":"cpu","rrf_k":60,"candidate_policy":"full_corpus","lambda_match":chosen["lambda_match"],"lambda_conflict":chosen["lambda_conflict"],"exploratory_lambda_match":min(x for x in MATCH if x>0),"exploratory_lambda_conflict":min(x for x in CONFLICT if x>0),"exploratory_note":"fixed smallest nonzero grid values; sensitivity only, not the selected method","selection_split":"dev","selection_rule":"maximize identifier MRR@10; minimize wrong-ID upper bound; maximize Recall@5; minimize sum, match, conflict"}
    cfg=Path("configs/final.yaml");cfg.write_text(yaml.safe_dump(config,sort_keys=True),encoding="utf-8",newline="\n")
    output_rows=[{k:r[k] for k in ['run_id','dataset','split','query_id','method','doc_id','rank','raw_score']} for r in source]
    for q in queries:
        settings=(("rrf_bonus",chosen["lambda_match"],0.0), ("proposed",chosen["lambda_match"],chosen["lambda_conflict"]), ("rrf_bonus_fixed",config["exploratory_lambda_match"],0.0), ("proposed_fixed",config["exploratory_lambda_match"],config["exploratory_lambda_conflict"]))
        for method,lm,lc in settings:
            for r in rerank(q["text"],original[q["query_id"]],docs,lm,lc):
                output_rows.append({"run_id":"stage09_dev","dataset":"technical","split":"dev","query_id":q["query_id"],"method":method,"doc_id":r["doc_id"],"rank":r["rank"],"raw_score":r["score"]})
    rankfile=out/"rankings.csv"
    with rankfile.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=['run_id','dataset','split','query_id','method','doc_id','rank','raw_score'],lineterminator="\n");w.writeheader();w.writerows(output_rows)
    evaluate_file(rankfile,"dev","data/technical",out)
    sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    frozen=json.loads(Path("outputs/manifests/dataset_summary.json").read_text(encoding="utf-8"))["sha256_all"]
    for name in ('queries_test.jsonl','qrels_test.tsv'):
        if sha(Path('data/technical')/name)!=frozen[name]:raise ValueError(f"Frozen test file changed: {name}")
    freeze={"config_sha256":sha(cfg),"test_query_sha256":frozen['queries_test.jsonl'],"test_qrels_sha256":frozen['qrels_test.tsv'],"selection_rule":config['selection_rule'],"selected":chosen,"pre_freeze_git_head":subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),"note":"Selection uses development judgments only; test files checked by hash, not evaluated."}
    Path('outputs/manifests/dev_freeze.json').write_text(json.dumps(freeze,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(freeze,indent=2))

if __name__=="__main__":main()
