"""Build paper figures and tables from saved experiment outputs, never hard-coded measurements."""
from pathlib import Path
import json
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd
import yaml

FINAL = Path('outputs/final')
FIG = Path('outputs/figures')
TABLE = Path('outputs/tables')
METHODS = [('tfidf','TF-IDF'),('minilm','MiniLM'),('rrf','RRF'),
           ('rrf_bonus','Bonus\nselected'),('proposed','Full\nselected'),
           ('rrf_bonus_fixed','Bonus\nexploratory'),('proposed_fixed','Full\nexploratory')]


def save(name):
    plt.savefig(FIG / (name + '.png'), dpi=250, bbox_inches='tight')
    plt.savefig(FIG / (name + '.svg'), bbox_inches='tight')
    plt.close()


def architecture(config):
    fig, ax = plt.subplots(figsize=(10, 3.7)); ax.set_xlim(0,10); ax.set_ylim(0,4); ax.axis('off')
    def box(x,y,w,h,label,color):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.08',facecolor=color,edgecolor='#334155'))
        ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontsize=10)
    box(.2,1.4,1.5,1.1,'Query +\ncorpus','#e2e8f0')
    box(2.5,2.5,1.6,.8,'TF-IDF','#dbeafe');box(2.5,.5,1.6,.8,'MiniLM\n(frozen)','#dbeafe')
    box(5,1.4,1.1,1.1,'RRF','#dcfce7');box(7,1.4,1.6,1.1,'Identifier parser\n+ reranker','#fef3c7')
    box(9.1,1.4,.8,1.1,'Ranked\ndocs','#e2e8f0')
    for start,end in [((1.7,1.95),(2.5,2.9)),((1.7,1.95),(2.5,.9)),((4.1,2.9),(5,1.95)),((4.1,.9),(5,1.95)),((6.1,1.95),(7,1.95)),((8.6,1.95),(9.1,1.95))]:
        ax.annotate('',xy=end,xytext=start,arrowprops={'arrowstyle':'->','color':'#334155','lw':1.3})
    ax.text(5,-.05,f"Primary selected weights: match = {config['lambda_match']}, conflict = {config['lambda_conflict']}; nonzero variants are exploratory.",ha='center',fontsize=9)
    save('architecture')


def main():
    FIG.mkdir(parents=True,exist_ok=True); TABLE.mkdir(parents=True,exist_ok=True)
    data=json.loads((FINAL/'metrics.json').read_text(encoding='utf-8'))['methods']
    timing=json.loads((FINAL/'timing_summary.json').read_text(encoding='utf-8'))
    dense=json.loads(Path('outputs/examples/dense_demo.json').read_text(encoding='utf-8'))
    boot=json.loads((FINAL/'paired_bootstrap.json').read_text(encoding='utf-8'))
    rankings=pd.read_csv(FINAL/'rankings.csv'); per=pd.read_csv(FINAL/'per_query.csv')
    queries={q['query_id']:q for q in (json.loads(line) for line in Path('data/technical/queries_test.jsonl').read_text(encoding='utf-8').splitlines())}
    architecture(yaml.safe_load(Path('configs/final.yaml').read_text(encoding='utf-8')))
    rows=[]
    for key,label in METHODS:
        m=data[key]['type:identifier']; w=m['wrong_id_at_1']
        rows.append({'method':key,'label':label.replace('\n',' '),'n_queries':m['n_queries'],
                     'mrr_at_10':m['mrr_at_10'],'recall_at_5':m['recall_at_5'],
                     'ndcg_at_10':m['ndcg_at_10'],'wrong_id_lower':w['lower_bound'],
                     'wrong_id_upper':w['upper_bound'],'wrong_id_observed':w['wrong'],
                     'wrong_id_unknown':w['unknown'],'wrong_id_eligible':w['eligible']})
    result=pd.DataFrame(rows);result.to_csv(TABLE/'identifier_metrics.csv',index=False)
    x=np.arange(len(rows)); colors=['#94a3b8','#94a3b8','#2563eb','#60a5fa','#1d4ed8','#f59e0b','#b45309']
    fig, axes=plt.subplots(1,2,figsize=(12,4.5),sharey=True)
    for ax,metric,title in zip(axes,['recall_at_5','mrr_at_10'],['Recall@5','MRR@10']):
        ax.bar(x,result[metric],color=colors);ax.set_title(title);ax.set_ylim(0,1.1);ax.set_ylabel('Mean per query');ax.set_xticks(x,[v[1] for v in METHODS],rotation=35,ha='right');ax.grid(axis='y',alpha=.2)
    fig.suptitle(f'Identifier queries (n={rows[0]["n_queries"]}); nonzero weights are exploratory',fontsize=11);fig.tight_layout();save('identifier_effectiveness')
    subset=result[result.method.isin(['rrf','rrf_bonus','proposed','rrf_bonus_fixed','proposed_fixed'])]
    fig,ax=plt.subplots(figsize=(8,4.5));xx=np.arange(len(subset));low=subset.wrong_id_lower.to_numpy();high=subset.wrong_id_upper.to_numpy()
    ax.bar(xx,low,color='#b45309',label='Observed lower bound');ax.bar(xx,high-low,bottom=low,color='#fcd34d',hatch='//',label='Unjudged uncertainty')
    ax.set_xticks(xx,subset.label,rotation=22,ha='right');ax.set_ylim(0,1);ax.set_ylabel('WrongIdentifier@1 fraction');ax.set_title(f'Wrong-ID bounds (eligible n={int(subset.wrong_id_eligible.iloc[0])})');ax.legend();fig.tight_layout();save('wrong_identifier_bounds')
    components=timing['components'];names=list(components);med=[components[k]['median'] for k in names];p95=[components[k]['p95'] for k in names]
    fig,ax=plt.subplots(figsize=(9,4.5));xx=np.arange(len(names));ax.bar(xx-.18,med,.36,label='median');ax.bar(xx+.18,p95,.36,label='p95');ax.set_xticks(xx,[x.replace('_ms','').replace('_','\n') for x in names]);ax.set_ylabel('Warm component time (ms)');ax.set_title(f'Sequential CPU components (n={timing["samples"]} each; not end-to-end)');ax.legend();fig.tight_layout();save('latency_components')
    one={'Model load (final run)':timing['model_load_seconds'],'TF-IDF index (final run)':timing['lexical_index_build_seconds'],'Cached embedding load (final run)':timing['embedding_cache_load_or_build_seconds'],'Embedding build (earlier uncached run)':dense['technical_preprocessing_seconds']}
    fig,ax=plt.subplots(figsize=(9,4));ax.barh(list(one),list(one.values()),color='#0f766e');ax.set_xlabel('Seconds');ax.set_title('One-time costs; embedding build measured in an earlier run');fig.tight_layout();save('latency_one_time')
    cases=[]
    for category,qid in [('exploratory success','test01'),('selected-method failure','test04'),('natural no-change','test11')]:
        entry={'case':category,'query_id':qid,'query':queries[qid]['text']}
        for method in ('rrf','proposed','proposed_fixed'):
            r=rankings[(rankings.query_id==qid)&(rankings.method==method)].sort_values('rank')
            p=per[(per.query_id==qid)&(per.method==method)].iloc[0]
            entry[method+'_top_doc']=r.iloc[0].doc_id;entry[method+'_mrr_at_10']=p.mrr_at_10
        cases.append(entry)
    cases=pd.DataFrame(cases);cases.to_csv(TABLE/'case_studies.csv',index=False)
    summary=result[['label','n_queries','mrr_at_10','recall_at_5','ndcg_at_10','wrong_id_lower','wrong_id_upper']].copy()
    (TABLE/'identifier_metrics.tex').write_text(summary.to_latex(index=False,float_format=lambda x:f'{x:.3f}',escape=True),encoding='utf-8')
    compact=cases[['case','query_id','rrf_top_doc','rrf_mrr_at_10','proposed_fixed_top_doc','proposed_fixed_mrr_at_10']]
    (TABLE/'case_studies.tex').write_text(compact.to_latex(index=False,float_format=lambda x:f'{x:.3f}',escape=True),encoding='utf-8')
    (TABLE/'paired_bootstrap.json').write_text(json.dumps(boot,indent=2)+'\n',encoding='utf-8')
    print('Wrote 5 figures (SVG and PNG), identifier metrics, case studies, and bootstrap table from saved run files.')


if __name__=='__main__': main()
