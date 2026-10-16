---
name: manage-agent-governance
description: Initialize, audit, repair, or evolve a project's agent-governance system. Use when creating or adopting a project, changing AGENTS.md, or working with office/ skills, scripts, records, handoffs, governance tests, or agent interaction rules.
---

# Manage Agent Governance

Keep the project's agent-facing rules discoverable, minimal, auditable, and safe to reuse.

## Workflow and Authority

1. Resolve the actual project root with `git rev-parse --show-toplevel` for a Git checkout, otherwise the user-selected directory. A mismatch must be reported; do not silently expand scope. The initializer requires an explicit root and rejects linked paths and filesystem roots.
2. Read root `AGENTS.md`, `office/README.md`, `office/AGENTS.md`, the agent record entrance and current state, then task-relevant sources and working changes. Preserve stricter rules and user work; report missing/stale facts without expanding a read-only task.
3. Select the authorized mode before any side effects:
   - **Read-only audit:** read and report functionality, gaps, references and proposed changes. No initialization, repairs, records, self-tests, installation or publication. Run a structural validator only if checks are authorized; otherwise inspect statically. The initializer's `-Plan` is a read-only inventory, not a validator or a test.
   - **Initialize:** preview the trusted [initializer](../../scripts/Initialize-Office.ps1) with explicit `-ProjectRoot` and `-Plan`. Copy only the exact [bootstrap manifest](../../templates/bootstrap-manifest.psd1) files when initialization is authorized. Use generic templates, not the source project's live policies. Existing differing governance files block all writes; merge them under the upgrade workflow. Existing records are always preserved. `-Force` is rejected.
   - **Repair or upgrade:** follow [maintenance boundaries](references/maintenance.md). Show affected paths, source/target differences, policy impact and migration plan before applying an authorized merge. Existing in-scope implementation authorization remains valid; do not ask again unnecessarily. Initialization is not a version upgrade.
4. After authorized edits, run the [structural validator](../../scripts/Test-OfficeGovernance.ps1), then the [isolated self-tests](../../tests/Test-OfficeGovernance.ps1) for changes to scripts, templates, skills or tests. Respect explicit user limits on execution.
5. For record maintenance, follow [dual-entry records](references/records.md): human and agent entrances share canonical facts and evidence. For authorized adoption or upgrades, wire the startup/completion obligations into the target project contract and local skill; source/template updates alone do not upgrade existing projects. Before completion, map the actual diff to affected records, update authoritative facts first, and report updated records, justified no-impact decisions and deferred items. Only when writing is authorized, append durable decisions or substantial task evidence. Preserve existing architecture and test authorities; do not bulk-migrate history or log routine questions, full transcripts, duplicate raw logs, secrets or private connection details.
6. Report what changed, actual validation results, preserved differences, pending dependencies and skipped checks. Structure and fixture tests do not establish product correctness, live cross-model success or release readiness.

## Responsibility Boundaries

- This skill owns the governance foundation for one selected project, not global installation or changes to every project.
- Never recursively copy office/. Exclude project-specific skills, `.local`, connection profiles and credential references, demos, build artifacts, caches and runtime evidence from bootstrap.
- Delegate behavior-change testing to govern-change-tests, incremental alignment to piecewise-alignment, release gates to release-preflight and optional model collaboration to c-c-colaborate. Preserve each workflow's own trigger and authorization rules; report missing dependencies instead of auto-installing or activating them.
- Updating the maintained source does not authorize synchronizing `.publish`, committing, pushing or deploying. Publication requires its own scope and the package checks in the maintenance reference.

## Change Rules

- Merge existing instructions; do not weaken or silently discard them.
- Use exact `AGENTS.md` casing for Codex discovery. Treat `Agent.md` or `agent.md` as a migration input, not a second source of truth.
- Keep skill frontmatter limited to `name` and `description`.
- Prefer deterministic scripts for repeatable checks and concise Markdown for policy.
- Keep generated outputs, temporary test projects, and secrets out of `office/records/`.
- Require explicit user authorization before external writes, destructive operations, publishing, or credential use.
