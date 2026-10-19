"""Create a blinded, unjudged source-evidence package; no retriever is run."""
import csv
import hashlib
import json
import random
import re
from pathlib import Path

ROOT=Path('data/phase2')


def jsonl(p):return [json.loads(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip()]


def main():
    dest=ROOT/'review'
    if dest.exists():raise FileExistsError('Preserve existing review package')
    dest.mkdir(parents=True)
    docs=jsonl(ROOT/'corpus.jsonl');needs=jsonl(ROOT/'needs_draft.jsonl');by_id={d['doc_id']:d for d in docs}
    provenance={r['doc_id']:r for r in csv.DictReader((ROOT/'provenance.csv').open(encoding='utf-8',newline=''))}
    chip=lambda d:d['doc_id'].split('-part')[0]
    candidates=[];missing=[];source_crossrefs=[]
    for q in needs:
        selected=[]
        if q['family']=='cve':
            target=q['target'].lower()
            if target in by_id:selected.append(target)
            # Mention of the target in another record is a candidate, not a label.
            cross=[d['doc_id'] for d in docs if d['family']=='cve' and d['doc_id']!=target and q['target'].casefold() in d['text'].casefold()]
            if cross:source_crossrefs.append({'need_id':q['need_id'],'target':target,'candidates':cross})
            selected.extend(cross[:2])
            numeric=int(target.rsplit('-',1)[1]);year=target.split('-')[1]
            others=[d['doc_id'] for d in docs if d['family']=='cve' and d['doc_id']!=target and d['doc_id'].split('-')[1]==year]
            others.sort(key=lambda x:(abs(int(x.rsplit('-',1)[1])-numeric),x));selected.extend(others[:2])
        else:
            macro=q['expected_macro'];pattern=re.compile(r'^\s*#\s*define\s+'+re.escape(macro)+r'(?:\s|\(|$)',re.M)
            matches=[d for d in docs if d['family']=='esp32' and pattern.search(d['text'])]
            if q['family']=='esp32':
                target=q['target'].lower().replace('-','');selected.extend(d['doc_id'] for d in matches if chip(d)==target)
                if not selected:
                    missing.append({'need_id':q['need_id'],'reason':'No chunk containing expected macro for target variant; do not assume a negative. All source chunks for that variant are offered as context.'})
                    selected.extend(d['doc_id'] for d in docs if d['family']=='esp32' and chip(d)==target)
                selected.extend(d['doc_id'] for d in matches if chip(d)!=target)
            else:selected.extend(d['doc_id'] for d in matches)
            selected=selected[:6] if q['family']=='esp32' and any(x['need_id']==q['need_id'] for x in missing) else selected[:4]
        if not selected:
            if not any(x['need_id']==q['need_id'] for x in missing):missing.append({'need_id':q['need_id'],'reason':'No source candidate found under the initial evidence rule.'})
        for did in dict.fromkeys(selected):
            doc=by_id[did];p=provenance[did]
            candidates.append({'need_id':q['need_id'],'split':q['split'],'question':q['query'],'doc_id':did,
                'title':doc['title'],'passage':doc['text'],'source_url':doc['source_url'],'source_revision':p['origin_revision'],
                'source_raw_path':p['raw_path'],'source_sha256':p['raw_sha256'],
                'proposed_relevance':'unjudged','human_relevance':'','reviewer_id':'','independent_of_author':'',
                'reviewed_at_utc':'','confidence':'','evidence_or_reason':'','ambiguity_or_adjudication':''})
    random.Random(42).shuffle(candidates)
    for n,row in enumerate(candidates,1):row['review_pair_id']=f'pair-{n:04d}'
    fields=['review_pair_id',*([x for x in candidates[0] if x!='review_pair_id'])]
    with (dest/'candidate_pairs.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');writer.writeheader();writer.writerows(candidates)
    with (dest/'question_review.csv').open('w',encoding='utf-8-sig',newline='') as f:
        fields=['need_id','split','query','query_type','family','origin','topic_id','reviewer_id','independent_of_author','reviewed_at_utc','question_valid','rewrite_or_notes']
        writer=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');writer.writeheader()
        for q in needs:writer.writerow({k:q.get(k,'') for k in fields})
    (dest/'missing_candidates.json').write_text(json.dumps(missing,indent=2)+'\n',encoding='utf-8')
    (dest/'cross_reference_candidates.json').write_text(json.dumps(source_crossrefs,indent=2)+'\n',encoding='utf-8')
    summary={'queries':len(needs),'candidate_pairs':len(candidates),'needs_without_initial_evidence':len(missing),
             'cross_reference_query_count':len(source_crossrefs),'human_reviewed_pairs':0,'seed':42,
             'note':'Candidate selection uses explicit source IDs and macro-name lookups, not retrieval rankings; all relevance fields are unjudged.'}
    (dest/'manifest.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
