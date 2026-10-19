"""Validate source integrity and report review/split gaps without inventing labels."""
import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT=Path('data/phase2')
def read(p):return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def sha(b):return hashlib.sha256(b).hexdigest()
def tokens(s):return set(re.findall(r'[a-z0-9]+',s.casefold()))
def similarity(a,b):return len(a&b)/len(a|b) if a|b else 1.0


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='outputs/phase2/manifests/dataset_validation.json');args=parser.parse_args()
    output=Path(args.output)
    if output.exists():raise FileExistsError('Preserve previous validation output; select a new --output')
    docs=read(ROOT/'corpus.jsonl');needs=read(ROOT/'needs_draft.jsonl');old=read(Path('data/technical/queries_test.jsonl'))
    with (ROOT/'provenance.csv').open(encoding='utf-8',newline='') as f:prov=list(csv.DictReader(f))
    with (ROOT/'review/candidate_pairs.csv').open(encoding='utf-8-sig',newline='') as f:reviews=list(csv.DictReader(f))
    errors=[]
    if len({d['doc_id'] for d in docs})!=len(docs):errors.append('duplicate document ID')
    if len({q['need_id'] for q in needs})!=len(needs):errors.append('duplicate query ID')
    if len({q['query'].casefold().strip() for q in needs})!=len(needs):errors.append('duplicate query text')
    if set(d['doc_id'] for d in docs)!=set(p['doc_id'] for p in prov):errors.append('provenance/document mismatch')
    by_id={d['doc_id']:d for d in docs}
    for p in prov:
        raw=Path(p['raw_path']).read_bytes();d=by_id[p['doc_id']]
        if sha(raw)!=p['raw_sha256'] or sha((d['title']+'\n'+d['text']).encode('utf-8'))!=p['content_sha256']:errors.append(f'hash mismatch: {p["doc_id"]}')
        if not p['origin_url'].startswith('https://') or not p['rights']:errors.append(f'missing provenance/rights: {p["doc_id"]}')
    overlap=set(q['query'].casefold().strip() for q in needs)&set(q['text'].casefold().strip() for q in old)
    if overlap:errors.append('exact query reuse from old pilot test')
    dev=[q for q in needs if q['split']=='dev'];test=[q for q in needs if q['split']=='test']
    groups=set(q['topic_id'] for q in dev)&set(q['topic_id'] for q in test)
    if groups:errors.append('shared exact topic IDs between splits: '+str(sorted(groups)))
    pairs=[]
    for a in dev:
        for b in test:
            j=similarity(tokens(a['query']),tokens(b['query']))
            if j>=.60:pairs.append({'dev':a['need_id'],'test':b['need_id'],'token_jaccard':round(j,4)})
    old_pairs=[]
    for a in needs:
        for b in old:
            j=similarity(tokens(a['query']),tokens(b['text']))
            if j>=.60:old_pairs.append({'phase2':a['need_id'],'phase1_test':b['query_id'],'token_jaccard':round(j,4)})
    missing=json.loads((ROOT/'review/missing_candidates.json').read_text(encoding='utf-8'))
    summary=json.loads((ROOT/'review/manifest.json').read_text(encoding='utf-8'))
    result={'status':'PROVISIONAL','structural_errors':errors,'documents':len(docs),'families':dict(Counter(d['family'] for d in docs)),
            'queries':len(needs),'split_type_counts':{f'{k[0]}:{k[1]}':v for k,v in Counter((q['split'],q['query_type']) for q in needs).items()},
            'exact_old_test_query_overlap':len(overlap),'exact_topic_overlap':sorted(groups),
            'cross_split_jaccard_ge_0_60':pairs,'old_test_jaccard_ge_0_60':old_pairs,
            'missing_initial_evidence':missing,'review':summary,'pair_rows':len(reviews),
            'human_reviewed_rows':sum(bool(r['human_relevance']) for r in reviews),
            'limits':['Token overlap is a screening heuristic, not a semantic independence test.',
                      'All questions and candidate pairs are unreviewed drafts; a match is not a positive judgment.',
                      'Sample, confusable and cross-reference targets and human-review gate are not yet met.']}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','structural_errors','documents','families','queries','split_type_counts','missing_initial_evidence','human_reviewed_rows')},indent=2))
    print('Cross-split similarity flags:',len(pairs),'Phase 1 test similarity flags:',len(old_pairs))
    if errors:raise SystemExit(1)


if __name__=='__main__':main()
