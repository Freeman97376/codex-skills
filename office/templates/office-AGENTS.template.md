# Project Agent Governance Contract

## Scope and authority

Resolve the user-selected project root, read existing rules and inspect working
changes. Preserve stricter rules and user work. Do not expand to other projects.
Before substantive work or after a session/context reset, read records/agent-index.md
and records/current-state.md; then only relevant architecture, effective decisions,
unresolved errors and active handoffs. Recheck the actual root, branch, commit and
working changes; reread within a task when the baseline or relevant rules change.
Report missing/stale sources and conflicts. Keep local, remote and deployed state
separate; do not silently adopt a code defect as policy or execute old handoff actions.
Read-only review does not authorize initialization, repair, records or tests.
Authorized implementation includes proportionate local verification unless the
user restricts it. Ask before destructive operations, credentials, external
publication, paid calls or material scope expansion.

## Responsibilities

Keep the root AGENTS.md short, detailed policy in office/AGENTS.md, procedures in
skills/, deterministic helpers in scripts/, templates in templates/ and governance
checks in tests/. Keep product code and executable tests in their native locations.
Project-specific skills, connections, demos and caches are not bootstrap content.
Governance initialization is not an upgrade: review differences and obtain upgrade
authority before merging existing rules; never overwrite them with the seed.

<!-- test-governance:start -->
## Change-Test Governance

Use govern-change-tests for authorized behavior changes or known-error fixes when
that skill is available. If unavailable, report the dependency; do not auto-install.
Keep canonical cases and known errors under records/ and executable product tests
in the native project locations. Derived tests are not user-confirmed contracts.
Confirm purpose, process and expected result before promoting canonical cases.
Verified errors require passing regression evidence or a user-approved manual
waiver; invalidate evidence when related behavior changes. Structure checks do not
prove product behavior or live release readiness.
<!-- test-governance:end -->

## Records

Only when writes are authorized, append durable decisions and concise substantial
task evidence to records/decision-log.md and records/task-log.md. Prefer evidence
links. Do not store credentials, personal material, full transcripts or duplicate
raw logs. Preserve history with superseding entries. A read-only request overrides
routine logging. Use skills/manage-agent-governance/references/records.md for the
dual-entry record workflow. records/README.md is the human entrance and
records/agent-index.md is the agent entrance; both link shared facts. Preserve
existing architecture and testing authorities. Record source/version and separate
implemented behavior, historical test evidence and current verification.

## Records at Task Completion

Before closing authorized implementation or maintenance, follow [the shared-fact lifecycle](skills/manage-agent-governance/references/records.md). Compare the actual task diff and validation with the affected current facts, architecture/contracts, decisions, changes, test evidence and handoffs. Update the affected authoritative source first; change either entrance only if its navigation or short summary changed. Do not duplicate evidence or add logs for trivial questions or formatting.

The completion report must identify updated records, or explain why no record update was needed, and disclose any deferred update with its reason, affected conclusion and next step. Do not report documentation synchronization complete while a relevant fact remains stale. Distinguish implemented behavior, historical evidence and current verification; preserve history through appended corrections or superseding entries.

Read-only instructions and execution limits take precedence: report gaps in the response without routine record writes or tests. These are agent workflow obligations, not a background service or proof of compliance; structure/link checks cannot prove factual freshness or that an agent read the sources.

## Validation and delegation

After authorized governance changes run scripts/Test-OfficeGovernance.ps1; after
script, template, skill or test changes also run tests/Test-OfficeGovernance.ps1.
The self-tests create isolated temporary fixtures and are not a read-only audit.
Report actual results, scope and skipped checks. Do not automatically activate
Piecewise, release checks, independent model collaboration, deployment or paid
evaluation; each workflow retains its own human authorization requirements.
