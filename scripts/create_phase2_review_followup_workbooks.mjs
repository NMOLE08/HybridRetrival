// Create derived Phase 2 review workbooks.  The submitted workbook is never modified.
import fs from 'node:fs/promises';
import { FileBlob, Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const [submittedPath, inputPath, normalizedPath, followupPath] = process.argv.slice(2);
const input = JSON.parse(await fs.readFile(inputPath, 'utf8'));

const submitted = await FileBlob.load(submittedPath);
const normalized = await SpreadsheetFile.importXlsx(submitted);
const qSheet = normalized.worksheets.getItem('Questions');
const qRange = qSheet.getRange(`D2:D${input.questions.length + 1}`);
qRange.values = input.questions.map((q) => {
  const raw = String(q.question_valid ?? '').trim().toLowerCase();
  return [raw === '1' ? 'yes' : raw === '0' ? 'no' : raw];
});
const normalizedFile = await SpreadsheetFile.exportXlsx(normalized);
await normalizedFile.save(normalizedPath);

const wb = Workbook.create();
const start = wb.worksheets.add('Start here');
const questionFollowup = wb.worksheets.add('Question follow-up');
const pairEvidence = wb.worksheets.add('Pair evidence');
const coverage = wb.worksheets.add('Coverage candidates');
const actions = wb.worksheets.add('Coverage required');
for (const sheet of [start, questionFollowup, pairEvidence, coverage, actions]) sheet.showGridLines = false;

const startRows = [
  ['PHASE 2 — REVIEW FOLLOW-UP', ''],
  ['Version', 'stage15-followup-v1. Derived from the submitted workbook; original workbook and its labels are preserved.'],
  ['Purpose', 'Finish metadata and evidence only. Existing labels are shown as submitted and are not changed here.'],
  ['Reviewer pseudonym', 'Enter the same pseudonym in each reviewed row. Do not use a fabricated identity.'],
  ['Independence', 'Enter yes only if you independently reviewed the item and did not author the question or candidate selection.'],
  ['Timestamp', 'Enter the actual review time in ISO UTC, for example 2026-10-21T14:30:00Z.'],
  ['Confidence', 'Choose high, medium, or low.'],
  ['Evidence note', 'Give a short source-specific reason. Use uncertainty for unresolved ambiguity; do not convert it to a negative label.'],
  ['Question follow-up', 'Resolve all 16 submitted no validity decisions: correct the decision, explicitly exclude the question, or explain needed source evidence.'],
  ['Pair evidence', 'Add evidence and reviewer metadata for each existing submitted label. The relevance label is reference-only here.'],
  ['Coverage candidates', 'Review only the new, unjudged existing-corpus candidates. Blank relevance means unjudged.'],
  ['Coverage required', 'Shows all 33 questions without a submitted positive and the action needed to close each coverage gap.'],
  ['Caution', 'Missing a macro does not establish absent hardware. ESP-08, ESP-11, and ESP-13 require source-context review.'],
];
start.getRangeByIndexes(0, 0, startRows.length, 2).values = startRows;
start.getRange(`A1:B${startRows.length}`).format.wrapText = true;
start.getRange(`A1:B${startRows.length}`).format.rowHeight = 34;
start.getRange('A:A').format.columnWidth = 23;
start.getRange('B:B').format.columnWidth = 110;
start.getRange('A1:B1').format.fill = '#17365D';
start.getRange('A1:B1').format.font.color = '#FFFFFF';
start.getRange('A1:B1').format.font.bold = true;

function table(sheet, columns, records, rowHeight = 50) {
  const values = [columns, ...records.map((r) => columns.map((c) => r[c] ?? ''))];
  sheet.getRangeByIndexes(0, 0, values.length, columns.length).values = values;
  const all = sheet.getRangeByIndexes(0, 0, values.length, columns.length);
  all.format.wrapText = true;
  all.format.rowHeight = rowHeight;
  all.format.columnWidth = 20;
  sheet.getRangeByIndexes(0, 0, 1, columns.length).format.fill = '#17365D';
  sheet.getRangeByIndexes(0, 0, 1, columns.length).format.font.color = '#FFFFFF';
  sheet.getRangeByIndexes(0, 0, 1, columns.length).format.font.bold = true;
  sheet.getRangeByIndexes(0, 0, 1, columns.length).format.rowHeight = 30;
  sheet.freezePanes.freezeRows(1);
}
function editable(sheet, range) { sheet.getRange(range).format.fill = '#FFF2CC'; }
function list(sheet, range, values) { sheet.getRange(range).dataValidation = { rule: { type: 'list', values } }; }

const invalid = input.questions.filter((q) => ['0', 'no'].includes(String(q.question_valid).trim().toLowerCase()));
const qColumns = ['need_id', 'split', 'query', 'submitted_question_valid', 'required_action', 'corrected_question_valid', 'correction_or_exclusion_reason', 'reviewer_pseudonym', 'independent_of_author', 'actual_reviewed_at_utc', 'confidence', 'evidence_note', 'uncertainty'];
const requirementByNeed = Object.fromEntries(input.requirements.map((r) => [r.need_id, r]));
const qRecords = invalid.map((q) => ({
  need_id: q.need_id, split: q.split, query: q.query, submitted_question_valid: q.question_valid,
  required_action: requirementByNeed[q.need_id]?.required_action ?? '', corrected_question_valid: '', correction_or_exclusion_reason: '', reviewer_pseudonym: '', independent_of_author: '', actual_reviewed_at_utc: '', confidence: '', evidence_note: '', uncertainty: '',
}));
table(questionFollowup, qColumns, qRecords, 62);
questionFollowup.getRange('C:C').format.columnWidth = 58;
questionFollowup.getRange('E:E').format.columnWidth = 68;
for (const col of ['F', 'G', 'H', 'I', 'J', 'K', 'L', 'M']) editable(questionFollowup, `${col}2:${col}${qRecords.length + 1}`);
list(questionFollowup, `F2:F${qRecords.length + 1}`, ['yes', 'no', 'unknown', 'exclude']);
list(questionFollowup, `I2:I${qRecords.length + 1}`, ['yes', 'no']);
list(questionFollowup, `K2:K${qRecords.length + 1}`, ['high', 'medium', 'low']);

const pColumns = ['review_pair_id', 'need_id', 'split', 'question', 'doc_id', 'title', 'source_url', 'submitted_relevance', 'reviewer_pseudonym', 'independent_of_author', 'actual_reviewed_at_utc', 'confidence', 'evidence_note', 'uncertainty'];
const pRecords = input.pairs.map((p) => ({
  review_pair_id: p.review_pair_id, need_id: p.need_id, split: p.split, question: p.question, doc_id: p.doc_id, title: p.title, source_url: p.source_url, submitted_relevance: p.human_relevance,
  reviewer_pseudonym: '', independent_of_author: '', actual_reviewed_at_utc: '', confidence: '', evidence_note: '', uncertainty: '',
}));
table(pairEvidence, pColumns, pRecords, 62);
pairEvidence.getRange('D:D').format.columnWidth = 55;
pairEvidence.getRange('F:F').format.columnWidth = 45;
pairEvidence.getRange('G:G').format.columnWidth = 60;
for (const col of ['I', 'J', 'K', 'L', 'M', 'N']) editable(pairEvidence, `${col}2:${col}${pRecords.length + 1}`);
list(pairEvidence, `J2:J${pRecords.length + 1}`, ['yes', 'no']);
list(pairEvidence, `L2:L${pRecords.length + 1}`, ['high', 'medium', 'low']);

const cColumns = ['review_pair_id', 'need_id', 'split', 'question', 'doc_id', 'title', 'passage', 'source_url', 'candidate_basis', 'human_relevance', 'reviewer_pseudonym', 'independent_of_author', 'actual_reviewed_at_utc', 'confidence', 'evidence_note', 'uncertainty'];
const cRecords = input.additional.map((p) => ({
  ...p, reviewer_pseudonym: '', independent_of_author: '', actual_reviewed_at_utc: '', confidence: '', evidence_note: '', uncertainty: '',
}));
table(coverage, cColumns, cRecords, 82);
coverage.getRange('D:D').format.columnWidth = 54;
coverage.getRange('F:F').format.columnWidth = 42;
coverage.getRange('G:G').format.columnWidth = 90;
coverage.getRange('H:H').format.columnWidth = 58;
coverage.getRange('I:I').format.columnWidth = 42;
for (const col of ['J', 'K', 'L', 'M', 'N', 'O', 'P']) editable(coverage, `${col}2:${col}${cRecords.length + 1}`);
list(coverage, `J2:J${cRecords.length + 1}`, ['1', '0', 'unknown']);
list(coverage, `L2:L${cRecords.length + 1}`, ['yes', 'no']);
list(coverage, `N2:N${cRecords.length + 1}`, ['high', 'medium', 'low']);

const aColumns = ['need_id', 'split', 'question', 'submitted_question_decision', 'submitted_positive_count', 'expected_macro', 'additional_unjudged_candidates', 'required_action'];
table(actions, aColumns, input.requirements, 62);
actions.getRange('C:C').format.columnWidth = 60;
actions.getRange('H:H').format.columnWidth = 88;

wb.recalculate();
for (const [name, range] of [['Start here', 'A1:B13'], ['Question follow-up', 'A1:M5'], ['Coverage candidates', 'A1:P4']]) {
  const image = await wb.render({ sheetName: name, range, scale: 1, format: 'png' });
  await fs.writeFile(`${followupPath}.${name.replaceAll(' ', '_')}.png`, new Uint8Array(await image.arrayBuffer()));
}
const file = await SpreadsheetFile.exportXlsx(wb);
await file.save(followupPath);
console.log(JSON.stringify({ normalizedPath, followupPath, invalidQuestions: qRecords.length, existingPairs: pRecords.length, unjudgedCandidates: cRecords.length }));
