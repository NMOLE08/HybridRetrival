"""Build a source-traceable draft corpus from pinned CVEs and cached SoC headers."""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path

ROOT=Path('data/phase2')


def sha(raw):return hashlib.sha256(raw).hexdigest()


def main():
    output=ROOT/'corpus.jsonl'
    if output.exists():raise FileExistsError('Preserve the existing corpus; do not overwrite it')
    cves=json.loads(Path('outputs/phase2/manifests/source_collection.json').read_text(encoding='utf-8'))
    phase1=json.loads(Path('outputs/manifests/source_discovery.json').read_text(encoding='utf-8'))
    docs=[];provenance=[]
    def add(doc,source,revision,raw_hash,method,license_note):
        doc['content_sha256']=sha((doc['title']+'\n'+doc['text']).encode('utf-8'))
        docs.append(doc);provenance.append({'doc_id':doc['doc_id'],'origin_url':doc['source_url'],'origin_revision':revision,
            'raw_path':source,'raw_sha256':raw_hash,'content_sha256':doc['content_sha256'],'extraction_method':method,'rights':license_note})
    for source in cves['selected']:
        raw=Path(source['path']).read_bytes()
        if sha(raw)!=source['sha256']:raise ValueError(f'Source hash mismatch: {source["id"]}')
        record=json.loads(raw);descs=record['containers']['cna']['descriptions']
        text=next(x['value'].strip() for x in descs if x.get('lang','').lower().startswith('en') and x.get('value','').strip())
        doc={'doc_id':source['id'].lower(),'title':source['id'],'text':text,'source_url':source['url'],
             'source_type':'official CVE CNA description','family':'cve'}
        add(doc,source['path'],cves['revision'],source['sha256'],'First nonempty English CNA description; complete original text','CVE Program Terms of Use; see NOTICE.md')
    for source in phase1['records']:
        if source['id'].startswith('CVE-'):continue
        raw=Path(source['local_path']).read_bytes()
        if sha(raw)!=source['sha256']:raise ValueError(f'Cached SoC source hash mismatch: {source["id"]}')
        if b'SPDX-License-Identifier: Apache-2.0 OR MIT' not in raw[:500]:raise ValueError(f'Unverified license: {source["id"]}')
        path=ROOT/'sources/esp32'/f'{source["id"]}-soc_caps.h';path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists() and path.read_bytes()!=raw:raise ValueError(f'Existing source differs: {path}')
        path.write_bytes(raw)
        lines=raw.decode('utf-8').splitlines(keepends=True)
        chip=source['id'].upper().replace('ESP32','ESP32-',1).rstrip('-')
        for index in range(6):
            start=len(lines)*index//6;end=len(lines)*(index+1)//6
            text=''.join(lines[start:end]).strip()
            if not text:raise ValueError(f'Empty chunk: {source["id"]} {index}')
            doc={'doc_id':f'{source["id"]}-part{index+1}','title':f'{chip} SoC capabilities, source lines {start+1}-{end}',
                 'text':text,'source_url':source['url'],'source_type':'Espressif SoC capability source','family':'esp32'}
            add(doc,path.as_posix(),phase1['esp_idf_revision'],source['sha256'],f'Exact contiguous source lines {start+1}-{end}; preprocessor context may extend beyond chunk',
                'Apache-2.0 OR MIT per source header; MIT option; see NOTICE.md')
    if len({d['doc_id'] for d in docs})!=len(docs):raise ValueError('Duplicate doc ID')
    output.write_text(''.join(json.dumps(d,ensure_ascii=False)+'\n' for d in docs),encoding='utf-8',newline='\n')
    with (ROOT/'provenance.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(provenance[0]),lineterminator='\n');writer.writeheader();writer.writerows(provenance)
    print(f'Built {len(docs)} provisional passages: {len(cves["selected"])} CVE and {len(docs)-len(cves["selected"])} SoC chunks.')


if __name__=='__main__':main()
