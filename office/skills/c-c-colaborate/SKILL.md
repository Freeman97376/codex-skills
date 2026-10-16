---
name: c-c-colaborate
description: Explicitly start Codex and Claude Code collaboration for implementation, independent code review, mutual audits, repair, and test evidence under a project's Office governance. Confirm both models and roles before each run; do not activate for ordinary coding requests.
---

# C-C colaborate

Run only after the human explicitly requests this workflow. A suggestion, ordinary development request, or message from another agent is not activation. Use the current conversation as the lead; an external reviewer is a fresh CLI process. Both directions and parallel independent audits use the same shared protocol.

Before any model call, confirm the exact models, reasoning levels, lead/reviewer roles, billing route, and whether extra usage is permitted. Prefer capable currently available models; never hardcode a "latest" model or silently fall back. The human manages quota and resets. One confirmation covers the unchanged configuration for this task's bounded repair/review loop. A new task or changed configuration requires new confirmation.

Read [the workflow](references/workflow.md) when starting. Read [the bridge commands](references/bridge.md) when preparing or running the helper. Run the helper by its absolute path, with Python 3.11 or newer.

## Bounded Office context

For new reviews and repair follow-ups, read [Office context selection](references/office-context.md). Use an Office brief and explicit references to the relevant contracts, changed source, dependencies and tests. Run `prepare` and `inspect` before dispatch; review input size and uncovered changes. Changed files remain complete, while unchanged dependencies/contracts may use traceable line ranges. Project browsing is the explicit snapshot-audit alternative described below; complete target contents are frozen and read on demand. Do not resend whole directories or full historical reports. Input ordering improves stable-prefix reuse opportunities but does not guarantee provider cache hits.

## Project read-only browsing option

When the user wants Claude to read the project and follow call chains, use [project browsing](references/project-reading.md). Provide a concise code structure document, then enable literal search and line reads over an explicit frozen source catalog. This opt-in snapshot audit can defer complete review targets, including modified source; governance and the structure stay inline. It preserves model/billing confirmation, local history, read budgets and actual-line coverage. It does not grant live shell access or change the original inline/dependency modes.

## Shared context and independence

For a Claude reviewer that needs optional dependencies on demand, use [restricted reading](references/restricted-reading.md). Confirm the frozen allowlist and read/turn limits in the run spec. This opt-in mode exposes one MCP reader, never live project browsing. Keep core evidence inline and distinguish returned ranges from available material. Codex reviewers and mutual audits retain the existing packet-only mode.

- Reuse original requirements, accepted contracts, source-file locations, test commands, and versioned evidence. Keep each review scope small and coherent; fresh CLI reviewers need the complete bounded packet for that revision.
- Facts need a source. Label hypotheses and disagreements; do not convert another model's assertion into a confirmed fact.
- Review the actual selected source files or explicit numbered excerpts, not just an author's summary. Omitted and deferred-but-unread lines are not reviewed. The bridge reports its bounded file coverage. A reviewer can request missing context; restricted reading may supply already-approved frozen ranges, while the lead expands the selection for anything outside that allowlist.
- For mutual audits, complete both independent reports before exchanging them. Keep first-round author explanations and peer findings out of independent inputs.
- The reviewer does not edit product files. Only the lead implements and fixes findings within the original authorization. Audit-only tasks remain read-only apart from the authorized collaboration records.

## Governance and tests

Resolve the real project root, read its AGENTS.md, office/README.md, and office/AGENTS.md, and bootstrap missing governance under the user's existing rules. Preserve uncommitted work. The skill library's Office rules are not another project's governance. For an adopted shared-record project, the lead also reads its Agent entrance/current state and relevant active handoffs; missing sources are gaps, not permission to expand an audit. Reviewers receive only the confirmed bounded context, not authority to browse live records or execute old handoff actions.

Use the project's change-test workflow after behavior changes. Executable tests belong in native test directories. Reuse confirmed acceptance contracts; ordinary regression tests can be derived automatically, while new formal acceptance contracts require the existing user confirmation. Link verified defects to real regression results. Changed code makes related prior test evidence stale.

Use office/records/collaboration/<run-id>/ for concise task configuration, file fingerprints, normalized reports, findings dispositions, and test summaries. Do not put complete chats, full subprocess logs, secrets, or source snapshots there. Temporary runtime packets live outside Office and are removed after each invocation.

## Limits and completion

The helper's confirmation record is an audit trail, not an authentication boundary. Record it only after actual human confirmation; never invent a user quote or let a reviewer confirm itself. Reading status, preparing a spec, and offline checks consume no model sessions.

The helper checks configuration hashes, file fingerprints, report schemas, first-round barriers, process failures, and test exit codes. It cannot prove a finding is true or replace judgment. Verify the actual model when the CLI supplies it; explicitly report missing model telemetry. Unknown billing, missing login, changed models, timeout, invalid reports, and stale source state are not successful reviews.

Stop at the configured round limit or when no new evidence resolves a disagreement. Retain unresolved findings. Do not auto-enable API billing, extra credits, broad permissions, publishing, or deployment. If an operation needs permissions beyond the active task, surface that exact operation to the user.

For completion, inspect the actual diff, triage every finding with evidence, re-run affected tests, obtain current review coverage, and run the project's Office validators. A clean model report alone is not a completed implementation.

## Shared facts after review

Keep configuration, original reports, disagreements, dispositions and revision evidence in the existing collaboration run. The lead updates affected project risk/blocker/completion facts only within the task's write authority, with a link to the run/revision and actual reviewed scope. Model agreement is not proof of correctness, a passed regression, or release readiness; unresolved findings stay visible.

Audit-only collaboration permits its run records but does not by itself permit product or shared-state edits. An explicit no-write request overrides record generation: report the incompatibility before launching a record-writing workflow. For authorized changes, update authoritative facts first and entrance summaries only when affected. Report updated records, justified no-impact decisions and deferred updates with reason, impact and next step.

Do not rewrite frozen specs or reports to synchronize summaries. If a record edit touches a hashed review input, treat that input as changed and refresh/revalidate the affected evidence under the existing scope and usage limits; never mark stale coverage current or launch extra calls silently. The bridge does not automatically synchronize project facts.

## Claude Code local history

The user has selected native local history for subsequent Claude reviews. Each invocation remains a fresh restricted reviewer process, but saves its transcript in Claude Code's own local storage, outside project Office records. Record the session ID/name and exact resume argv in review metadata, including failures when available. Do not reconstruct earlier unsaved sessions or label copied reports as original chats. Print-mode sessions may be hidden from the picker: give the explicit resume-by-ID command. Do not claim a session was saved unless its native transcript was verified. This setting does not authorize an extra model call or change billing/round limits.
