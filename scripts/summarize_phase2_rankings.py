"""Summarize saved Phase 2 rankings against derived exploratory qrels."""
import argparse, csv, json
from collections import defaultdict
from pathlib import Path
from iphr.data_io import load_corpus
from iphr.evaluation import evaluate_query, group_summaries

def load_queries(path): return [json.loads(x) for x in Path(path).read_text(encoding='utf-8').splitlines() if x.strip()]
def load_qrels(path):
    out=defaultdict(dict)
    with Path(path).open(encoding='utf-8',newline='') as f:
        for r in csv.DictReader(f):
            if r['relevance'] in {'0','1'}: out[r['query_id']][r['doc_id']]=int(r['relevance'])
    return out
def main():
    p=argparse.ArgumentParser(); p.add_argument('--rankings',required=True); p.add_argument('--queries',required=True); p.add_argument('--output-dir',required=True); args=p.parse_args()
    docs={d['doc_id']:d for d in load_corpus('data/phase2/corpus.jsonl')}; qs={q['query_id']:q for q in load_queries(args.queries)}; labels=load_qrels('data/phase2/exploratory_v1/qrels.csv')
    ranked=defaultdict(list)
    with Path(args.rankings).open(encoding='utf-8',newline='') as f:
        for r in csv.DictReader(f): ranked[(r['method'],r['query_id'])].append((int(r['rank']),r['doc_id']))
    per=[]
    for (method,qid), values in sorted(ranked.items()):
        if qid not in qs: continue
        row=evaluate_query(qs[qid],[doc for _,doc in sorted(values)],labels[qid],docs); row['method']=method; per.append(row)
    out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True)
    fields=['query_id','method','query_type','identifier_family','recall_at_5','mrr_at_10','ndcg_at_10','known_relevant','wrong_id_eligible','wrong_id_at_1']
    with (out/'per_query.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(per)
    summary={m:group_summaries([r for r in per if r['method']==m]) for m in sorted({r['method'] for r in per})}
    (out/'metrics.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'methods':list(summary),'queries':len(qs)},indent=2))
if __name__=='__main__': main()
