"""Validate returned review evidence, not the human's actual identity or expertise."""
import argparse
import csv
import hashlib
import json
import re
import sys
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path('data/phase2/review_v2')
NS = {'x': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
      'p': 'http://schemas.openxmlformats.org/package/2006/relationships'}

def csv_rows(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def xlsx_rows(path):
    """Read simple Excel values, including Excel's inline and shared strings; no formulas."""
    with zipfile.ZipFile(path) as z:
        book = ET.fromstring(z.read('xl/workbook.xml'))
        rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        targets = {x.attrib['Id']: x.attrib['Target'] for x in rels}
        strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            root = ET.fromstring(z.read('xl/sharedStrings.xml'))
            strings = [''.join(t.text or '' for t in si.findall('.//x:t', NS)) for si in root.findall('x:si', NS)]
        result = {}
        for sheet in book.findall('x:sheets/x:sheet', NS):
            name = sheet.attrib['name']
            if name not in ('Questions', 'Pairs'): continue
            target = targets[sheet.attrib['{%s}id' % NS['r']]].lstrip('/')
            target = target if target.startswith('xl/') else 'xl/' + target
            root = ET.fromstring(z.read(target)); grid = []
            for row in root.findall('x:sheetData/x:row', NS):
                cells = {}
                for cell in row.findall('x:c', NS):
                    if cell.find('x:f', NS) is not None: raise ValueError('Formula found in review sheet')
                    letters = re.match(r'[A-Z]+', cell.attrib['r']).group()
                    col = 0
                    for c in letters: col = col*26 + ord(c)-64
                    typ = cell.attrib.get('t'); v = cell.find('x:v', NS)
                    if typ == 'inlineStr': value = ''.join(t.text or '' for t in cell.findall('.//x:t', NS))
                    elif v is None: value = ''
                    elif typ == 's': value = strings[int(v.text)]
                    else: value = v.text or ''
                    cells[col-1] = value
                if cells:
                    grid.append([cells.get(i, '') for i in range(max(cells)+1)])
            if not grid: raise ValueError('Empty review sheet: '+name)
            headers = grid[0]
            if len(set(headers)) != len(headers) or '' in headers: raise ValueError('Invalid headers: '+name)
            result[name] = [dict(zip(headers, row + ['']*(len(headers)-len(row)))) for row in grid[1:]]
        if set(result) != {'Questions','Pairs'}: raise ValueError('Workbook must contain Questions and Pairs sheets')
        return result['Questions'], result['Pairs']

def utc_ok(value):
    try:
        dt = datetime.fromisoformat(value.strip().replace('Z', '+00:00'))
        return dt.tzinfo is not None and dt.utcoffset() == timedelta(0)
    except (ValueError, AttributeError): return False

def tokens(s): return set(re.findall(r'[a-z0-9]+', s.casefold()))
def overlap(a, b):
    x,y = tokens(a),tokens(b)
    return len(x & y)/len(x | y) if x | y else 1.0

def canonical(value):
    # XLSX/XML normalizes CRLF and CR line breaks to LF; do not treat that as a content edit.
    return str(value).replace('\r\n', '\n').replace('\r', '\n')

def validate(questions, pairs, reference_questions, reference_pairs, old_test):
    errors, pending, flags = [], [], []
    def indexed(items, key, label):
        out = {}
        for r in items:
            k = r.get(key, '')
            if not k or k in out: errors.append(f'{label}: missing or duplicate {key}: {k}')
            out[k] = r
        return out
    qmap = indexed(questions,'need_id','questions'); pmap = indexed(pairs,'review_pair_id','pairs')
    rq = indexed(reference_questions,'need_id','reference questions'); rp = indexed(reference_pairs,'review_pair_id','reference pairs')
    if set(qmap)!=set(rq): errors.append('Question IDs do not match the v2 package')
    if set(pmap)!=set(rp): errors.append('Pair IDs do not match the v2 package')
    qfixed = ['need_id','split','query','query_type','family','origin','topic_id']
    pfixed = ['review_pair_id','need_id','split','question','doc_id','title','passage','source_url','source_revision','source_raw_path','source_sha256']
    for k, q in qmap.items():
        if k not in rq: continue
        if any(str(q.get(f,'')) != str(rq[k].get(f,'')) for f in qfixed): errors.append(f'{k}: immutable question data changed; propose rewrite in notes')
        val = str(q.get('question_valid','')).strip().lower()
        if val not in ('yes','no','unknown',''): errors.append(f'{k}: question_valid must be yes, no or unknown')
        if not val: pending.append(f'{k}: missing question decision')
        elif val != 'yes': pending.append(f'{k}: question requires resolution ({val})')
        if val:
            if not str(q.get('reviewer_id','')).strip(): errors.append(f'{k}: missing reviewer_id')
            if str(q.get('independent_of_author','')).strip().lower() != 'yes': errors.append(f'{k}: independence must be attested yes')
            if not utc_ok(str(q.get('reviewed_at_utc',''))): errors.append(f'{k}: invalid UTC timestamp')
        for old in old_test:
            if overlap(q.get('query',''),old['text']) >= .60: flags.append(f"{k}: old test {old['query_id']} similarity >= 0.60; human semantic check required")
    positives = {k: 0 for k in qmap}
    for k,p in pmap.items():
        if k not in rp: continue
        if any(canonical(p.get(f,'')) != canonical(rp[k].get(f,'')) for f in pfixed): errors.append(f'{k}: immutable source or pair data changed')
        label = str(p.get('human_relevance','')).strip().lower()
        if label not in ('0','1','unknown',''): errors.append(f'{k}: relevance must be 0, 1 or unknown')
        if not label: pending.append(f'{k}: missing relevance decision')
        elif label == 'unknown': pending.append(f'{k}: unresolved unknown')
        elif label == '1' and p.get('need_id') in positives: positives[p['need_id']] += 1
        if label:
            if not str(p.get('reviewer_id','')).strip(): errors.append(f'{k}: missing reviewer_id')
            if str(p.get('independent_of_author','')).strip().lower() != 'yes': errors.append(f'{k}: independence must be attested yes')
            if not utc_ok(str(p.get('reviewed_at_utc',''))): errors.append(f'{k}: invalid UTC timestamp')
            if not str(p.get('evidence_or_reason','')).strip(): errors.append(f'{k}: missing source-specific evidence')
            if not str(p.get('confidence','')).strip(): errors.append(f'{k}: missing confidence')
            if not str(p.get('ambiguity_or_adjudication','')).strip(): errors.append(f'{k}: record uncertainty or none')
        if not str(p.get('source_url','')).startswith('https://'): errors.append(f'{k}: invalid source reference')
    for q,count in positives.items():
        if count == 0: pending.append(f'{q}: no independently reviewed positive')
    for q in qmap.values():
        for other in qmap.values():
            if q.get('split') == 'dev' and other.get('split') == 'test':
                if q.get('query','').strip().casefold() == other.get('query','').strip().casefold(): errors.append(f"identical cross-split query: {q['need_id']} / {other['need_id']}")
                if q.get('topic_id') and q.get('topic_id') == other.get('topic_id'): errors.append(f"shared cross-split topic: {q['need_id']} / {other['need_id']}")
                if overlap(q.get('query',''),other.get('query','')) >= .60: flags.append(f"cross-split similarity: {q['need_id']} / {other['need_id']}")
    return {'status':'BLOCKED' if errors or pending or flags else 'READY_FOR_MANUAL_GATE_REVIEW',
            'questions':len(questions),'pairs':len(pairs),'reviewed_questions':sum(bool(str(q.get('question_valid','')).strip()) for q in questions),
            'reviewed_pairs':sum(bool(str(p.get('human_relevance','')).strip()) for p in pairs),
            'questions_without_reviewed_positive':sum(v==0 for v in positives.values()),
            'errors':errors,'pending':pending,'overlap_flags':flags,
            'limitations':['Self-attested identity and independence cannot be verified by this script.',
             'Passing does not authorize tuning; a human must resolve validity, overlap, source coverage and the protocol gate.',
             'This initial source pool is not a complete retrieval pool.']}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--workbook',type=Path); ap.add_argument('--questions',type=Path); ap.add_argument('--pairs',type=Path)
    ap.add_argument('--output',type=Path); args=ap.parse_args()
    if args.workbook and (args.questions or args.pairs): ap.error('use workbook OR both CSVs')
    if args.workbook: questions,pairs=xlsx_rows(args.workbook)
    else: questions,pairs=csv_rows(args.questions or ROOT/'question_review.csv'),csv_rows(args.pairs or ROOT/'candidate_pairs.csv')
    old=[json.loads(x) for x in Path('data/technical/queries_test.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
    result=validate(questions,pairs,csv_rows(ROOT/'question_review.csv'),csv_rows(ROOT/'candidate_pairs.csv'),old)
    provenance={p['doc_id']:p for p in csv_rows(Path('data/phase2/provenance.csv'))}
    checked = {}
    for p in pairs:
        did = p.get('doc_id',''); source = provenance.get(did)
        if not source:
            result['errors'].append(f'{did}: no provenance record'); continue
        for field, origin in [('source_url','origin_url'),('source_revision','origin_revision'),('source_raw_path','raw_path'),('source_sha256','raw_sha256')]:
            if str(p.get(field,'')) != source[origin]: result['errors'].append(f"{p.get('review_pair_id','')}: {field} differs from provenance")
        if did not in checked:
            try: checked[did] = hashlib.sha256(Path(source['raw_path']).read_bytes()).hexdigest() == source['raw_sha256']
            except OSError: checked[did] = False
        if not checked[did]: result['errors'].append(f'{did}: missing raw source or SHA-256 mismatch')
    if result['errors']: result['status']='BLOCKED'
    out=json.dumps(result,indent=2,ensure_ascii=False)+'\n'
    if args.output: args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(out,encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('pending','errors','overlap_flags')},indent=2))
    print('errors:',len(result['errors']),'pending:',len(result['pending']),'overlap flags:',len(result['overlap_flags']))
    return 0 if result['status']=='READY_FOR_MANUAL_GATE_REVIEW' else 1

if __name__ == '__main__': sys.exit(main())
