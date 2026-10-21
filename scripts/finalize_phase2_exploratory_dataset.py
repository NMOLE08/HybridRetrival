"""Build an immutable derived exploratory dataset from author labels and source evidence.

This never edits the submitted workbook.  It deliberately does not add positives:
an author label survives as positive only with retained raw-source target evidence.
"""
import csv
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

ROOT = Path('data/phase2')
OUT = Path('outputs/phase2/stage15_exploratory')
FINAL = ROOT / 'exploratory_v1'

def jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]

def write_jsonl(path, rows):
    path.write_text(''.join(json.dumps(row, sort_keys=True, ensure_ascii=False)+'\n' for row in rows), encoding='utf-8')

def write_csv(path, rows, fields):
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def workbook_rows():
    spec = importlib.util.spec_from_file_location('review_validator', 'scripts/validate_phase2_human_review.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module.xlsx_rows(ROOT / 'review_v3/phase2_human_review_normalized.xlsx')

def main():
    if FINAL.exists() or OUT.exists():
        raise FileExistsError('Exploratory v1 already exists; preserve it and create a new version for a future amendment.')
    OUT.mkdir(parents=True); FINAL.mkdir(parents=True)
    questions, pairs = workbook_rows()
    needs = {x['need_id']: x for x in jsonl(ROOT / 'review_v2/needs.jsonl')}
    corpus = {x['doc_id']: x for x in jsonl(ROOT / 'corpus.jsonl')}
    with (ROOT / 'provenance.csv').open(encoding='utf-8', newline='') as handle:
        provenance = {x['doc_id']: x for x in csv.DictReader(handle)}
    raw = {doc_id: Path(row['raw_path']).read_text(encoding='utf-8').casefold() for doc_id, row in provenance.items()}

    positives = [p for p in pairs if str(p.get('human_relevance','')).strip() == '1']
    supported = set()
    source_audit = []
    for pair in pairs:
        need = needs[pair['need_id']]; target = str(need.get('target','')).casefold()
        label = str(pair.get('human_relevance','')).strip()
        raw_has_target = bool(target and target in raw[pair['doc_id']])
        canonical_source = need['family'] == 'cve' and pair['doc_id'].casefold() == target
        evidence_supported = label == '1' and raw_has_target and (canonical_source or raw_has_target)
        if evidence_supported: supported.add(pair['review_pair_id'])
        source_audit.append({
            'review_pair_id': pair['review_pair_id'], 'need_id': pair['need_id'], 'doc_id': pair['doc_id'],
            'author_label': label, 'target': need.get('target',''), 'raw_source_contains_target': str(raw_has_target).lower(),
            'canonical_target_source': str(canonical_source).lower(),
            'derived_label': '1' if evidence_supported else ('0' if label == '0' else 'unknown'),
            'audit_disposition': 'retained_positive_with_source_evidence' if evidence_supported else (
                'author_negative_retained' if label == '0' else 'author_positive_to_unknown_no_target_evidence' if label == '1' else 'unjudged_unknown'),
        })
    supported_by_need = Counter(next(x['need_id'] for x in pairs if x['review_pair_id'] == pair_id) for pair_id in supported)
    eligibility = []
    included = []
    for q in questions:
        need = needs[q['need_id']]; valid = str(q.get('question_valid','')).strip().lower()
        count = supported_by_need[q['need_id']]
        if valid != 'yes': status, reason = 'excluded', f'author question decision is {valid or "blank"}'
        elif count == 0: status, reason = 'excluded', 'no author positive with retained raw-source target evidence'
        else: status, reason = 'eligible', 'author-positive source evidence satisfies conservative eligibility policy'
        row = {'need_id':q['need_id'],'split':q['split'],'query':q['query'],'query_type':q['query_type'],'family':q['family'],
               'target':need.get('target',''),'author_question_valid':valid,'source_evidenced_positive_count':count,
               'eligibility':status,'reason':reason}
        eligibility.append(row)
        if status == 'eligible':
            included.append({'query_id':q['need_id'],'text':q['query'],'query_type':q['query_type'],'identifier_family':q['family'],
                             'split':q['split'],'target':need.get('target',''),'origin':'author_annotated_exploratory_v1'})
    included_ids = {x['query_id'] for x in included}
    qrels = []
    for row in source_audit:
        if row['need_id'] not in included_ids: continue
        qrels.append({'query_id':row['need_id'],'doc_id':row['doc_id'],'relevance':row['derived_label'],
                      'author_label':row['author_label'],'evidence_disposition':row['audit_disposition']})
    dev = [x for x in included if x['split'] == 'dev']; test = [x for x in included if x['split'] == 'test']
    write_jsonl(FINAL/'queries_dev.jsonl', dev); write_jsonl(FINAL/'queries_test.jsonl', test)
    write_csv(FINAL/'qrels.csv', qrels, ['query_id','doc_id','relevance','author_label','evidence_disposition'])
    write_csv(OUT/'query_eligibility.csv', eligibility, list(eligibility[0]))
    write_csv(OUT/'label_evidence_audit.csv', source_audit, list(source_audit[0]))
    manifest = {
        'dataset_version':'phase2_exploratory_v1','label_origin':'project_author; not independently verified',
        'corpus_path':'data/phase2/corpus.jsonl','corpus_sha256':sha256(ROOT/'corpus.jsonl'),
        'included_queries':len(included),'included_dev_queries':len(dev),'included_test_queries':len(test),
        'excluded_queries':len(questions)-len(included),'all_questions':len(questions),'original_pairs':len(pairs),
        'original_author_labels':dict(Counter(str(p.get('human_relevance','')).strip() for p in pairs)),
        'source_evidenced_author_positives':len(supported),'derived_qrels':dict(Counter(x['relevance'] for x in qrels)),
        'excluded_by_reason':dict(Counter(x['reason'] for x in eligibility if x['eligibility']=='excluded')),
        'unresolved_additional_candidates':sum(1 for _ in csv.DictReader((ROOT/'review_v3/additional_candidates.csv').open(encoding='utf-8-sig'))),
        'files':{name:sha256(FINAL/name) for name in ('queries_dev.jsonl','queries_test.jsonl','qrels.csv')},
        'selection_rule':'No retrieval output was read. Eligibility requires author validity yes plus an author-positive source whose pinned raw record contains the query target.',
        'limitations':['Author annotations are not independently verified.','Unjudged candidates remain unknown.','Excluded queries can only be recovered by a new versioned author adjudication.'],
    }
    (FINAL/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    (OUT/'dataset_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(manifest, indent=2))

if __name__ == '__main__': main()
