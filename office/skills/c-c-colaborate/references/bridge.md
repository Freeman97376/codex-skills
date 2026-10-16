# Bridge operations

Use Python 3.11+ and absolute script paths. No third-party Python package is needed. The helper orchestrates reviewers; the active host agent performs authorized implementation and repairs. Running preflight, init, status, snapshot, or adapter installation makes no model inference calls. Review and cross-review do consume model usage.

## Project browsing option

For structure-first project inspection, see [project reading](project-reading.md). It uses the existing `restricted_read` spec with `mode: project` and an inline Office `structure` path. `project_map.py` creates an offline candidate catalog. Only this snapshot-audit mode enables literal search and permits complete targets to be deferred; normal changed-file and restricted-dependency rules remain unchanged.

## Prepare and confirm

The optional `restricted_read` spec field enables [frozen allowlisted reading](restricted-reading.md) for a Claude-only reviewer run. It adds explicit file, request, response-character, cumulative-character and turn limits; omission preserves packet-only behavior. The dependency-only form and the project mode above are the exceptions to the no-fetch descriptions below: only already-selected frozen ranges can be fetched, never missing project files.

For new scopes, use [Office context selection](office-context.md) to prepare a bounded file/range index, then run `prepare --spec <base-spec> --index <Office-index> --output <new-draft>` and `inspect --spec <new-draft>`. Both are zero-inference operations. The generated optional `context_index` contains `path` and `sha256`; all other schema fields below are unchanged. Legacy specs without it keep their complete-file semantics and existing snapshot fingerprints.


1. Read the target project's governance, inspect its current worktree, and run its Office validator. Add applicable nested AGENTS.md/CLAUDE.md policies, relevant callers, test helpers, and dependency contracts to the selected files. Include a relevant base commit for change review. For a non-Git project include a relevant before-state file when needed; never pretend a snapshot is a diff.
2. Run `python <skill>/scripts/bridge.py preflight`. This locates native CLIs, checks versions and filtered login status. It never logs tokens or copies credentials. A discovered executable or cached model name is not evidence of actual model availability.
3. Draft the spec below outside permanent records. Replace placeholders with verified exact model IDs and the real project path. Show the human the selections, effort, roles, usage route, extra-usage setting, bounded scope, test execution and maximum rounds. Confirm the active lead model in its host UI; the bridge cannot switch or attest an already-running conversation.
4. Run `init --spec <absolute-spec.json>`. It prints the immutable spec hash and Office run directory. Only after actual human confirmation run `confirm --run <run-dir> --spec-hash <hash> --human-reference <short-message-reference>`. An agent recording a confirmation is an audit trail, not independent proof of consent. Do not invent it.

```json
{
  "run_id": "feature-review-001",
  "project_root": "C:/path/to/real-project",
  "mode": "implement-review",
  "lead": "codex",
  "models": {
    "codex": {"model": "REPLACE_EXACT_CODEX_ID", "effort": "high", "billing": "subscription", "extra_usage_allowed": false},
    "claude": {"model": "REPLACE_EXACT_CLAUDE_ID", "effort": "high", "billing": "subscription", "extra_usage_allowed": false}
  },
  "reviewers": ["claude"],
  "goal": "Original human requirement, not the implementer's proposed answer.",
  "acceptance": ["Observable accepted behavior and relevant contract references."],
  "files": ["src/changed.py", "tests/test_changed.py"],
  "base_ref": null,
  "max_rounds": 3,
  "timeout_seconds": 600,
  "max_packet_chars": 400000,
  "allow_test_execution": true,
  "tests": [{"id": "regression", "argv": ["C:/Python314/python.exe", "-m", "unittest", "discover", "-s", "tests", "-p", "test_changed.py"]}],
  "no_tests_reason": ""
}
```

`base_ref` is null for a snapshot-only audit, or a full resolved commit hash for a diff review. Confirm this distinction with the scope. Both model selections are recorded even when only one external CLI runs. For Claude lead/Codex review set `lead: claude`, `reviewers: [codex]`. For mutual audits use `mode: mutual-audit`, `reviewers: [codex, claude]`; the current conversation remains coordinator. Audit mode has the opposite-provider reviewer and no implementation authority. Set `tests: []`, `allow_test_execution: false` and a meaningful `no_tests_reason` for an audit without command execution.

Exact IDs cannot be rolling aliases such as opus, latest or auto. Supported effort flags can vary; inspect installed CLI help and current official docs before selecting. CLI failures never trigger a fallback. Inherited authentication/provider environment overrides block calls until deliberately resolved; the helper neither clears credentials nor changes authentication. Fable additionally requires explicit extra-usage approval because print mode can charge usage credits. Other account-side credit settings are not observable by this helper: the human must verify them if extra usage is forbidden. No automatic quota reset or budget downgrade is implemented.

## Review and repair

All commands below take `--run <absolute-run-dir>`:

| Command | Result |
| --- | --- |
| `snapshot` | Creates a revision, hashes selected files plus root governance, records Git head, diff fingerprint and uncovered changed paths. |
| `test` | Runs the exact confirmed argv list from the project root; records exit codes and output hashes, not raw logs. |
| `review --provider all` | Dispatches approved reviewers. In mutual mode their first prompts are identical and exclude peer reports; processes run concurrently. |
| `review --provider all --phase cross` | Mutual mode only; both independent reports must exist on this revision before exchanging them. |
| `disposition --finding r001/claude-independent/finding-id --status rejected --evidence "source/test evidence"` | Appends a triage decision; valid states are fixed, rejected, deferred, unresolved. |
| `status` | Reports missing, failed, stale or unverified evidence and unresolved findings. No inference. |
| `finalize --lead-evidence "diff inspection and project validator references"` | Records the lead's scope-limited acceptance only after required gates pass. |

After a repair, snapshot again, rerun tests and review the new revision. A `fixed` disposition requires a later current review; `rejected` requires evidence. Deferred/unresolved findings prevent full acceptance. Model context requests require a new confirmed run with expanded scope. A revision allows one test attempt and one call per reviewer per phase. Even failures consume their slot; an explicitly chosen fresh revision consumes another approved round. There are no automatic retries. Preserve failures and stop at the round limit.

Failed test/review commands exit nonzero as well as returning a blocked/failed JSON status. `status` is a read-only query: inspect its status and reasons rather than treating its successful process exit as acceptance. CLI-internal transport or structured-output retries can still occur within the configured timeout; the helper never starts an additional inference process automatically. If a native test fails, use its exact command and normal project debugging workflow to inspect the relevant failure; the collaboration record deliberately retains hashes instead of full output.

Reviewers receive selected UTF-8 text, a diff if available, requirements, governance and concise test results. They cannot independently fetch missing files in this bounded-packet mode. Missing sources are accepted only as deletions proved against `base_ref`; binary/oversize files, common secret paths and paths escaping the root are refused. This filename check is not a secret scanner: inspect selected content and requirements before sending them. Custom policy outside the declared files must be included explicitly. No blanket whole-repo pass is claimed.

The helper starts isolated, short-lived reviewer CLI processes with project customizations, hooks, MCP and tool execution disabled using installed-version flags. This minimizes interference; CLI flags are not an OS-level security boundary. Test commands are real authorized commands and can have the side effects of the project's normal tests. Neither helper nor reports authorize additional commands or scope. Do not run both models as writers to the same checkout.

Actual provider model metadata is recorded separately from the requested ID. A mismatch fails. If a CLI omits model telemetry, the report is retained as unverified and automatic finalization stays blocked; report this limitation to the user. Never use model-authored prose as identity verification. `status` reports readiness, not correctness; even an accepted revision must be rechecked after source changes. Out-of-scope changed paths block full acceptance; split unrelated user work into an isolated checkout or report the bounded review without claiming completion.

Temporary source packets and raw CLI/test outputs are cleaned up after execution. Office keeps configuration, fingerprints, report summaries, findings and test-result hashes. Do not put secrets in commands, specs or findings. Reports are immutable; dispositions are separate append-only records. A lock prevents concurrent mutation of one run. After interruption, inspect whether its child process is still alive before manually removing a stale `.active.lock`; never auto-unlock or repeat a paid call.

The fresh reviewer receives the complete bounded context every time; this deliberately avoids hidden session state. Shared facts save repeated discovery and documentation work, but do not create shared token caches across providers. A changed spec requires a new confirmation. Prefer small coherent scopes and concise findings to control cost.

## Personal adapters

Run `python <skill>/scripts/install.py` to inspect an installation plan, then add `--apply` for authorized installation. It creates personal entries in `~/.agents/skills/c-c-colaborate` and `~/.claude/skills/c-c-colaborate`. Both point to the maintained source by absolute path. The Codex entry disables implicit invocation in its UI metadata; Claude uses `disable-model-invocation: true`.

The installer checks both destinations before writing. Existing unowned files, user-edited owned files, linked adapter directories and source conflicts cause a stop without overwriting them. Re-running an unchanged installation is idempotent. Source moves require deliberate adapter migration; ordinary source content updates are immediately shared. Restart or refresh each host's skill list if discovery is stale. Use `$c-c-colaborate` in Codex, `/c-c-colaborate` in Claude Code. No account config, auth file or chat history is copied.

## Saved Claude review sessions

Claude reviewer invocations now have unique `--session-id` and `--name` arguments and omit `--no-session-persistence`. The empty stable working directory is `<Claude config directory>/collaboration-reviews`; source packet files and raw subprocess output remain temporary. Native Claude Code history may contain the review packet. Office retains only the `claude_session` locator and normalized report, not a copied transcript. Codex reviewers remain ephemeral.

After a call, `claude_session.persistence` is `saved` only if this invocation's nonempty native transcript exists; otherwise it is `not_verified`. Use the exact `resume_argv` with the installed native CLI. `-p` sessions are excluded from the ordinary picker and `--continue`; open them explicitly with `claude --resume <session-id>`. These are local Claude Code sessions, not automatically claude.ai Chat conversations. Earlier calls made with persistence disabled cannot be retroactively restored from the normalized report. Per-run confirmation, billing checks and limits still apply.

Official reference: https://code.claude.com/docs/en/sessions
