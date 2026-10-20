// Run with the bundled artifact-tool runtime; input JSON is generated from review_v2 CSVs.
import fs from 'node:fs/promises';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const data = JSON.parse(await fs.readFile(process.argv[2], 'utf8'));
const output = process.argv[3];
const wb = Workbook.create();
const instructions = wb.worksheets.add('Start');
const questions = wb.worksheets.add('Questions');
const pairs = wb.worksheets.add('Pairs');
for (const sheet of [instructions, questions, pairs]) sheet.showGridLines = false;
const intro = [
 ['PHASE 2 — INDEPENDENT REVIEW', ''],
 ['Version', `stage14b-v2; ${data.questions.length} questions and ${data.pairs.length} candidate pairs.`],
 ['Who', 'A real independent reviewer who did not author the questions or candidate selection.'],
 ['1 — Questions', 'For every row, enter question_valid yes/no/unknown and your ID, independence yes, and UTC timestamp. Put corrections in rewrite_or_notes.'],
 ['2 — Pairs', 'For every row, inspect the passage and its pinned source. Enter 1 if it directly answers the question, 0 if checked and not relevant, or unknown if uncertain.'],
 ['Evidence', 'Enter source-specific evidence or reason, confidence, uncertainty (or none), reviewer ID, independence yes, and UTC timestamp for each pair.'],
 ['Timestamp', 'Enter ISO UTC as text, for example 2026-10-19T12:00:00Z; use the actual review time.'],
 ['Context', 'Open the source URL and check the full file, including preprocessor conditions; the excerpt may omit context.'],
 ['Caution', 'Missing macro does not prove hardware absence. A different CVE title can still contain a relevant cross-reference.'],
 ['Gaps', 'ESP-08, ESP-11 and ESP-13 lack an explicit target macro; assess whether the corpus contains an answer. Conflicting external evidence for ESP-11 needs adjudication.'],
 ['Changes', 'Seven source-conditioned question replacements address old-test topics or missing detail; approve or reject independently.'],
 ['Return', 'Save a completed copy; do not edit IDs, source cells, or question text. Return the workbook and reviewer provenance. Blanks are unjudged.'],
 ['Limit', 'The initial candidate pool is incomplete and contains no rankings or automatic labels. Unknown cases need resolution before evaluation.'],
];
instructions.getRangeByIndexes(0,0,intro.length,2).values=intro;
instructions.getRange('A:A').format.columnWidth=21;
instructions.getRange('B:B').format.columnWidth=105;
instructions.getRange(`A1:B${intro.length}`).format.wrapText=true;
instructions.getRange(`A1:B${intro.length}`).format.rowHeight=34;
instructions.getRange('A1:B1').format.fill='#17365D';
instructions.getRange('A1:B1').format.font.color='#FFFFFF';
instructions.getRange('A1:B1').format.font.bold=true;

const qcols=['need_id','split','query','question_valid','rewrite_or_notes','reviewer_id','independent_of_author','reviewed_at_utc','query_type','family','origin','topic_id'];
const pcols=['review_pair_id','need_id','split','question','human_relevance','ambiguity_or_adjudication','evidence_or_reason','reviewer_id','independent_of_author','reviewed_at_utc','confidence','doc_id','title','passage','source_url','source_revision','source_raw_path','source_sha256','proposed_relevance'];
function populate(sheet, records, cols, height) {
 const values=[cols,...records.map(row=>cols.map(k=>row[k] ?? ''))];
 sheet.getRangeByIndexes(0,0,values.length,cols.length).values=values;
 sheet.getRangeByIndexes(0,0,1,cols.length).format.fill='#17365D';
 sheet.getRangeByIndexes(0,0,1,cols.length).format.font.color='#FFFFFF';
 sheet.getRangeByIndexes(0,0,1,cols.length).format.font.bold=true;
 sheet.getRangeByIndexes(0,0,values.length,cols.length).format.wrapText=true;
 sheet.getRangeByIndexes(0,0,values.length,cols.length).format.rowHeight=height;
 sheet.getRangeByIndexes(0,0,1,cols.length).format.rowHeight=30;
 sheet.getRangeByIndexes(0,0,values.length,cols.length).format.columnWidth=20;
 sheet.freezePanes.freezeRows(1);
}
populate(questions,data.questions,qcols,45);
populate(pairs,data.pairs,pcols,85);
questions.getRange('C:C').format.columnWidth=65;
questions.getRange('D2:H71').format.fill='#FFF2CC';
questions.getRange('D2:D71').dataValidation={rule:{type:'list',values:['yes','no','unknown']}};
pairs.getRange('D:D').format.columnWidth=58;
pairs.getRange(`E2:K${data.pairs.length+1}`).format.fill='#FFF2CC';
pairs.getRange('N:N').format.columnWidth=95;
pairs.getRange('O:O').format.columnWidth=65;
pairs.getRange(`E2:E${data.pairs.length+1}`).dataValidation={rule:{type:'list',values:['1','0','unknown']}};
wb.recalculate();
for (const [name,range] of [['Start','A1:B13'],['Questions','A1:H4'],['Pairs','A1:H4']]) {
 const image=await wb.render({sheetName:name,range,scale:1,format:'png'});
 await fs.writeFile(`${output}.${name}.png`,new Uint8Array(await image.arrayBuffer()));
}
const file=await SpreadsheetFile.exportXlsx(wb); await file.save(output);
console.log((await wb.inspect({kind:'sheet',include:'id,name'})).ndjson);
