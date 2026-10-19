"""Collect pinned public CVE records for prewritten needs and a seeded distractor sample.

No retrieval model, rankings, or relevance judgments are consulted. Raw records
are retained for provenance. A frozen selection manifest records failures too.
"""
from __future__ import annotations
import concurrent.futures
import hashlib
import json
import random
import itertools
import urllib.error
import urllib.request
from pathlib import Path
import truststore

REV='f36061cc9d42937cd6a7a7321a89da7ef625a190'
HEADERS={'User-Agent':'iphr-phase2-provenance/1.0','Accept':'application/vnd.github+json'}
ROOT=Path('data/phase2')


def get(url):
    req=urllib.request.Request(url,headers=HEADERS)
    with urllib.request.urlopen(req,timeout=45) as response:return response.read()


def cve_url(identifier):
    year,num=identifier.split('-')[1:];return f'https://raw.githubusercontent.com/CVEProject/cvelistV5/{REV}/cves/{year}/{int(num)//1000}xxx/{identifier}.json'


def main():
    truststore.inject_into_ssl()
    manifest=Path('outputs/phase2/manifests/source_collection.json')
    if manifest.exists():raise FileExistsError(f'Preserve existing collection: {manifest}')
    needs=[json.loads(x) for x in (ROOT/'needs_draft.jsonl').read_text(encoding='utf-8').splitlines()]
    targets=sorted({x['target'] for x in needs if x['family']=='cve'})
    excluded={json.loads(x)['doc_id'].upper() for x in Path('data/technical/corpus.jsonl').read_text(encoding='utf-8').splitlines()}
    buckets=[];index_meta=[]
    for year in (2022,2023,2024):
        url=f'https://api.github.com/repos/CVEProject/cvelistV5/contents/cves/{year}/0xxx?ref={REV}'
        raw=get(url);values=json.loads(raw)
        if not isinstance(values,list):raise ValueError(f'Unexpected index response: {url}')
        ids=sorted(x['name'].removesuffix('.json') for x in values if x.get('name','').startswith('CVE-') and x['name'].endswith('.json'))
        index_meta.append({'url':url,'sha256':hashlib.sha256(raw).hexdigest(),'entries':len(ids)})
        random.Random(42+year).shuffle(ids);buckets.append(ids[:90])
    candidate_ids=[i for triple in itertools.zip_longest(*buckets) for i in triple if i is not None]
    candidate_ids=[i for i in candidate_ids if i not in excluded and i not in targets]
    ordered=targets+candidate_ids
    print(f'Fetching {len(targets)} question-target records and {len(candidate_ids)} index candidates from the pinned CVE revision.',flush=True)
    def fetch(identifier):
        url=cve_url(identifier)
        try:
            raw=get(url);value=json.loads(raw)
            if value.get('cveMetadata',{}).get('state')!='PUBLISHED':return {'id':identifier,'url':url,'error':'not published'}
            descriptions=value.get('containers',{}).get('cna',{}).get('descriptions',[])
            text=next((d.get('value','') for d in descriptions if d.get('lang','').lower().startswith('en') and d.get('value','').strip()),'')
            if not text:return {'id':identifier,'url':url,'error':'no English CNA description'}
            return {'id':identifier,'url':url,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'raw':raw}
        except (OSError,ValueError,KeyError) as e:return {'id':identifier,'url':url,'error':str(e)}
    # Fetch in fixed batches, keeping order deterministic regardless of response timing.
    results=[];remaining=ordered[:];target_count=len(targets)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        while remaining and (len(results)<target_count or sum('raw' in x for x in results)<90):
            batch=remaining[:24];remaining=remaining[24:]
            results.extend(pool.map(fetch,batch))
            print(f'Fetched {len(results)} candidates; {sum("raw" in x for x in results)} usable so far.',flush=True)
    selected=[];failures=[]
    for r in results:
        if 'raw' not in r:failures.append(r);continue
        if r['id'] not in targets and len(selected)>=90:continue
        raw=r.pop('raw');path=ROOT/'sources/cve'/f"{r['id']}.json";path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists() and path.read_bytes()!=raw:raise ValueError(f'Existing source differs: {path}')
        path.write_bytes(raw);r['path']=path.as_posix();r['targeted_by_draft']=r['id'] in targets;selected.append(r)
    missing=sorted(set(targets)-{x['id'] for x in selected})
    output={'revision':REV,'index':index_meta,'seed':42,'selected':selected,'errors':failures,'missing_draft_targets':missing,
            'selection_note':'All available prewritten CVE targets first, followed by interleaved seeded filenames from 2022-2024 0xxx index lists; selection is not a representative sample.',
            'rights':'CVE Program Terms of Use; retained notice and upstream source metadata',
            'source':'https://github.com/CVEProject/cvelistV5'}
    manifest.parent.mkdir(parents=True,exist_ok=True);manifest.write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'selected':len(selected),'failed':len(failures),'missing_draft_targets':missing},indent=2))


if __name__=='__main__':main()
