"""Development-only selection for the frozen Phase 2 exploratory subset."""
from __future__ import annotations
import csv, hashlib, json, platform, subprocess, sys, time
from collections import defaultdict
from pathlib import Path
import numpy as np
import yaml
from iphr.data_io import load_corpus
from iphr.dense import DenseRetriever
from iphr.evaluation import evaluate_query, group_summaries
from iphr.hybrid import reciprocal_rank_fusion
from iphr.lexical import LexicalRetriever
from iphr.reranker import rerank

MATCH = (0.0, 0.003, 0.006, 0.012)
CONFLICT = (0.0, 0.003, 0.006)
DATA = Path('data/phase2/exploratory_v1')
OUT = Path('outputs/phase2/stage16')

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def queries(path): return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]
def qrels(path):
    out = defaultdict(dict)
    with path.open(encoding='utf-8', newline='') as handle:
        for row in csv.DictReader(handle):
            if row['relevance'] in {'0','1'}: out[row['query_id']][row['doc_id']] = int(row['relevance'])
    return out
def write_csv(path, records, fields=None):
    with path.open('w',encoding='utf-8',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=fields or list(records[0]),lineterminator='\n'); writer.writeheader(); writer.writerows(records)

def main():
    if OUT.exists(): raise FileExistsError('Stage 16 output exists; preserve it and use a new run directory.')
    OUT.mkdir(parents=True)
    docs=load_corpus('data/phase2/corpus.jsonl'); by_id={d['doc_id']:d for d in docs}
    dev=queries(DATA/'queries_dev.jsonl'); labels=qrels(DATA/'qrels.csv')
    if any(not any(v==1 for v in labels[q['query_id']].values()) for q in dev): raise ValueError('Development query without frozen positive')
    lexical=LexicalRetriever(docs); dense=DenseRetriever(docs)
    base={}; rankings=[]
    for q in dev:
        lexical_rank=lexical.search(q['text'],len(docs)); dense_rank=dense.search(q['text'],len(docs))
        rrf=reciprocal_rank_fusion([lexical_rank,dense_rank],k=60); base[q['query_id']]=rrf
        for method, items in [('tfidf',lexical_rank),('minilm',dense_rank),('rrf',rrf)]:
            rankings.extend({'run_id':'phase2_stage16_dev','dataset':'phase2_exploratory_v1','split':'dev','query_id':q['query_id'],'method':method,'doc_id':x['doc_id'],'rank':x['rank'],'raw_score':x['score']} for x in items)
    grid=[]
    for lm in MATCH:
        for lc in CONFLICT:
            rows=[]
            for q in dev:
                ranked=rerank(q['text'],base[q['query_id']],docs,lm,lc)
                rows.append(evaluate_query(q,[x['doc_id'] for x in ranked],labels[q['query_id']],by_id))
            summary=group_summaries(rows)['type:identifier']; wrong=summary['wrong_id_at_1']
            grid.append({'lambda_match':lm,'lambda_conflict':lc,'identifier_mrr_at_10':summary['mrr_at_10'],
                         'identifier_recall_at_5':summary['recall_at_5'],'identifier_ndcg_at_10':summary['ndcg_at_10'],
                         'identifier_wrong_upper':wrong['upper_bound'],'identifier_wrong_lower':wrong['lower_bound'],
                         'identifier_wrong_unknown':wrong['unknown']})
    def key(x): return (-x['identifier_mrr_at_10'],x['identifier_wrong_upper'],-x['identifier_recall_at_5'],x['lambda_match']+x['lambda_conflict'],x['lambda_match'],x['lambda_conflict'])
    selected=min(grid,key=key)
    for row in grid: row['selected']=row is selected
    for q in dev:
        variants=[('match_only',selected['lambda_match'],0.0),('identifier_aware',selected['lambda_match'],selected['lambda_conflict'])]
        for method,lm,lc in variants:
            for item in rerank(q['text'],base[q['query_id']],docs,lm,lc):
                rankings.append({'run_id':'phase2_stage16_dev','dataset':'phase2_exploratory_v1','split':'dev','query_id':q['query_id'],'method':method,'doc_id':item['doc_id'],'rank':item['rank'],'raw_score':item['score']})
    write_csv(OUT/'dev_rankings.csv',rankings,['run_id','dataset','split','query_id','method','doc_id','rank','raw_score'])
    write_csv(OUT/'grid.csv',grid)
    config={'dataset_version':'phase2_exploratory_v1','seed':42,'device':'cpu','model':'sentence-transformers/all-MiniLM-L6-v2',
            'model_revision':'1110a243fdf4706b3f48f1d95db1a4f5529b4d41','rrf_k':60,'lambda_match':selected['lambda_match'],
            'lambda_conflict':selected['lambda_conflict'],'selection_split':'development only','selection_rule':'maximize identifier MRR@10; minimize observed upper WrongIdentifier@1; maximize Recall@5; minimize total weight; match; conflict',
            'annotation_status':'author annotated; not independently verified','unknown_policy':'unknown pairs are omitted from relevance and remain unknown for wrong-identifier bounds'}
    cfg=Path('configs/phase2_exploratory_final.yaml'); cfg.write_text(yaml.safe_dump(config,sort_keys=True),encoding='utf-8',newline='\n')
    test_files={'queries_test.jsonl':sha(DATA/'queries_test.jsonl'),'qrels.csv':sha(DATA/'qrels.csv')}
    freeze={'stage':'16','selected':selected,'config_sha256':sha(cfg),'corpus_sha256':sha('data/phase2/corpus.jsonl'),
            'dev_queries_sha256':sha(DATA/'queries_dev.jsonl'),'test_hashes_checked_without_evaluation':test_files,
            'dataset_manifest_sha256':sha(DATA/'manifest.json'),'git_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
            'model_cache_hit':dense.cache_hit,'model_load_seconds':dense.model_load_seconds,'embedding_seconds':dense.preprocessing_seconds,
            'note':'Only development queries were ranked for selection. No held-out test ranking or metric was generated.'}
    (OUT/'freeze.json').write_text(json.dumps(freeze,indent=2)+'\n',encoding='utf-8')
    env={'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'torch':__import__('torch').__version__,'sentence_transformers':__import__('sentence_transformers').__version__}
    (OUT/'environment.json').write_text(json.dumps(env,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'grid_rows':len(grid),'development_queries':len(dev),'selected':selected,'test_evaluated':False},indent=2))
if __name__=='__main__': main()
