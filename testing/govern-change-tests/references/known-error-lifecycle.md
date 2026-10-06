# Known Error Lifecycle

Store one Markdown record per durable error under `office/records/known-errors/`. Prefer IDs such as `ERR-AUTH-001` and keep raw logs outside governance records.

## Required frontmatter

```yaml
---
known_error_version: 1
id: ERR-AREA-001
status: open
severity: medium
reported_at: 2026-08-28T12:00:00-07:00
resolved_at: none
root_cause_status: unknown
regression_test_case: none
regression_test_path: none
regression_test_command: none
last_verified_at: none
verified_against: none
waiver_status: none
waiver_confirmed_at: none
superseded_by: none
---
```

Allowed status flow:

```text
open -> reproduced -> regression_draft -> fixed_unverified -> verified
```

Use `superseded` only when another record replaces the error. Use `waiver_status: user-approved` only when automated regression testing is genuinely infeasible and the user confirms the documented manual alternative.

## Required body

```markdown
# ERR-AREA-001 - Short symptom

## Symptom

Describe the concise user-visible or contract-level failure.

## Trigger

Describe reproducible inputs, state, environment, and actions.

## Evidence

Record concise evidence and whether reproduction is confirmed. Do not store secrets or full noisy logs.

## Expected behavior

State the corrected observable contract.

## Root cause

Separate confirmed cause from inference.

## Resolution

Describe the fix or current mitigation and affected paths.

## Verification

Link the regression test case and executable test path, command, verified state, timestamp, and evidence level.

## Manual verification

When a waiver is approved, record repeatable manual steps, expected result, residual risk, confirmation time, and review condition. Otherwise write `Not applicable`.

## Notes

Record related contracts, cases, or superseding records.
```

## Verification gate

- `verified` requires a linked regression case, existing test path, exact command, timestamp, and verified state whose test execution is `passed`.
- If automation is infeasible, `verified` instead requires `waiver_status: user-approved`, `waiver_confirmed_at`, and substantive **Manual verification** content.
- A one-time disappearance of the symptom, an unexecuted test, or stale regression evidence cannot establish `verified`.
- When the linked regression case becomes `stale`, describe the error as previously verified but not verified for the current state until the test passes again.

## Generated-input failures

When an error comes from fuzz or confusing-input testing, **Trigger** must link the exact synthetic failing fixture, its transport/encoding, case ID, seed, generator version/hash, and replay command. In **Evidence**, distinguish the first observation from independent replay and from any later reduction. Keep original and reduced reproducers separately; accept a reduction only after the same oracle reproduces the same failure signature. **Verification** must link a deterministic regression replay of the retained fixture. Generating a corpus, or having a new random batch miss the failure, does not verify the error.
