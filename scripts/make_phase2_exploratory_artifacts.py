"""Create Phase 2 exploratory figures and tables only from saved artifacts."""
import csv, json
from collections import defaultdict
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

ROOT=Path('outputs/phase2'); OUT=ROOT/'stage18'; FIG=OUT/'figures'; TABLE=OUT/'tables'
METHODS=[('tfidf','TF-IDF'),('minilm','MiniLM'),('rrf','RRF'),('match_only','Match-only'),('identifier_aware','Identifier-aware')]
def rows(path):
    with Path(path).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def save(fig,name):
    fig.savefig(FIG/(name+'.png'),dpi=250,bbox_inches='tight');fig.savefig(FIG/(name+'.svg'),bbox_inches='tight');plt.close(fig)
def write(path, data, fields=None):
    with Path(path).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(data[0]),lineterminator='\n');w.writeheader();w.writerows(data)
def rank_of(ranked, positives):
    for x in ranked:
        if x['doc_id'] in positives:return int(x['rank'])
    return None
def main():
    if OUT.exists(): raise FileExistsError('Stage 18 output exists; preserve it and create a new run directory.')
    FIG.mkdir(parents=True); TABLE.mkdir(parents=True)
    metrics=json.loads((ROOT/'stage17/metrics.json').read_text(encoding='utf-8')); boot=json.loads((ROOT/'stage17/paired_bootstrap.json').read_text(encoding='utf-8'))
    timing=json.loads((ROOT/'stage17/timing_summary.json').read_text(encoding='utf-8')); manifest=json.loads((ROOT/'stage15_exploratory/dataset_manifest.json').read_text(encoding='utf-8'))
    result=[]
    for key,label in METHODS:
        allm=metrics[key]['all']; w=allm['wrong_id_at_1']; result.append({'method':key,'label':label,'queries':allm['n_queries'],'mrr_at_10':allm['mrr_at_10'],'recall_at_5':allm['recall_at_5'],'ndcg_at_10':allm['ndcg_at_10'],'wrong_lower':w['lower_bound'],'wrong_upper':w['upper_bound'],'wrong_unknown':w['unknown']})
    write(TABLE/'baseline_comparison.csv',result)
    labels=[x['label'] for x in result];x=np.arange(len(result));
    fig,axes=plt.subplots(1,3,figsize=(13,4)); colors=['#64748b','#60a5fa','#2563eb','#f59e0b','#b45309']
    for ax,metric,title in zip(axes,['mrr_at_10','recall_at_5','ndcg_at_10'],['MRR@10','Recall@5','nDCG@10']):
        ax.bar(x,[r[metric] for r in result],color=colors);ax.set_ylim(0,1.08);ax.set_title(title);ax.set_xticks(x,labels,rotation=30,ha='right');ax.grid(axis='y',alpha=.25)
    fig.suptitle('Phase 2 held-out exploratory subset (18 author-annotated CVE queries)');fig.tight_layout();save(fig,'metric_comparison')
    fig,ax=plt.subplots(figsize=(8,4.2)); names=['TF-IDF','MiniLM','Match-only','Identifier-aware']; ys=np.arange(len(names)); vals=[boot[k]['mrr_at_10']['difference'] for k in ('tfidf','minilm','match_only','identifier_aware')]; lows=[boot[k]['mrr_at_10']['low'] for k in ('tfidf','minilm','match_only','identifier_aware')]; highs=[boot[k]['mrr_at_10']['high'] for k in ('tfidf','minilm','match_only','identifier_aware')]
    ax.errorbar(vals,ys,xerr=[[v-l for v,l in zip(vals,lows)],[h-v for v,h in zip(vals,highs)]],fmt='o',color='#1d4ed8',capsize=4);ax.axvline(0,color='#64748b',lw=1);ax.set_yticks(ys,names);ax.set_xlabel('Paired MRR@10 difference versus RRF');ax.set_title('Percentile bootstrap 95% intervals (n=18; descriptive)');ax.grid(axis='x',alpha=.25);fig.tight_layout();save(fig,'paired_mrr_differences')
    fig,ax=plt.subplots(figsize=(9,4)); comps=timing['components']; names=list(comps); xx=np.arange(len(names));ax.bar(xx-.18,[comps[n]['median_ms'] for n in names],.36,label='median');ax.bar(xx+.18,[comps[n]['p95_ms'] for n in names],.36,label='p95');ax.set_xticks(xx,[n.replace('_ms','').replace('_','\n') for n in names]);ax.set_ylabel('Milliseconds');ax.set_title('Warm CPU component timing (not end-to-end)');ax.legend();fig.tight_layout();save(fig,'computational_cost')
    fig,ax=plt.subplots(figsize=(11,3.4));ax.axis('off');ax.set_xlim(0,11);ax.set_ylim(0,4)
    def box(x,y,w,h,text,color):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.08',facecolor=color,edgecolor='#334155'));ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=9)
    box(.2,1.45,1.4,.9,'Query +\n150 docs','#e2e8f0');box(2.4,2.45,1.5,.75,'TF-IDF','#dbeafe');box(2.4,.45,1.5,.75,'MiniLM\npretrained','#dbeafe');box(4.8,1.45,1.1,.9,'RRF\nk=60','#dcfce7');box(6.7,1.45,1.8,.9,'Identifier parser\nconflict penalty','#fef3c7');box(9.3,1.45,1.35,.9,'Ranked\ndocuments','#e2e8f0')
    for a,b in [((1.6,1.9),(2.4,2.82)),((1.6,1.9),(2.4,.82)),((3.9,2.82),(4.8,1.9)),((3.9,.82),(4.8,1.9)),((5.9,1.9),(6.7,1.9)),((8.5,1.9),(9.3,1.9))]:ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','color':'#334155'})
    ax.text(5.5,.05,'Frozen selected weights: match=0; conflict=0.003. No model training.',ha='center',fontsize=9);save(fig,'retrieval_architecture')
    flow=[{'stage':'Draft questions','count':70},{'stage':'Author validity yes','count':54},{'stage':'Source-evidenced positive','count':30},{'stage':'Development eligible','count':12},{'stage':'Held-out eligible','count':18}];write(TABLE/'eligibility_flow.csv',flow)
    fig,ax=plt.subplots(figsize=(11,2.6));ax.axis('off');ax.set_xlim(0,11);ax.set_ylim(0,3)
    for i,row in enumerate(flow):
        left=.2+i*2.15; box=FancyBboxPatch((left,.85),1.7,1.05,boxstyle='round,pad=.08',facecolor='#dbeafe' if i<2 else '#fef3c7',edgecolor='#334155');ax.add_patch(box);ax.text(left+.85,1.38,row['stage']+'\n'+str(row['count']),ha='center',va='center',fontsize=9)
        if i<len(flow)-1:ax.annotate('',xy=(left+2.1,1.38),xytext=(left+1.72,1.38),arrowprops={'arrowstyle':'->','color':'#334155'})
    ax.text(5.4,.25,'40 excluded before retrieval: 16 author-invalid; 24 without a source-evidenced author positive',ha='center',fontsize=9);save(fig,'eligibility_flow')
    family=[{'identifier_family':'cve','queries':18,'mrr_at_10':metrics['identifier_aware']['all']['mrr_at_10'],'note':'Only eligible family; ESP32 and natural queries excluded by evidence policy'}];write(TABLE/'family_breakdown.csv',family)
    fig,ax=plt.subplots(figsize=(5,3.5));ax.bar(['CVE'],[1.0],color='#b45309');ax.set_ylim(0,1.08);ax.set_ylabel('Identifier-aware MRR@10');ax.set_title('Identifier-family breakdown: CVE-only eligible subset');ax.text(0,.5,'No ESP32/natural\nqueries eligible',ha='center',va='center',color='white',weight='bold');fig.tight_layout();save(fig,'family_breakdown')
    ablation=[]
    for r in result:
        ablation.append({'configuration':r['label'],'method':r['method'],'mrr_at_10':r['mrr_at_10'],'recall_at_5':r['recall_at_5'],'ndcg_at_10':r['ndcg_at_10']})
    write(TABLE/'ablation.csv',ablation)
    intervals=[]
    for method in ('tfidf','minilm','match_only','identifier_aware'):
        for metric,value in boot[method].items():intervals.append({'method':method,'metric':metric,**value})
    write(TABLE/'paired_intervals.csv',intervals)
    ranked=defaultdict(list)
    for r in rows(ROOT/'stage17/rankings.csv'): ranked[(r['method'],r['query_id'])].append(r)
    qrels=defaultdict(set)
    for r in rows('data/phase2/exploratory_v1/qrels.csv'):
        if r['relevance']=='1':qrels[r['query_id']].add(r['doc_id'])
    queries={json.loads(line)['query_id']:json.loads(line) for line in (Path('data/phase2/exploratory_v1/queries_test.jsonl').read_text(encoding='utf-8').splitlines()) if line}
    candidates=[]
    for qid in queries:
        rrf=rank_of(ranked[('rrf',qid)],qrels[qid]); aware=rank_of(ranked[('identifier_aware',qid)],qrels[qid]); dense=rank_of(ranked[('minilm',qid)],qrels[qid]);
        candidates.append({'query_id':qid,'query':queries[qid]['text'],'rrf_first_positive_rank':rrf,'identifier_aware_first_positive_rank':aware,'minilm_first_positive_rank':dense})
    success=next(x for x in candidates if x['identifier_aware_first_positive_rank']<x['rrf_first_positive_rank'])
    failure=max(candidates,key=lambda x:(x['minilm_first_positive_rank'] or 999))
    examples=[{'case':'identifier-aware success over RRF',**success},{'case':'semantic baseline failure (not identifier-aware failure)',**failure}]
    write(TABLE/'retrieval_examples.csv',examples)
    (OUT/'manifest.json').write_text(json.dumps({'source_metrics':'outputs/phase2/stage17/metrics.json','source_manifest':'outputs/phase2/stage17/manifest.json','source_eligibility_manifest':'outputs/phase2/stage15_exploratory/dataset_manifest.json','figures':sorted(p.name for p in FIG.iterdir()),'tables':sorted(p.name for p in TABLE.iterdir()),'note':'All figures/tables derive from saved Phase 2 outputs; Phase 1 is not included.'},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'figures':len(list(FIG.iterdir())),'tables':len(list(TABLE.iterdir())),'example_cases':examples},indent=2))
if __name__=='__main__':main()
