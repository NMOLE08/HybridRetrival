"""One frozen held-out evaluation for the Phase 2 exploratory subset."""
from __future__ import annotations
import csv, hashlib, json, subprocess, time
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
import yaml
from iphr.data_io import load_corpus
from iphr.dense import DenseRetriever
from iphr.evaluation import evaluate_query, group_summaries, paired_bootstrap
from iphr.hybrid import reciprocal_rank_fusion
from iphr.identifiers import extract_identifiers
from iphr.lexical import LexicalRetriever
from iphr.reranker import rerank

DATA=Path('data/phase2/exploratory_v1'); STAGE16=Path('outputs/phase2/stage16'); OUT=Path('outputs/phase2/stage17')
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load_queries(path): return [json.loads(x) for x in Path(path).read_text(encoding='utf-8').splitlines() if x.strip()]
def labels(path):
    out=defaultdict(dict)
    with Path(path).open(encoding='utf-8',newline='') as f:
        for r in csv.DictReader(f):
            if r['relevance'] in {'0','1'}: out[r['query_id']][r['doc_id']]=int(r['relevance'])
    return out
def write_csv(path, records, fields=None):
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(records[0]),lineterminator='\n');w.writeheader();w.writerows(records)
def elapsed(fn):
    start=time.perf_counter_ns(); value=fn(); return value,(time.perf_counter_ns()-start)/1e6

def main():
    if OUT.exists(): raise FileExistsError('Stage 17 output exists; preserve it and create a new run directory.')
    freeze=json.loads((STAGE16/'freeze.json').read_text(encoding='utf-8')); cfg_path=Path('configs/phase2_exploratory_final.yaml')
    if sha(cfg_path)!=freeze['config_sha256']: raise ValueError('frozen configuration hash mismatch')
    for name, expected in freeze['test_hashes_checked_without_evaluation'].items():
        if sha(DATA/name)!=expected: raise ValueError(f'frozen test hash mismatch: {name}')
    if sha('data/phase2/corpus.jsonl')!=freeze['corpus_sha256']: raise ValueError('frozen corpus hash mismatch')
    cfg=yaml.safe_load(cfg_path.read_text(encoding='utf-8')); OUT.mkdir(parents=True)
    docs=load_corpus('data/phase2/corpus.jsonl'); by_id={d['doc_id']:d for d in docs}; qs=load_queries(DATA/'queries_test.jsonl')
    lexical=LexicalRetriever(docs); dense=DenseRetriever(docs); all_rows=[]; explanations=[]; timings=[]; repeat=[]
    for q in qs:
        lexical_rank,lex_ms=elapsed(lambda:lexical.search(q['text'],len(docs)))
        vector,embed_ms=elapsed(lambda:np.asarray(dense.model.encode_query(q['text'],normalize_embeddings=True,show_progress_bar=False),dtype=np.float32).reshape(-1))
        def dense_rank():
            scores=dense.embeddings @ vector; order=sorted(range(len(docs)),key=lambda i:(-float(scores[i]),docs[i]['doc_id']))
            return [{'doc_id':docs[i]['doc_id'],'title':docs[i]['title'],'source_url':docs[i].get('source_url',''),'rank':rank,'score':float(scores[i])} for rank,i in enumerate(order,1)]
        semantic_rank,semantic_ms=elapsed(dense_rank)
        fused,fusion_ms=elapsed(lambda:reciprocal_rank_fusion([lexical_rank,semantic_rank],k=cfg['rrf_k']))
        match_only,match_ms=elapsed(lambda:rerank(q['text'],fused,docs,cfg['lambda_match'],0.0))
        aware,aware_ms=elapsed(lambda:rerank(q['text'],fused,docs,cfg['lambda_match'],cfg['lambda_conflict']))
        methods=[('tfidf',lexical_rank),('minilm',semantic_rank),('rrf',fused),('match_only',match_only),('identifier_aware',aware)]
        for method, ranked in methods:
            all_rows.extend({'run_id':'phase2_stage17_frozen_test','dataset':'phase2_exploratory_v1','split':'test','query_id':q['query_id'],'method':method,'doc_id':x['doc_id'],'rank':x['rank'],'raw_score':x['score']} for x in ranked)
            explanations.extend({'query_id':q['query_id'],'method':method,'doc_id':x['doc_id'],'rank':x['rank'],**x['explanation']} for x in ranked if 'explanation' in x)
        # Repeat before judgments are loaded.
        again_l=lexical.search(q['text'],len(docs)); again_s=dense.search(q['text'],len(docs)); again_r=reciprocal_rank_fusion([again_l,again_s],k=cfg['rrf_k']); again_a=rerank(q['text'],again_r,docs,cfg['lambda_match'],cfg['lambda_conflict'])
        if [x['doc_id'] for x in lexical_rank]!=[x['doc_id'] for x in again_l] or [x['doc_id'] for x in semantic_rank]!=[x['doc_id'] for x in again_s] or [x['doc_id'] for x in fused]!=[x['doc_id'] for x in again_r] or [x['doc_id'] for x in aware]!=[x['doc_id'] for x in again_a]: raise RuntimeError('ranking repeat mismatch: '+q['query_id'])
        repeat.append(q['query_id'])
        for rep in range(3):
            _,a=elapsed(lambda:lexical.search(q['text'],len(docs))); _,b=elapsed(lambda:dense.model.encode_query(q['text'],normalize_embeddings=True,show_progress_bar=False)); _,c=elapsed(dense_rank); _,d=elapsed(lambda:reciprocal_rank_fusion([lexical_rank,semantic_rank],k=cfg['rrf_k'])); _,e=elapsed(lambda:rerank(q['text'],fused,docs,cfg['lambda_match'],cfg['lambda_conflict']))
            timings.append({'query_id':q['query_id'],'repeat':rep+1,'tfidf_ms':a,'embedding_ms':b,'dense_rank_ms':c,'rrf_ms':d,'identifier_aware_rerank_ms':e})
    write_csv(OUT/'rankings.csv',all_rows,['run_id','dataset','split','query_id','method','doc_id','rank','raw_score'])
    (OUT/'score_explanations.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in explanations),encoding='utf-8')
    write_csv(OUT/'timing_samples.csv',timings)
    # Only now load author-derived qrels.
    qrel=labels(DATA/'qrels.csv'); per=[]
    grouped=defaultdict(list)
    for row in all_rows: grouped[(row['method'],row['query_id'])].append(row)
    for (method,qid), rows in sorted(grouped.items()):
        outcome=evaluate_query(next(q for q in qs if q['query_id']==qid),[x['doc_id'] for x in sorted(rows,key=lambda r:r['rank'])],qrel[qid],by_id); outcome['method']=method; per.append(outcome)
    fields=['query_id','method','query_type','identifier_family','recall_at_5','mrr_at_10','ndcg_at_10','known_relevant','wrong_id_eligible','wrong_id_at_1']
    write_csv(OUT/'per_query.csv',per,fields)
    metrics={m:group_summaries([x for x in per if x['method']==m]) for m in sorted({x['method'] for x in per})}
    (OUT/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n',encoding='utf-8')
    paired={}; comparisons=[]
    for method in ('tfidf','minilm','match_only','identifier_aware'):
        a={x['query_id']:x for x in per if x['method']==method}; b={x['query_id']:x for x in per if x['method']=='rrf'}
        paired[method]={metric:paired_bootstrap([a[q][metric] for q in b],[b[q][metric] for q in b]) for metric in ('mrr_at_10','recall_at_5','ndcg_at_10')}
        for metric in ('mrr_at_10','recall_at_5','ndcg_at_10'):
            gains=sum(a[q][metric]>b[q][metric] for q in b); losses=sum(a[q][metric]<b[q][metric] for q in b); ties=len(b)-gains-losses
            comparisons.append({'method':method,'metric':metric,'gains':gains,'losses':losses,'ties':ties})
    (OUT/'paired_bootstrap.json').write_text(json.dumps(paired,indent=2)+'\n',encoding='utf-8'); write_csv(OUT/'gains_losses_ties.csv',comparisons)
    timing={k:{'median_ms':float(np.median([x[k] for x in timings])),'p95_ms':float(np.percentile([x[k] for x in timings],95))} for k in timings[0] if k not in {'query_id','repeat'}}
    (OUT/'timing_summary.json').write_text(json.dumps({'samples':len(timings),'conditions':'three sequential warm component samples per query; not end-to-end latency','lexical_build_seconds':None,'model_load_seconds':dense.model_load_seconds,'embedding_cache_seconds':dense.preprocessing_seconds,'components':timing},indent=2)+'\n',encoding='utf-8')
    manifest={'stage':'17','config_sha256':sha(cfg_path),'freeze_sha256':sha(STAGE16/'freeze.json'),'corpus_sha256':sha('data/phase2/corpus.jsonl'),'test_query_sha256':sha(DATA/'queries_test.jsonl'),'qrels_sha256':sha(DATA/'qrels.csv'),'queries':len(qs),'ranking_rows':len(all_rows),'repeat_checks':repeat,'model_cache_hit':dense.cache_hit,'model_revision':cfg['model_revision'],'seed':cfg['seed'],'annotation_status':'author annotated; incomplete and not independently verified','git_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'queries':len(qs),'ranking_rows':len(all_rows),'metrics':{m:metrics[m]['all'] for m in metrics},'repeat_checks':len(repeat)},indent=2))
if __name__=='__main__':main()
