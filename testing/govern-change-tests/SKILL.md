---
name: govern-change-tests
description: Analyze behavior changes and known errors, generate reusable project-native tests including malformed, confusing, and fuzz inputs, and maintain Office test evidence. Use after implementation, bug fixes, contract changes, or explicit testing and robustness requests; remain read-only for review or diagnosis without edit authorization.
---

# Govern Change Tests

Turn changed behavior and known failures into reusable tests with an auditable distinction between proposed coverage, user-confirmed acceptance contracts, and actual execution evidence.

## Trigger and Authority

- Run a test-impact analysis after authorized work changes functional behavior, fixes a known error, or changes an API, schema, permission, migration, or fixed business contract. Also run when the user explicitly requests testing or validation.
- Skip automatic analysis for documentation, comments, formatting, or other changes confirmed not to affect runtime behavior.
- Match the current task authority. During implementation, creating and running relevant project-local tests is in scope. During review, explanation, or diagnosis, remain read-only and report test gaps without creating files.
- Ask before paid-network calls, production data, external accounts, destructive environments, publishing, or any other action requiring additional authority.

## Establish the Test Impact

1. Resolve the real project root and read the applicable `AGENTS.md`, `office/README.md`, and `office/AGENTS.md` rules.
2. Inspect the actual diff, error evidence, affected contracts, existing test frameworks, fixtures, commands, and working-tree state. Preserve user changes and do not reset or overwrite them.
3. Map each material change or known error to its observable behavior, affected paths or contracts, regression risk, existing coverage, and smallest useful test level.
4. Separate confirmed repository facts from inferred risk. Do not invent a reproduced failure, a passing result, or user confirmation.

## Choose the Test Class

- Create **derived tests** for ordinary branches, boundaries, transformations, and low-risk regression coverage. They may be generated and executed within implementation authority, but they remain `draft` or `derived` and are not a formal acceptance baseline.
- Propose a **canonical test case** for core user journeys, fixed contracts, security or permission boundaries, data integrity, migrations, or important repeated errors. Discuss its purpose, process, and expected result with the user. Promote it to `confirmed` only after all three are explicitly confirmed.
- Keep expected and actual results separate. User confirmation defines the expected contract; only real execution can establish `passed`, `failed`, or `blocked`.
- Version confirmed cases instead of overwriting them. A replacement must identify the prior version; retain the prior file as `superseded` with a reverse link.

Read [references/test-case-schema.md](references/test-case-schema.md) when creating or changing governed test-case records.

## Generate Reusable Tests

- Use the project's existing test framework, directory conventions, fixtures, factories, mocks, and commands. Put executable product tests in the project's normal test locations, never under `office/`.
- Test observable behavior and contracts rather than copying implementation details. Prefer extending an existing suite over creating a parallel harness.
- For a known error, prefer evidence that the test failed before the fix and passes after it. If pre-fix execution is unavailable, state the lower evidence level instead of fabricating it.
- Run the smallest relevant test first, then expand to module, integration, or broader validation only when risk warrants it. Report the exact command, pass criteria, actual outcome, and skipped checks.

## Generate Robustness and Confusing Inputs

- When requested, or when changed input handling has a concrete risk, cover relevant malformed, boundary, Unicode/confusable, noisy, and domain-specific ambiguous inputs. During read-only review, propose coverage only.
- Read [references/robustness-testing.md](references/robustness-testing.md) before generating or running these cases. It defines contract-based assertions, deterministic generation, bounded execution, and failure replay/reduction.
- Prefer the existing project-native fuzz/property-based framework. The bundled [scripts/generate_input_cases.py](scripts/generate_input_cases.py) can generate a bounded, reproducible corpus from synthetic JSON seeds without dependencies or target execution.
- Keep a valid baseline, preserve exact failing inputs, and turn reproduced failures into deterministic regression tests. Generated cases remain derived; generation alone cannot establish a passing test or confirmed acceptance contract.

## Govern Known Errors

- Maintain the known-error lifecycle without treating a plausible fix as verification.
- Mark an error `verified` only when a linked regression test passes against the fixed state, or when automation is genuinely infeasible and the user explicitly approves a documented manual-test waiver.
- Do not close an error merely because the symptom disappeared once. Keep root-cause certainty distinct from reproduction and verification evidence.

Read [references/known-error-lifecycle.md](references/known-error-lifecycle.md) when creating, updating, verifying, waiving, or superseding a known-error record.

## Persist and Invalidate Evidence

- Use `office/records/test-ledger.md` as the index. Store canonical cases under `office/records/test-cases/<type>/` and known errors under `office/records/known-errors/`; create those folders only when first needed.
- Store concise governance evidence, not full transcripts, secrets, credentials, or noisy raw logs. Link to project test files or durable CI evidence when available.
- Track specification state separately from execution state. Supported execution states are `not_implemented`, `not_run`, `passed`, `failed`, `blocked`, and `stale`.
- Record the verified commit or working-tree fingerprint plus covered paths and contract identifiers. When later changes intersect those paths or contracts, change `passed` to `stale`; restore `passed` only after re-execution succeeds.
- A known error whose regression evidence is stale must not be described as verified for the current code state.

## Validate and Handoff

- Run the project-native tests that are proportionate to the change, then run `office/scripts/Test-ChangeTestGovernance.ps1` when the project has adopted the Office testing baseline.
- Update `office/records/task-log.md` only for substantial test work. Keep detailed case and error evidence in their dedicated records.
- Finish with changed or proposed tests, purpose, command, actual result, evidence level, stale or missing coverage, waivers, and the next concrete action.
- Never claim a test passed unless its command completed successfully in the stated environment.
