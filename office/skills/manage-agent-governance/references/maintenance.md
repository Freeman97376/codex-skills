# Maintenance Boundaries

## Initialization and upgrades

The seed manifest is an exact source-to-destination map. It includes generic
policies, this skill, deterministic governance helpers, clean templates and tests.
It deliberately omits other skills, local configuration, connection profiles,
credential references, demos, caches, build products and the source project's
records. Optional workflows are named dependencies, not copied installations.

Use a trusted seed and an explicit project root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File 'C:\path\to\trusted-seed\office\scripts\Initialize-Office.ps1' -ProjectRoot 'C:\path\to\project' -Plan
```

The preview returns Create, Unchanged, PreserveRecord or ReviewRequired, exact
source/target paths and SHA-256 fingerprints. It writes nothing and executes no
validator or test. For an authorized initialization omit -Plan. Differing existing
governance blocks the entire copy before writes, even if it contains valid custom
rules. This is a review requirement, not a claim that custom rules are defective.
Existing records remain unchanged. A later I/O failure may leave newly created
files; report partial progress rather than deleting them or claiming rollback.

For repair or upgrade, present a per-file comparison, intended rule changes,
stricter target rules to retain, dependencies and migration/verification steps.
Within granted upgrade scope, merge only selected changes. Do not use -Force,
delete target rules to bypass conflicts, or assume skipped files are current.
The manifest version is a format version, not proof that a project has upgraded.
Git-root mismatch, linked paths or missing seed files require correction before
initialization. Concurrent filesystem replacement is outside this helper's
guarantee; use a stable, trusted source and target during the operation.

## Read-only review

Explicit read-only requests override routine record requirements. Report findings
in the response; do not initialize office/, repair files, append logs or run the
fixture self-tests. Structural checks are opt-in within the user's execution
limits. A preview lists differences but does not establish semantic correctness.

## Records maintenance

Use [dual-entry records](records.md) for human and agent navigation over shared
facts. Current facts are updated, historical events are appended or superseded,
and handoffs track current work until completion. Retain existing architecture,
decisions and testing records as authorities. Automatic summarization, full-text
index services and archival/deletion automation remain outside this initial module.

## Package and publication review

Before separately authorized publication, compare the maintained source with the
exact staging copy and list intentional exclusions. Verify all manifest sources
and bundled local Markdown links, parse PowerShell examples and inspect placeholder
commands for complete arguments and quotes. Redact with complete generic values,
never substring replacement that truncates a command. Check for credentials,
private profiles and project-specific material without dumping their contents.
Do not claim an omitted dependency was packaged or a stale copy was refreshed.
Publish approval applies to the reviewed artifact, not any future modifications.

Local structural checks and isolated regression tests do not verify remote
publication, account state, production behavior, live review or release readiness.
