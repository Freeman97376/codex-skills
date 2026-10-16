# Repair Plan Template

Use for a multi-error or system-risk repair; a small fix can use a concise subset. This template is a plan, not implementation or publishing authority.

## Baseline, authority, and decisions

Record actual checkout/candidate, affected scope, known constraints, existing authorization, and choices still reserved for human discussion. Preserve unaffected work and historical results.

## Diagnosis and priority

| Error/risk ID | Reproduced / inferred / historically fixed | Confirmed cause or next diagnostic | Impact | Priority and dependency | Linked history/evidence |
|---|---|---|---|---|---|

## Ordered changes

| Step | Behavior and invariant | Proposed implementation and affected paths/contracts | Compatibility/persistence | Material/case/test gate | Relevant skills | Discussion or external authority required |
|---|---|---|---|---|---|---|

For each major step state the smallest useful diagnostic or failing baseline, shared fix, negative and positive controls, completion criteria, and rollback/residual risk. Suspected risks begin with a bounded diagnostic; do not preselect a large refactor as the diagnosis.

## Discussion items

Give a recommended behavior and concrete alternatives/tradeoffs for each unresolved detail. Reference stable IDs so replies update the plan. Treat answers as behavior alignment; do not silently promote all derived tests to confirmed golds or infer paid/production/reviewer authority.

## Validation, history, and release

Specify focused tests, document replay, browser flow, broader required checks, and evidence-freshness renewal. Record provider/time budgets and stopping conditions for proposed external work. Link summary/history/ledger updates.

Independent review and release-preflight are conditional phases when explicitly requested; keep exact review settings and concrete release approval separate. Define candidate CI, production preflight, backup/rollback and post-release manual checks only when relevant. Do not equate a local pass or skill installation with live acceptance.
