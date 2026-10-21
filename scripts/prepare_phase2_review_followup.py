"""Create review-only follow-up materials from a submitted workbook; never assign labels."""
import csv
import importlib.util
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path('data/phase2')
OUT = Path('outputs/phase2/stage15')
REVIEW3 = ROOT / 'review_v3'

def jsonl(path):
    return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]

def load_validator():
    spec = importlib.util.spec_from_file_location('review_validator', 'scripts/validate_phase2_human_review.py')
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def write_csv(path, records):
    if not records: return
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(records[0]), lineterminator='\n')
        w.writeheader(); w.writerows(records)

def is_invalid(value):
    """Accept the submitted workbook's original numeric or normalized wording."""
    return str(value).strip().lower() in {'0', 'no'}

def main():
    OUT.mkdir(parents=True, exist_ok=True); REVIEW3.mkdir(parents=True, exist_ok=True)
    validator = load_validator()
    questions, pairs = validator.xlsx_rows(ROOT / 'review_v2/phase2_human_review.xlsx')
    needs = {x['need_id']: x for x in jsonl(ROOT / 'review_v2/needs.jsonl')}
    docs = {x['doc_id']: x for x in jsonl(ROOT / 'corpus.jsonl')}
    with (ROOT / 'provenance.csv').open(encoding='utf-8', newline='') as f: provenance = {x['doc_id']:x for x in csv.DictReader(f)}
    positives = Counter(x['need_id'] for x in pairs if x['human_relevance'].strip() == '1')
    existing = {(x['need_id'], x['doc_id']) for x in pairs}
    invalid = [x for x in questions if is_invalid(x['question_valid'])]
    uncovered = [x for x in questions if positives[x['need_id']] == 0]
    added = []
    for q in uncovered:
        need = needs[q['need_id']]; macro = need.get('expected_macro') or ''
        if not macro:
            continue
        pattern = re.compile(r'^\s*#\s*define\s+' + re.escape(macro) + r'(?:\s|\(|$)', re.M)
        candidates = [d for d in docs.values() if d['family'] == 'esp32' and pattern.search(d['text']) and (q['need_id'],d['doc_id']) not in existing]
        candidates.sort(key=lambda d: d['doc_id'])
        for d in candidates:
            p=provenance[d['doc_id']]
            added.append({'review_pair_id':f'followup-{len(added)+1:04d}','need_id':q['need_id'],'split':q['split'],
                          'question':q['query'],'doc_id':d['doc_id'],'title':d['title'],'passage':d['text'],
                          'source_url':d['source_url'],'source_revision':p['origin_revision'],'source_raw_path':p['raw_path'],
                          'source_sha256':p['raw_sha256'],'candidate_basis':f'existing pinned corpus contains {macro}',
                          'human_relevance':'','reviewer_id':'','independent_of_author':'','reviewed_at_utc':'',
                          'confidence':'','evidence_or_reason':'','ambiguity_or_adjudication':''})
    # Do not overwrite a returned reviewer follow-up file.
    if (REVIEW3 / 'additional_candidates.csv').exists():
        raise FileExistsError('Preserve review_v3; choose a new version for any later changes')
    write_csv(REVIEW3 / 'additional_candidates.csv', added)
    report_rows=[]
    for q in questions:
        n=needs[q['need_id']]; need_added=[x for x in added if x['need_id']==q['need_id']]
        disposition=[]
        if is_invalid(q['question_valid']): disposition.append('Reviewer marked question invalid; human must correct or exclude it explicitly.')
        if positives[q['need_id']] == 0:
            if need_added: disposition.append(f'{len(need_added)} unjudged existing-corpus macro candidate(s) prepared for review.')
            else: disposition.append('No additional existing-corpus candidate found under macro evidence rule; correct, exclude, or add separately sourced evidence under a new reviewed version.')
        if q['need_id'] in ('esp-08','esp-11','esp-13'): disposition.append('Known hardware-evidence ambiguity; missing macro is not a negative.')
        if not disposition: continue
        report_rows.append({'need_id':q['need_id'],'split':q['split'],'question':q['query'],'submitted_question_decision':q['question_valid'],
                            'submitted_positive_count':positives[q['need_id']],'expected_macro':n.get('expected_macro',''),
                            'additional_unjudged_candidates':len(need_added),'required_action':' '.join(disposition)})
    write_csv(OUT/'review_followup_requirements.csv',report_rows)
    manifest={'submitted_questions':len(questions),'submitted_pairs':len(pairs),'invalid_questions':[x['need_id'] for x in invalid],
              'questions_without_positive':[x['need_id'] for x in uncovered],'additional_unjudged_candidates':len(added),
              'note':'Additional candidates are source-evidence candidates only; no human labels, evidence, metadata, or timestamps were created.'}
    (OUT/'review_followup_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    # Input for the separate simplified follow-up workbook.
    (OUT/'review_followup_workbook_input.json').write_text(json.dumps({'questions':questions,'pairs':pairs,'requirements':report_rows,'additional':added},ensure_ascii=False),encoding='utf-8')
    print(json.dumps(manifest,indent=2))

if __name__ == '__main__': main()
