# Phase 2 review follow-up

## What was preserved and normalized

The locally submitted v2 workbook remains untouched. Its 273 `Pairs` relevance
labels remain exactly as submitted: 102 `1` labels and 171 `0` labels. A separate
v3 normalized copy expresses the 70 question decisions in the required words:
54 `yes` and 16 `no`. No question decision was changed in meaning, and no pair
label, reviewer identity, timestamp, evidence note, confidence, uncertainty, or
independence declaration was invented.

## Decisions needing human action

The 16 submitted-invalid questions are `natural-03` through `natural-18`. For
each, the reviewer must either supply a corrected validity decision, explicitly
exclude it, or record what source evidence is missing. `natural-13` already has
one submitted positive candidate, but its invalidity still needs an explanation.

Thirty-three questions have no submitted positive candidate: `esp-01` through
`esp-16`, `natural-01` through `natural-12`, and `natural-14` through
`natural-18`. Direct macro lookup in the pinned corpus located 152 additional,
unjudged source candidates for 30 of these needs. Those are review leads only;
they have no assigned relevance labels. No matching candidate was found under
that narrow rule for `natural-08`, `natural-13`, or the hardware question whose
candidate depends on broader context. ESP-08, ESP-11, and ESP-13 require full
source-context review: an absent macro is not evidence that hardware is absent.

The coverage table in the follow-up workbook provides the exact action and
candidate count for every affected need. If a question cannot be supported from
the retained corpus, the reviewer must explicitly exclude or revise it in a new
versioned dataset change; it must not be silently treated as a negative case.

## Required reviewer completion

For each retained pair label, enter a stable pseudonym, a truthful independence
declaration, the actual ISO-UTC review timestamp, confidence, a short
source-specific evidence note, and uncertainty or `none`. Reviewers must also
judge the 152 new candidates as `1`, `0`, or `unknown` and complete the same
fields. The workbook deliberately leaves these cells blank.

## Gate status

The normalized workbook validation is **BLOCKED**. It records 70 question
decisions and 273 pair labels, but 33 needs still lack a reviewed positive and
reviewer provenance/evidence is absent. Structural validity cannot establish
semantic correctness or independence. Stage 15 pooling, development tuning,
configuration freezing, held-out testing, figures, and effectiveness claims
remain prohibited.

The exact outstanding validator items are 1,778 errors and 49 pending items:
343 missing independence attestations, 343 invalid/missing UTC timestamps, 273
missing pair reviewer pseudonyms, 273 missing pair evidence notes, 273 missing
pair confidence values, 273 missing pair uncertainty/adjudication values, 16
question-validity resolutions marked `no`, and 33 needs without an independently
reviewed positive. The script cannot validate that a supplied pseudonym,
declaration, timestamp, or evidence note is truthful; human review must do that.
