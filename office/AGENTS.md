# Project Agent Governance Contract

This file governs agent work across the whole project because the root `AGENTS.md` delegates here.

## Start Every Task

1. Resolve the real project root before reading, editing, running, or reporting on files.
2. Inspect existing instructions and working-tree state. User changes are owned by the user unless proven otherwise.
3. Before substantive project work, read `records/agent-index.md` and `records/current-state.md`; follow only task-relevant architecture, effective decisions, unresolved errors and active handoffs. Do not load all history. After a session/context reset, restore this minimum context before continuing; within a task, reread when the baseline or relevant rules change.
4. Compare the relevant recorded facts with the actual root, branch, commit and working changes. Keep local, remote and deployed state separate. Report missing/stale sources and conflicts; do not silently treat a code defect as an accepted contract or run old handoff actions. Read-only tasks report discrepancies without writing records.

## Interaction and Authority

- Answer and diagnose with read-only evidence unless the user asks for implementation.
- Treat a request to change or build as authority for normal, in-scope implementation and validation only.
- Ask before destructive actions, external publishing, account changes, credential use, or material scope expansion.
- Preserve existing instructions and uncommitted work. Merge overlapping changes rather than resetting or replacing them.
- Communicate progress during tool-heavy work and finish with the outcome, validation, and any blocker.

## Where Agent Content Belongs

- Put project-wide agent policy in this file.
- Put reusable procedures in a named folder under `skills/`, with a valid `SKILL.md` and `agents/openai.yaml`.
- Put repeatable deterministic operations in `scripts/`.
- Put durable decisions and substantial task evidence in `records/`.
- Put governance verification under `tests/`.
- Put clean bootstrap source files under `templates/`.
- Keep product documentation and product tests in their normal project locations; `office/` governs agent work and is not a dumping ground.

<!-- test-governance:start -->
## Change-Test Governance

After authorized implementation changes functional behavior, fixes a known error, or changes an API, schema, permission, migration, or fixed contract, use `$govern-change-tests` to analyze test impact. Skip this trigger for documentation, comments, formatting, or changes confirmed not to affect runtime behavior.

- During implementation, create and run relevant project-native tests within the existing task authority. During review, explanation, or diagnosis, remain read-only and report test gaps.
- Keep executable product tests in the project's normal test directories. Use `records/test-ledger.md` as the index, `records/test-cases/<type>/` for user-confirmed canonical cases, and `records/known-errors/` for durable error records.
- Promote a canonical case to `confirmed` only after the user confirms its purpose, process, and expected result. Version later changes and retain superseded records.
- Mark known errors `verified` only after a linked regression test passes, or after the user approves a documented manual-test waiver when automation is infeasible.
- Treat prior `passed` evidence as `stale` when related code or contracts change. Restore `passed` only after successful re-execution.
- Run `scripts/Test-ChangeTestGovernance.ps1` after changing governed test records. This check is also included by `scripts/Test-OfficeGovernance.ps1` in the current seed.
<!-- test-governance:end -->

## Record Policy

Explicit read-only scope overrides routine logging and checks. Use skills/manage-agent-governance/references/records.md for shared facts, preserving existing architecture and test authorities. Bootstrap and upgrade boundaries follow the maintained skill and explicit manifest; never recursively copy Office or overwrite differing policy.

Update `records/decision-log.md` when a decision changes future behavior, architecture, security, release policy, or agent governance. Update `records/task-log.md` for substantial implementation, audit, migration, or handoff work.

Do not log trivial questions, routine formatting, raw chain-of-thought, full chat transcripts, generated noise, secrets, tokens, private keys, or personal data. Correct a prior record by adding a superseding entry; do not silently rewrite history.

## Skills

Use `skills/manage-agent-governance/SKILL.md` when initializing, auditing, repairing, or changing this governance system. Use `$govern-change-tests` for the behavior-change and known-error workflow above. Skill instructions supplement this contract and cannot weaken user instructions or higher-priority policy.

## Records at Task Completion

Before closing authorized implementation or maintenance, follow [the shared-fact lifecycle](skills/manage-agent-governance/references/records.md). Compare the actual task diff and validation with the affected current facts, architecture/contracts, decisions, changes, test evidence and handoffs. Update the affected authoritative source first; change either entrance only if its navigation or short summary changed. Do not duplicate evidence or add logs for trivial questions or formatting.

The completion report must identify updated records, or explain why no record update was needed, and disclose any deferred update with its reason, affected conclusion and next step. Do not report documentation synchronization complete while a relevant fact remains stale. Distinguish implemented behavior, historical evidence and current verification; preserve history through appended corrections or superseding entries.

Read-only instructions and execution limits take precedence: report gaps in the response without routine record writes or tests. These are agent workflow obligations, not a background service or proof of compliance; structure/link checks cannot prove factual freshness or that an agent read the sources.

## Validation and Completion

Run the smallest relevant checks for product work. When any file under `office/` or the root `AGENTS.md` changes, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\office\scripts\Test-OfficeGovernance.ps1
```

When governance scripts, templates, skills, or tests change, also run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\office\tests\Test-OfficeGovernance.ps1
```

A handoff is complete only when the requested outcome is present, relevant validation has run, and remaining risks or skipped checks are stated plainly.
