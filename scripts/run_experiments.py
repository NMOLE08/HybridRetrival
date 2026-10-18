"""Run frozen held-out pilot once, with an identical-rank repeat check."""
from __future__ import annotations
import argparse,csv,hashlib,json,subprocess,time
from pathlib import Path
import numpy as np
import yaml
from iphr.data_io import load_corpus
from iphr.dense import DenseRetriever
from iphr.lexical import LexicalRetriever
from iphr.hybrid import reciprocal_rank_fusion
from iphr.reranker import rerank
from iphr.identifiers import extract_identifiers
from iphr.evaluation import paired_bootstrap
from evaluate_rankings import evaluate_file


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser(description='Run frozen technical evaluation')
    parser.add_argument('--output-dir',default='outputs/final')
    parser.add_argument('--manifest-path',default='outputs/manifests/final_run.json')
    args=parser.parse_args()
    freeze=json.loads(Path('outputs/manifests/dev_freeze.json').read_text(encoding='utf-8'))
    cfg_path=Path('configs/final.yaml')
    if digest(cfg_path)!=freeze['config_sha256']:raise ValueError('Frozen configuration hash mismatch')
    for name,key in [('queries_test.jsonl','test_query_sha256'),('qrels_test.tsv','test_qrels_sha256')]:
        if digest(Path('data/technical')/name)!=freeze[key]:raise ValueError(f'Frozen test hash mismatch: {name}')
    cfg=yaml.safe_load(cfg_path.read_text(encoding='utf-8'))
    docs=load_corpus('data/technical/corpus.jsonl');queries=[json.loads(x) for x in Path('data/technical/queries_test.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
    start=time.perf_counter();lexical=LexicalRetriever(docs);lexical_build=time.perf_counter()-start
    dense=DenseRetriever(docs,model_id=cfg['model'],revision=cfg['model_revision'])
    if dense.embeddings.shape[0]!=len(docs):raise ValueError('Mismatched corpus')
    rankings=[];explanations=[];timings=[];repeat_checks=[]
    def elapsed(fn):
        start=time.perf_counter_ns(); value=fn();return value,(time.perf_counter_ns()-start)/1e6
    for q in queries:
        a,lex_ms=elapsed(lambda:lexical.search(q['text'],len(docs)))
        vector,embedding_ms=elapsed(lambda:np.asarray(dense.model.encode_query(q['text'],normalize_embeddings=True,show_progress_bar=False),dtype=np.float32).reshape(-1))
        def dense_rank():
            scores=dense.embeddings @ vector
            ordered=sorted(range(len(docs)),key=lambda i:(-float(scores[i]),docs[i]['doc_id']))
            return [{'doc_id':docs[i]['doc_id'],'title':docs[i]['title'],'source_url':docs[i].get('source_url',''),'rank':rank,'score':float(scores[i])} for rank,i in enumerate(ordered,1)]
        b,dense_rank_ms=elapsed(dense_rank)
        c,fusion_ms=elapsed(lambda:reciprocal_rank_fusion([a,b],k=cfg['rrf_k']))
        selected_bonus=rerank(q['text'],c,docs,cfg['lambda_match'],0)
        selected,selected_ms=elapsed(lambda:rerank(q['text'],c,docs,cfg['lambda_match'],cfg['lambda_conflict']))
        fixed_bonus=rerank(q['text'],c,docs,cfg['exploratory_lambda_match'],0)
        fixed,fixed_ms=elapsed(lambda:rerank(q['text'],c,docs,cfg['exploratory_lambda_match'],cfg['exploratory_lambda_conflict']))
        if not extract_identifiers(q['text']):
            for r in [selected_bonus,selected,fixed_bonus,fixed]:
                if [(x['doc_id'],x['score']) for x in r] != [(x['doc_id'],x['score']) for x in c]:raise RuntimeError('Identifier-free invariance failed')
        for method,items in [('tfidf',a),('minilm',b),('rrf',c),('rrf_bonus',selected_bonus),('proposed',selected),('rrf_bonus_fixed',fixed_bonus),('proposed_fixed',fixed)]:
            for item in items:
                rankings.append({'run_id':'stage10_frozen','dataset':'technical','split':'test','query_id':q['query_id'],'method':method,'doc_id':item['doc_id'],'rank':item['rank'],'raw_score':item['score']})
                if 'explanation' in item:explanations.append({'query_id':q['query_id'],'method':method,'doc_id':item['doc_id'],'rank':item['rank'],**item['explanation']})
        # Repeat full baseline retrieval before examining any test labels.
        a2=lexical.search(q['text'],len(docs));b2=dense.search(q['text'],len(docs));c2=reciprocal_rank_fusion([a2,b2],k=cfg['rrf_k'])
        if [[x['doc_id'] for x in z] for z in (a,b,c)] != [[x['doc_id'] for x in z] for z in (a2,b2,c2)]:raise RuntimeError(f"Repeated rankings differ: {q['query_id']}")
        for lm,lc,prior in [(cfg['lambda_match'],0,selected_bonus),(cfg['lambda_match'],cfg['lambda_conflict'],selected),(cfg['exploratory_lambda_match'],0,fixed_bonus),(cfg['exploratory_lambda_match'],cfg['exploratory_lambda_conflict'],fixed)]:
            if [x['doc_id'] for x in rerank(q['text'],c2,docs,lm,lc)] != [x['doc_id'] for x in prior]: raise RuntimeError('Repeated reranking differs')
        repeat_checks.append(q['query_id'])
        # The first pass warms model and index; save three subsequent component timings.
        for repetition in range(3):
            _,lex_ms=elapsed(lambda:lexical.search(q['text'],len(docs)))
            _,embedding_ms=elapsed(lambda:dense.model.encode_query(q['text'],normalize_embeddings=True,show_progress_bar=False))
            _,dense_rank_ms=elapsed(dense_rank)
            _,fusion_ms=elapsed(lambda:reciprocal_rank_fusion([a,b],k=cfg['rrf_k']))
            _,selected_ms=elapsed(lambda:rerank(q['text'],c,docs,cfg['lambda_match'],cfg['lambda_conflict']))
            _,fixed_ms=elapsed(lambda:rerank(q['text'],c,docs,cfg['exploratory_lambda_match'],cfg['exploratory_lambda_conflict']))
            timings.append({'query_id':q['query_id'],'repeat':repetition+1,'lexical_ms':lex_ms,'query_embedding_ms':embedding_ms,'dense_rank_ms':dense_rank_ms,'rrf_fusion_ms':fusion_ms,'selected_rerank_ms':selected_ms,'fixed_rerank_ms':fixed_ms})
    out=Path(args.output_dir);out.mkdir(parents=True,exist_ok=True)
    ranks=out/'rankings.csv'
    with ranks.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rankings[0]),lineterminator='\n');w.writeheader();w.writerows(rankings)
    (out/'score_explanations.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in explanations),encoding='utf-8',newline='\n')
    with (out/'timing_samples.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(timings[0]),lineterminator='\n');w.writeheader();w.writerows(timings)
    # Test labels are first read only after ranks and repeat checks are complete.
    summaries=evaluate_file(ranks,'test','data/technical',out)
    with (out/'per_query.csv').open(encoding='utf-8',newline='') as f:per=list(csv.DictReader(f))
    diffs={}
    for method in ('tfidf','minilm','rrf_bonus','proposed','rrf_bonus_fixed','proposed_fixed'):
        paired=[]
        for base in (r for r in per if r['method']=='rrf' and r['query_type']=='identifier'):
            other=next(r for r in per if r['method']==method and r['query_id']==base['query_id'])
            paired.append((base,other))
        diffs[method]={metric:paired_bootstrap([float(b[metric]) for a,b in paired],[float(a[metric]) for a,b in paired]) for metric in ('mrr_at_10','recall_at_5')}
    (out/'paired_bootstrap.json').write_text(json.dumps(diffs,indent=2)+'\n',encoding='utf-8')
    timing_summary={'samples':len(timings),'unit':'ms','conditions':'Three component timings per query after its first warm pass; sequential CPU; components are timed separately, not end-to-end.', 'lexical_index_build_seconds':lexical_build,'model_load_seconds':dense.model_load_seconds,'embedding_cache_load_or_build_seconds':dense.preprocessing_seconds,'embedding_cache_hit':dense.cache_hit,'components':{name:{'median':float(np.median([x[name] for x in timings])),'p95':float(np.percentile([x[name] for x in timings],95))} for name in timings[0] if name not in ('query_id','repeat')}}
    (out/'timing_summary.json').write_text(json.dumps(timing_summary,indent=2)+'\n',encoding='utf-8')
    demo=json.loads(Path('outputs/examples/dense_demo.json').read_text(encoding='utf-8'))
    manifest={'config_sha256':digest(cfg_path),'dataset_summary_sha256':digest('outputs/manifests/dataset_summary.json'),'query_sha256':freeze['test_query_sha256'],'qrels_sha256':freeze['test_qrels_sha256'],'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'model_id':cfg['model'],'model_revision':cfg['model_revision'],'model_weights_sha256':demo['weights_sha256'],'corpus_hash':dense.corpus_hash,'device':'cpu','seed':cfg['seed'],'queries':len(queries),'ranking_rows':len(rankings),'repeat_checks_passed':repeat_checks,'parser_coverage_count':sum(bool(extract_identifiers(q['text'])) for q in queries),'environment_manifest':'outputs/manifests/environment.json','note':'Fixed nonzero variants are exploratory; selected primary configuration is the dev-frozen no-op.'}
    manifest['git_tracked_worktree_dirty']=bool(subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],text=True).strip())
    manifest_path=Path(args.manifest_path);manifest_path.parent.mkdir(parents=True,exist_ok=True)
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'ranking_rows':len(rankings),'queries':len(queries),'methods':list(summaries),'repeat_checks':len(repeat_checks)},indent=2))

if __name__=='__main__':main()
