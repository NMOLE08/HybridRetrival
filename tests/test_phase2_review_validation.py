"""Review validation tests use synthetic fixtures, never research judgments."""
import importlib.util
from pathlib import Path

SPEC = importlib.util.spec_from_file_location('phase2_review_validator', Path('scripts/validate_phase2_human_review.py'))
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)

def fixtures():
    q = {'need_id':'q1','split':'dev','query':'What is the demo feature?', 'query_type':'identifier',
         'family':'esp32','origin':'fixture','topic_id':'demo','question_valid':'','reviewer_id':'',
         'independent_of_author':'','reviewed_at_utc':'','rewrite_or_notes':''}
    p = {'review_pair_id':'p1','need_id':'q1','split':'dev','question':q['query'],'doc_id':'d1',
         'title':'title','passage':'source text','source_url':'https://example.org/source',
         'source_revision':'abc','source_raw_path':'source.txt','source_sha256':'123',
         'human_relevance':'','reviewer_id':'','independent_of_author':'','reviewed_at_utc':'',
         'confidence':'','evidence_or_reason':'','ambiguity_or_adjudication':''}
    return q,p

def test_blank_review_is_blocked_and_no_positive_is_invented():
    q,p=fixtures(); r=validator.validate([q],[p],[q.copy()],[p.copy()],[])
    assert r['status']=='BLOCKED'
    assert r['reviewed_questions']==r['reviewed_pairs']==0
    assert r['questions_without_reviewed_positive']==1

def test_judgment_requires_metadata_and_preserved_source():
    q,p=fixtures(); q0=q.copy(); p0=p.copy()
    q.update(question_valid='yes', reviewer_id='human',independent_of_author='yes',reviewed_at_utc='2026-10-19T12:00:00Z')
    p.update(human_relevance='1', reviewer_id='human',independent_of_author='yes',reviewed_at_utc='2026-10-19T12:00:00Z',
             confidence='high',evidence_or_reason='source supports the fixture',ambiguity_or_adjudication='none')
    assert validator.validate([q],[p],[q0],[p0],[])['status']=='READY_FOR_MANUAL_GATE_REVIEW'
    p['source_url']='https://example.org/changed'
    p['reviewed_at_utc']='2026-10-19'
    result=validator.validate([q],[p],[q0],[p0],[])
    assert result['status']=='BLOCKED'
    assert any('immutable' in e for e in result['errors'])
    assert any('timestamp' in e for e in result['errors'])

def test_unknown_is_not_a_negative_or_positive():
    q,p=fixtures(); q0=q.copy(); p0=p.copy()
    p.update(human_relevance='unknown',reviewer_id='human',independent_of_author='yes',
             reviewed_at_utc='2026-10-19T12:00:00Z',confidence='low',evidence_or_reason='insufficient',ambiguity_or_adjudication='unresolved')
    result=validator.validate([q],[p],[q0],[p0],[])
    assert result['questions_without_reviewed_positive']==1
    assert any('unresolved unknown' in x for x in result['pending'])
