"""Save full unmodified lexical, dense and RRF rankings for dev only."""
import csv
import json
from pathlib import Path
from iphr.data_io import load_corpus
from iphr.lexical import LexicalRetriever
from iphr.dense import DenseRetriever
from iphr.hybrid import reciprocal_rank_fusion


def main():
    docs=load_corpus("data/technical/corpus.jsonl")
    queries=[json.loads(line) for line in Path("data/technical/queries_dev.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    lexical=LexicalRetriever(docs); dense=DenseRetriever(docs)
    output=Path("outputs/dev");output.mkdir(parents=True,exist_ok=True)
    rows=[]; comparisons=[]
    for q in queries:
        a=lexical.search(q["text"],len(docs));b=dense.search(q["text"],len(docs));c=reciprocal_rank_fusion([a,b],k=60)
        for method,ranking in [("tfidf",a),("minilm",b),("rrf",c)]:
            for item in ranking:
                rows.append({"run_id":"stage05_dev_baselines","dataset":"technical","split":"dev","query_id":q["query_id"],"method":method,"doc_id":item["doc_id"],"rank":item["rank"],"raw_score":item["score"]})
        comparisons.append({"query_id":q["query_id"],"query":q["text"],"tfidf_top10":[x["doc_id"] for x in a[:10]],"minilm_top10":[x["doc_id"] for x in b[:10]],"rrf_top10":[x["doc_id"] for x in c[:10]]})
    with (output/"baseline_rankings.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n");w.writeheader();w.writerows(rows)
    (output/"baseline_comparisons.json").write_text(json.dumps(comparisons,indent=2)+"\n",encoding="utf-8")
    with (output/"baseline_top1_comparison.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.writer(f,lineterminator="\n");w.writerow(["query_id","tfidf_top1","minilm_top1","rrf_top1","tfidf_dense_disagree"])
        for c in comparisons:w.writerow([c["query_id"],c["tfidf_top10"][0],c["minilm_top10"][0],c["rrf_top10"][0],c["tfidf_top10"][0]!=c["minilm_top10"][0]])
    print(f"Wrote {len(rows)} ranking rows for {len(queries)} dev queries")

if __name__ == "__main__": main()
