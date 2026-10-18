"""Optional frozen-model SciFact check; no identifier claims or weight tuning."""
from __future__ import annotations
import csv,hashlib,json,time
from collections import defaultdict
from pathlib import Path
import yaml
from iphr.data_io import load_corpus
from iphr.dense import DenseRetriever
from iphr.lexical import LexicalRetriever
from iphr.hybrid import reciprocal_rank_fusion
from iphr.reranker import rerank
from iphr.evaluation import evaluate_query,group_summaries
from iphr.identifiers import extract_identifiers


def jsonl(p):
    with p.open(encoding="utf-8") as f:return [json.loads(x) for x in f if x.strip()]

def main():
    cfg=yaml.safe_load(Path('configs/final.yaml').read_text(encoding='utf-8'))
    manifest=json.loads(Path('outputs/manifests/scifact_download.json').read_text(encoding='utf-8'))
    root=Path('data/scifact')
    for name,expected in manifest['files'].items():
        if hashlib.sha256((root/name).read_bytes()).hexdigest()!=expected:raise ValueError(f'SciFact file hash mismatch: {name}')
    rawdocs=jsonl(root/'corpus.jsonl')
    docs=[{'doc_id':d['_id'],'title':d['title'],'text':d['text'],'source_url':'https://huggingface.co/datasets/BeIR/scifact'} for d in rawdocs]
    by_id={d['doc_id']:d for d in docs}
    judgments=defaultdict(dict)
    with (root/'qrels/test.tsv').open(encoding='utf-8',newline='') as f:
        for row in csv.DictReader(f,delimiter='\t'):judgments[row['query-id']][row['corpus-id']]=int(row['score'])
    queries=[{'query_id':q['_id'],'text':q['text'],'query_type':'natural','identifier_family':'none'} for q in jsonl(root/'queries.jsonl') if q['_id'] in judgments]
    if len(queries)!=len(judgments):raise ValueError('Missing SciFact test queries')
    print(f'Indexing {len(docs)} SciFact documents on CPU; this may take several minutes.',flush=True)
    t=time.perf_counter(); lexical=LexicalRetriever(docs);lex_seconds=time.perf_counter()-t
    dense=DenseRetriever(docs,model_id=cfg['model'],revision=cfg['model_revision']);print('Dense index ready.',flush=True)
    rows=[];metrics=[];coverage=0; changed=0
    for index,q in enumerate(queries,1):
        coverage+=bool(extract_identifiers(q['text']))
        a=lexical.search(q['text'],100); b=dense.search(q['text'],100)
        c=reciprocal_rank_fusion([a,b],k=cfg['rrf_k'])
        d=rerank(q['text'],c,docs,cfg['lambda_match'],cfg['lambda_conflict'])
        if [(x['doc_id'],x['score']) for x in c] != [(x['doc_id'],x['score']) for x in d]:changed+=1
        for method,ranking in [('tfidf',a),('minilm',b),('rrf',c),('proposed',d)]:
            for x in ranking:rows.append({'run_id':'scifact_frozen','dataset':'scifact','split':'test','query_id':q['query_id'],'method':method,'doc_id':x['doc_id'],'rank':x['rank'],'raw_score':x['score']})
            metrics.append({'method':method,**evaluate_query(q,[x['doc_id'] for x in ranking],judgments[q['query_id']],by_id)})
        if index%50==0:print(f'Evaluated {index}/{len(queries)} SciFact queries.',flush=True)
    out=Path('outputs/final');out.mkdir(parents=True,exist_ok=True)
    with (out/'scifact_rankings.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    with (out/'scifact_per_query.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(metrics[0]),lineterminator='\n');w.writeheader();w.writerows(metrics)
    output={'dataset':'BEIR SciFact','split':'test','corpus_size':len(docs),'queries':len(queries),'candidate_policy':'top 100 lexical and top 100 dense, RRF union','parser_coverage_count':coverage,'parser_coverage_fraction':coverage/len(queries),'selected_rankings_changed':changed,'lexical_index_seconds':lex_seconds,'model_load_seconds':dense.model_load_seconds,'embedding_preprocessing_seconds':dense.preprocessing_seconds,'embedding_cache_hit':dense.cache_hit,'methods':{method:group_summaries([r for r in metrics if r['method']==method])['all'] for method in ('tfidf','minilm','rrf','proposed')},'license':'CC BY-SA 4.0; see source dataset card','note':'General scientific claims; not evidence of technical identifier accuracy. Selected weights were frozen on technical development queries.'}
    (out/'scifact_metrics.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(output,indent=2))
if __name__=='__main__':main()
