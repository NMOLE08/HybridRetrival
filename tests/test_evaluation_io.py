import csv,json
from pathlib import Path
from tempfile import TemporaryDirectory
from importlib.util import module_from_spec,spec_from_file_location


def test_metrics_reproducible_from_saved_rankings():
    spec=spec_from_file_location("eval_script",Path(__file__).resolve().parents[1]/"scripts/evaluate_rankings.py")
    mod=module_from_spec(spec);spec.loader.exec_module(mod)
    Path("cache").mkdir(exist_ok=True)
    with TemporaryDirectory(dir="cache") as directory:
        root=Path(directory); data=root/"data";data.mkdir(); out=root/"out"
        docs=[{"doc_id":"a","title":"A","text":"text"},{"doc_id":"b","title":"B","text":"text"}]
        q={"query_id":"q","text":"find information","query_type":"natural","identifier_family":"none"}
        (data/"corpus.jsonl").write_text("".join(json.dumps(x)+"\n" for x in docs),encoding="utf-8")
        (data/"queries_dev.jsonl").write_text(json.dumps(q)+"\n",encoding="utf-8")
        (data/"qrels_dev.tsv").write_text("query_id\tdoc_id\trelevance\nq\tb\t1\n",encoding="utf-8")
        rankings=root/"rank.csv"
        rankings.write_text("method,query_id,doc_id,rank,split\nrrf,q,a,1,dev\nrrf,q,b,2,dev\n",encoding="utf-8")
        m=mod.evaluate_file(rankings,"dev",data,out)
        assert m["rrf"]["all"]["mrr_at_10"]==.5
        before=(out/"metrics.json").read_bytes()
        mod.evaluate_file(rankings,"dev",data,out)
        assert before == (out/"metrics.json").read_bytes()
