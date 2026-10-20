"""Create a separate, unjudged source-evidence review v2; never run retrieval."""
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path('data/phase2')
OUT = ROOT / 'review_v2'
AUDIT = Path('outputs/phase2/stage14b')

def rows(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def jsonl(path):
    return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]

def write_csv(path, data):
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(data[0]), lineterminator='\n')
        w.writeheader(); w.writerows(data)

def edit_distance(a, b):
    row = list(range(len(b)+1))
    for i, ca in enumerate(a, 1):
        next_row = [i]
        for j, cb in enumerate(b, 1):
            next_row.append(min(next_row[-1]+1, row[j]+1, row[j-1]+(ca != cb)))
        row = next_row
    return row[-1]

def main():
    OUT.mkdir(parents=True, exist_ok=True); AUDIT.mkdir(parents=True, exist_ok=True)
    for name, fields in [('question_review.csv', ('question_valid','reviewer_id','reviewed_at_utc')),
                         ('candidate_pairs.csv', ('human_relevance','reviewer_id','reviewed_at_utc'))]:
        existing = OUT/name
        if existing.exists() and any(any(row.get(f,'').strip() for f in fields) for row in rows(existing)):
            raise ValueError('Refusing to overwrite review work: '+str(existing))
    needs = jsonl(ROOT / 'needs_draft.jsonl')
    docs = {x['doc_id']: x for x in jsonl(ROOT / 'corpus.jsonl')}
    provenance = {x['doc_id']: x for x in rows(ROOT / 'provenance.csv')}
    old_questions = rows(ROOT / 'review/question_review.csv')
    old_pairs = rows(ROOT / 'review/candidate_pairs.csv')
    assert len(needs) == len(old_questions) == 70 and len(old_pairs) == 241
    changes = {
      'esp-01': ('Do the ESP32-C2 capability definitions indicate SHA-256 support?', 'SOC_SHA_SUPPORT_SHA256'),
      'esp-02': ('Do the ESP32-C5 capability definitions indicate AES-256 support?', 'SOC_AES_SUPPORT_AES_256'),
      'esp-03': ('Do the ESP32-S2 capability definitions indicate HMAC support?', 'SOC_HMAC_SUPPORTED'),
      'natural-01': ('Find a chip capability definition indicating SHA-256 hardware hashing support.', 'SOC_SHA_SUPPORT_SHA256'),
      'natural-02': ('Find a chip capability definition indicating AES-256 cryptographic support.', 'SOC_AES_SUPPORT_AES_256'),
      'natural-03': ('Find a chip capability definition indicating secure boot support.', 'SOC_SECURE_BOOT_SUPPORTED'),
    }
    changelog = []
    for q in needs:
        if q['need_id'] in changes:
            text, macro = changes[q['need_id']]
            changelog.append({'need_id': q['need_id'], 'old_question': q['query'], 'old_macro': q['expected_macro'],
                              'new_question': text, 'new_macro': macro,
                              'reason': 'old-test topic similarity; replacement proposed after inspecting pinned source; needs human approval'})
            q['query'], q['expected_macro'] = text, macro
            if q['query_type'] == 'natural':
                changelog[-1]['old_topic_id'] = q['topic_id']; changelog[-1]['new_topic_id'] = macro
                q['topic_id'] = macro
            q['origin'] = 'agent_authored_source_conditioned_stage14b'
            q['evidence_status'] = 'source_candidate_only_not_human_judged'
        elif q['need_id'] == 'cve-07':
            revised = 'What Microsoft Exchange vulnerability is described by CVE-2020-0688?'
            changelog.append({'need_id':q['need_id'], 'old_question':q['query'], 'old_macro':'',
                              'new_question':revised, 'new_macro':'',
                              'reason':'pinned target description reports memory corruption but does not name the requested control; source-conditioned proposal needs human approval'})
            q['query'] = revised
            q['origin'] = 'agent_authored_source_conditioned_stage14b'
            q['evidence_status'] = 'source_candidate_only_not_human_judged'
    by_need = {x['need_id']: x for x in needs}
    questions = []
    for row in old_questions:
        row['query'] = by_need[row['need_id']]['query']; row['origin'] = by_need[row['need_id']]['origin']; row['topic_id'] = by_need[row['need_id']]['topic_id']
        questions.append(row)
    pairs = []
    for row in old_pairs:
        row['question'] = by_need[row['need_id']]['query']
        pairs.append(row)
    # Keep all existing pair IDs and assignments, even when the question changed.
    # Add source-macro candidates without assigning relevance.
    for need_id in changes:
        q = by_need[need_id]
        pattern = re.compile(r'^\s*#\s*define\s+' + re.escape(q['expected_macro']) + r'(?:\s|\(|$)', re.M)
        target = (q['target'] or '').lower().replace('-', '')
        hits = [d for d in docs.values() if d['family'] == 'esp32' and pattern.search(d['text'])]
        hits.sort(key=lambda d: (not bool(target and d['doc_id'].startswith(target + '-part')), d['doc_id']))
        for d in hits[:4]:
            if any(r['need_id'] == need_id and r['doc_id'] == d['doc_id'] for r in pairs):
                continue
            p = provenance[d['doc_id']]
            row = dict.fromkeys(old_pairs[0], '')
            row.update(review_pair_id=f'pair-{len(pairs)+1:04d}', need_id=need_id, split=q['split'], question=q['query'],
                       doc_id=d['doc_id'], title=d['title'], passage=d['text'], source_url=d['source_url'],
                       source_revision=p['origin_revision'], source_raw_path=p['raw_path'], source_sha256=p['raw_sha256'], proposed_relevance='unjudged')
            pairs.append(row)
    # Add actual same-year CVE records within two edits, not synthetic identifiers.
    for q in needs:
        if q['family'] != 'cve': continue
        target = q['target'].lower()
        for d in docs.values():
            other = d['doc_id']
            if d['family'] != 'cve' or other == target or other.split('-')[1] != target.split('-')[1]: continue
            if edit_distance(target, other) > 2 or any(r['need_id']==q['need_id'] and r['doc_id']==other for r in pairs): continue
            p = provenance[other]; row = dict.fromkeys(old_pairs[0], '')
            row.update(review_pair_id=f'pair-{len(pairs)+1:04d}', need_id=q['need_id'], split=q['split'], question=q['query'],
                       doc_id=other, title=d['title'], passage=d['text'], source_url=d['source_url'],
                       source_revision=p['origin_revision'], source_raw_path=p['raw_path'], source_sha256=p['raw_sha256'], proposed_relevance='unjudged')
            pairs.append(row)
    assert len({p['review_pair_id'] for p in pairs}) == len(pairs)
    write_csv(OUT / 'question_review.csv', questions); write_csv(OUT / 'candidate_pairs.csv', pairs)
    (OUT / 'needs.jsonl').write_text(''.join(json.dumps(q, ensure_ascii=False)+'\n' for q in needs), encoding='utf-8')
    (OUT / 'change_log.json').write_text(json.dumps(changelog, indent=2)+'\n', encoding='utf-8')
    # Per-row AI-assisted pre-review: mechanical signals and source context, NOT judgments.
    pair_audit = []
    for p in old_pairs:
        q = next(q for q in jsonl(ROOT / 'needs_draft.jsonl') if q['need_id'] == p['need_id'])
        d = docs[p['doc_id']]; source = provenance[p['doc_id']]
        raw = Path(source['raw_path']).read_bytes()
        fulltext = raw.decode('utf-8')
        if d['family'] == 'cve':
            descriptions = json.loads(fulltext)['containers']['cna']['descriptions']
            extracted = next(x['value'].strip() for x in descriptions if x.get('lang','').lower().startswith('en') and x.get('value','').strip())
            in_source = d['text'] == extracted
        else:
            normalize = lambda x:x.replace('\r\n','\n').replace('\r','\n')
            in_source = normalize(d['text']) in normalize(fulltext)
        reasons = []
        if p['passage'] != d['text']: reasons.append('passage differs from corpus')
        if hashlib.sha256(raw).hexdigest() != source['raw_sha256']: reasons.append('raw hash mismatch')
        if p['source_url'] != source['origin_url']: reasons.append('source URL mismatch')
        if not in_source: reasons.append('passage differs from pinned source extraction')
        if p['source_revision'] != source['origin_revision'] or p['source_raw_path'] != source['raw_path'] or p['source_sha256'] != source['raw_sha256']: reasons.append('source provenance fields mismatch')
        if '\ufffd' in d['text']: reasons.append('source passage contains Unicode replacement character; inspect original and clarify')
        if q['family'] != 'cve':
            reasons.append('header excerpt: inspect full source and enclosing preprocessor conditions')
            if q['need_id'] in ('esp-08', 'esp-11', 'esp-13'): reasons.append('target macro absent: absence is not proof; external evidence and corpus support require review')
        else:
            target = q['target'].casefold()
            if target in d['text'].casefold() and d['doc_id'] != target: reasons.append('cross-reference mention: context may or may not answer need')
            if d['doc_id'] != target: reasons.append('different CVE title: do not assume irrelevant')
        if q['need_id'] in (*changes, 'cve-07'): reasons.append('v1 question superseded in v2; old pair remains for audit')
        macro = q.get('expected_macro') or ''
        macro_lines = [line.strip() for line in d['text'].splitlines() if macro and re.match(r'^\s*#\s*define\s+'+re.escape(macro)+r'(?:\s|\(|$)',line)]
        if q['family'] != 'cve' and not macro_lines: reasons.append('requested macro not defined in this excerpt; check context and relevance')
        pair_audit.append({'review_pair_id':p['review_pair_id'], 'need_id':p['need_id'], 'doc_id':p['doc_id'],
                           'question':p['question'], 'source_url':p['source_url'], 'raw_source':source['raw_path'],
                           'expected_macro_line_in_excerpt':' | '.join(macro_lines),
                           'cve_identifiers_in_excerpt':' | '.join(sorted(set(re.findall(r'\bCVE-\d{4}-\d{4,}\b',d['text'],re.I)))),
                           'preprocessor_directives_in_excerpt':str(bool(re.search(r'^\s*#\s*(?:if|ifdef|ifndef|elif|else|endif)\b',d['text'],re.M))).lower() if d['family']=='esp32' else 'not_applicable',
                           'passage_matches_corpus':str(p['passage']==d['text']).lower(),
                           'raw_sha256_matches':str(hashlib.sha256(raw).hexdigest()==source['raw_sha256']).lower(),
                           'source_url_matches':str(p['source_url']==source['origin_url']).lower(),
                           'source_extraction_matches':str(in_source).lower(),
                           'provenance_fields_match':str(p['source_revision']==source['origin_revision'] and p['source_raw_path']==source['raw_path'] and p['source_sha256']==source['raw_sha256']).lower(),
                           'target_macro_in_full_source':str(bool(q.get('expected_macro') and re.search(r'^\s*#\s*define\s+'+re.escape(q['expected_macro'])+r'(?:\s|\(|$)',fulltext,re.M))).lower() if q.get('expected_macro') else 'not_applicable',
                           'pre_review_flags':'; '.join(reasons) or 'Inspect answer scope and source; no judgment assigned.'})
    write_csv(AUDIT/'v1_pair_audit.csv', pair_audit)
    q_audit = []
    for q in jsonl(ROOT/'needs_draft.jsonl'):
        ps = [p for p in old_pairs if p['need_id']==q['need_id']]
        target = (q.get('target') or '').lower()
        candidates = [p for p in ps if (p['doc_id']==target if q['family']=='cve' else bool(target) and p['doc_id'].startswith(target.replace('-','')+'-part') and q.get('expected_macro','') in p['passage'])]
        flags = ['Human must check question validity and candidate relevance; no positive assumed.']
        if q['need_id'] in changes: flags.append('Similar to Phase 1 test topic; source-conditioned v2 replacement proposed.')
        if q['need_id'] == 'cve-07': flags.append('Target description names memory corruption but does not identify the requested Exchange control; source-conditioned broader replacement proposed.')
        if q['need_id'] == 'cve-01': flags.append('Target names affected products but may not identify a specific component; review scope.')
        if q['need_id'] in ('cve-15','cve-18'): flags.append('Target description is terse about product identity; inspect full CVE record and decide whether passage/title suffices.')
        if q['need_id'] in ('esp-08','esp-11','esp-13'): flags.append('No explicit target capability macro in pinned source; investigate full context and official sources.')
        if q['query_type'] == 'natural': flags.append('No single chip requested; multiple relevant passages possible and candidate coverage is incomplete.')
        if q['family'] == 'cve': flags.append('Check that target description actually answers requested detail and watch related-CVE cross-references.')
        q_audit.append({'need_id':q['need_id'],'split':q['split'],'question':q['query'],'candidate_count':len(ps),
                        'target_or_macro_candidate_count':len(candidates) if q.get('target') else 'not_applicable', 'candidate_source_links':' | '.join(dict.fromkeys(p['source_url'] for p in ps)),
                        'pre_review_flags':' '.join(flags)})
    write_csv(AUDIT/'v1_question_audit.csv', q_audit)
    # Enumerate true in-corpus text references; do not equate them with relevance.
    cves = [d for d in docs.values() if d['family']=='cve']
    cross = []
    for d in cves:
        for ref in sorted(set(re.findall(r'\bCVE-\d{4}-\d{4,}\b',d['text'],re.I))):
            if ref.casefold() != d['doc_id'] and ref.casefold() in docs:
                cross.append({'doc_id':d['doc_id'],'mentioned_cve':ref.upper(),'source_url':d['source_url'], 'statement':'mention only; human must assess relevance'})
    (AUDIT/'in_corpus_cve_crossrefs.json').write_text(json.dumps(cross,indent=2)+'\n',encoding='utf-8')
    confusables = []
    for q in needs:
        if q['family'] != 'cve': continue
        for d in cves:
            target = q['target'].lower(); other = d['doc_id']
            if target == other or target.split('-')[1] != other.split('-')[1]: continue
            distance = edit_distance(target, other)
            if distance <= 2:
                confusables.append({'need_id':q['need_id'], 'target':target.upper(), 'other':other.upper(),
                                    'edit_distance':distance, 'source_url':d['source_url'],
                                    'already_in_initial_review':any(p['need_id']==q['need_id'] and p['doc_id']==other for p in old_pairs),
                                    'note':'String similarity is not a relevance judgment; source is an actual pinned record.'})
    (AUDIT/'in_corpus_cve_confusables.json').write_text(json.dumps(confusables,indent=2)+'\n',encoding='utf-8')
    summary = {'version':'stage14b-v2','v1_questions_audited':len(q_audit),'v1_pairs_audited':len(pair_audit),
               'v2_questions':len(questions),'v2_pairs':len(pairs),'added_pairs':len(pairs)-len(old_pairs),
               'v1_raw_hash_mismatches':sum(r['raw_sha256_matches']=='false' for r in pair_audit),
               'v1_passage_mismatches':sum(r['passage_matches_corpus']=='false' for r in pair_audit),
               'v1_url_mismatches':sum(r['source_url_matches']=='false' for r in pair_audit),
               'v1_source_extraction_mismatches':sum(r['source_extraction_matches']=='false' for r in pair_audit),
               'v1_provenance_mismatches':sum(r['provenance_fields_match']=='false' for r in pair_audit),
               'in_corpus_crossrefs':len(cross),'same_year_cve_edit_distance_at_most_2':len(confusables),
               'human_reviewed_questions':0,'human_reviewed_pairs':0,
               'note':'Signals are not relevance judgments; coverage is not exhaustive pooling; human review required.'}
    (OUT/'manifest.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__ == '__main__': main()
