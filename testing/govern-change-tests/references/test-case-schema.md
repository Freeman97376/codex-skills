# Governed Test Case Schema

Use one Markdown file per governed test-case version under `office/records/test-cases/<type>/`. Prefer IDs such as `TC-AUTH-001-v1`; keep the filename equal to the lowercase ID.

## Required frontmatter

```yaml
---
test_case_version: 1
id: TC-AREA-001-v1
type: functional
spec_status: draft
execution_status: not_implemented
version: 1
supersedes: none
superseded_by: none
purpose_status: draft
process_status: draft
expected_result_status: draft
confirmed_at: none
confirmed_by: none
source_kind: change-derived
source_ids: none
test_path: none
test_command: none
last_verified_at: none
verified_against: none
coverage_paths: none
contract_ids: none
---
```

Allowed `spec_status` values are `draft`, `derived`, `confirmed`, and `superseded`. Allowed `execution_status` values are `not_implemented`, `not_run`, `passed`, `failed`, `blocked`, and `stale`.

Use project-relative paths. When multiple source IDs, coverage paths, or contracts apply, separate them with semicolons. Use `none` only when a value is genuinely not established.

## Required body

```markdown
# TC-AREA-001-v1 - Short behavior title

## Purpose

Describe the user behavior, contract, or regression risk this case protects and why it matters.

## Preconditions

Describe environment, data, identity, permissions, and setup.

## Process

List reusable actions precisely enough that another agent or person can repeat them.

## Expected result

State observable success and failure criteria. Do not include the actual run result here.

## Actual result

Record the latest real execution result or `Not run`.

## Evidence

Record the exact command, environment, timestamp, verified state, and concise evidence or durable evidence link.

## Confirmation

Summarize the user's confirmation of purpose, process, and expected result without copying the full conversation.

## Notes

Record relevant constraints, waiver links, or conflicts without raw secrets or noisy logs.
```

## Confirmation gate

- `confirmed` requires `purpose_status`, `process_status`, and `expected_result_status` all equal to `confirmed`, plus non-`none` `confirmed_at` and `confirmed_by: user`.
- A confirmed case is an acceptance contract; an agent may propose a replacement but cannot edit the confirmed meaning in place.
- A replacement version sets `supersedes` to the prior ID. The prior record becomes `superseded` and sets `superseded_by` to the new ID.

## Execution evidence

- `passed` requires an existing `test_path`, exact `test_command`, `last_verified_at`, and `verified_against` value.
- `stale` preserves the last verification evidence but signals that related paths or contracts changed afterward.
- `failed` and `blocked` must state the real obstacle in **Actual result** and must not weaken the confirmed expected result.
- Evidence level A means the regression test failed before the fix and passed after it. Level B means credible pre-fix error evidence exists and the post-fix test passed. Level C means coverage is inferred or not yet executed.

## Generated-input evidence (when applicable)

For fuzz or confusing-input cases, add a concise body section (no new required frontmatter) with the target and oracle source; corpus/fixture path and hash; input family and transport; generator version/hash and random seed; case, size, time, and failure budgets; exact execution/replay command; and generated versus executed/passed/failed/skipped/timed-out counts.

For a discovered failure, link the exact original and any reduced reproducer, failure signature, replay result, and deterministic regression test. Keep corpus contents and raw payloads in the project's native test area. Generation alone cannot establish `passed`: use `not_implemented` when no executable test exists, otherwise `not_run`; a generated expectation remains `derived` until the existing confirmation gate is satisfied. Include generator, fixtures, adapter, and relevant target paths in coverage so later changes invalidate evidence.
