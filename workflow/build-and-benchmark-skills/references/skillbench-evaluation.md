# Low-Usage SkillBench Evaluation

Use this reference when creating a case, freezing variants, running SkillBench, or interpreting its evidence.

## Evaluation Ladder

Advance only when the previous stage is valid:

1. **Static checks — 0 model sessions.** Validate the skill package, scripts, fixture, verifier, and secrets exclusions.
2. **SkillBench dry run — 0 model sessions.** Freeze the CasePack and SkillPacks, inspect their IDs, and confirm the planned settings and session count.
3. **Execution preflight — use existing evidence first.** Confirm the target launcher can honor the requested sandbox before spending a write-producing A/B run.
4. **Sentinel A/B — 2 model sessions by default.** Run one case against baseline and candidate once, then analyze the saved evidence by human review.
5. **Variance check — additional approval required.** Increase repetitions or cases only when the sentinel is valid and the decision warrants the extra usage.
6. **Release evidence.** Run the target production model and representative case set only after its budget is stated and approved.

Calculate the default sentinel budget with:

```text
python scripts/plan_skillbench_budget.py --cases 1 --variants 2 --runs 1 --max-sessions 2 --json
```

## Execution Preflight

- Treat the sandbox value printed by dry-run as the requested configuration, not proof of the effective nested Codex policy.
- Reuse recent compatible evidence that a write-producing run can create a file in its disposable workspace. Do not spend a new preflight session when such evidence already exists.
- On Windows, SkillBench 0.1.0 may need `SKILLBENCH_AUTH_HOME` pointed at the active Codex auth directory, Git's POSIX `sh` on `PATH`, and the native `codex.exe` directory before npm wrappers.
- If the saved Codex session context reports `read-only` for a requested `workspace-write` run, classify the comparison as environment-blocked. Do not retry or interpret its verifier failures as skill quality. Use a compatible WSL/Linux launcher or redesign the case as a genuinely read-only evaluation.

## Docker Launcher on Windows

Use `scripts/Invoke-SkillBenchDocker.ps1` when the Windows Codex Desktop host overrides a nested write-producing run. The container pins SkillBench 0.1.0 and Codex CLI 0.146.0, provides Linux `sh`, and mounts only the project workspace. The host Codex auth file is mounted read-only and only for a real run; it is not copied into the image or workspace.

`-Mode Check` launches the inner Codex sandbox without a model call, explicitly selects the same legacy `workspace-write` policy used by SkillBench, creates and removes a unique file in `/workspace`, and fails unless that write succeeds. `-Mode Run` repeats this preflight before mounting auth or starting a session. The launcher uses `docker/seccomp-codex-sandbox.json`, a pinned derivative of Moby's Docker 29.5.3 default profile. It preserves the default deny action, drops all outer Linux capabilities, and adds only the traced rules needed by Codex CLI 0.146.0: the exact namespace combination used by `clone`, `CLONE_NEWUSER` for `unshare`, and `mount`/`pivot_root`/`umount2` inside the resulting unprivileged namespaces. It never uses `seccomp=unconfined` or `CAP_SYS_ADMIN`.

The upstream profile source is `https://raw.githubusercontent.com/moby/moby/docker-v29.5.3/vendor/github.com/moby/profiles/seccomp/default.json` with SHA-256 `536529b665dd0972c37bfb569f5d4ac8a53592e7b00752bc39ff063ca9864c74`. The launcher separately pins the complete derived profile hash and fails closed if it changes. Re-trace and re-review the policy before changing the Docker or Codex versions. The image also provides `python` as an alias for Python 3 so frozen verifier commands remain portable.

Run these zero-session stages first from PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\workflow\build-and-benchmark-skills\scripts\Invoke-SkillBenchDocker.ps1 -Mode Build
powershell -NoProfile -ExecutionPolicy Bypass -File .\workflow\build-and-benchmark-skills\scripts\Invoke-SkillBenchDocker.ps1 -Mode Check
powershell -NoProfile -ExecutionPolicy Bypass -File .\workflow\build-and-benchmark-skills\scripts\Invoke-SkillBenchDocker.ps1 -Mode DryRun
```

Record the `cpk_*` and both `spk_*` IDs printed by dry-run. Do not substitute source paths during the paid run. After the user approves exactly two model sessions, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\workflow\build-and-benchmark-skills\scripts\Invoke-SkillBenchDocker.ps1 `
  -Mode Run `
  -CasePackId cpk_FROM_DRY_RUN `
  -BaselineSkillPackId spk_BASELINE_FROM_DRY_RUN `
  -CandidateSkillPackId spk_CANDIDATE_FROM_DRY_RUN `
  -ConfirmModelSessions 2
```

The launcher deliberately has no Codex-analysis mode. Create the evidence bundle with `-Mode Analyze -ComparisonId cmp_...`; this uses human analysis and zero model sessions. Never mount the Docker socket, the full user home, or credentials inside the benchmark workspace. Keep `workspace-write`; do not raise the inner sandbox merely because the outer boundary is a container. Do not replace the pinned profile with `seccomp=unconfined` or add `CAP_SYS_ADMIN` to bypass a failed preflight.

## Case Layout

```text
benchmarks/my-skill/
|-- case.json
|-- workspace/
|   |-- fixture files
|   `-- verify script
`-- variants/
    `-- baseline/
        `-- SKILL.md
```

The candidate may point to the actual skill directory instead of duplicating it.

A minimal case is:

```json
{
  "name": "observable behavior",
  "workspace": "workspace",
  "prompt": "Use $my-skill to inspect input.txt and create result.json.",
  "exclude": [".env", "node_modules", "dist"],
  "artifacts": ["result.json"],
  "verify": ["python verify.py"],
  "metadata": {
    "decision": "candidate improves the required result without weakening safety"
  }
}
```

Paths are relative to `case.json`. Keep verifier scripts inside the workspace when they must run against the isolated final tree.

## Verifier Rules

- Verify observable outcomes and safety: exact files, JSON schemas, expected values, preserved inputs, prohibited side effects, project-native tests, and exit codes.
- Keep expected data unavailable to the agent when it would reveal the answer. The verifier may hold gold values that the prompt and skill cannot access.
- Avoid checking generated prose word-for-word. Check a structural field only when that field is part of the actual artifact contract.
- Keep the fixture disposable. Never use production systems, credentials, personal data, or commands with external side effects.
- Treat every `verify` command as trusted host code: SkillBench executes it through host `sh -c`, outside the Codex sandbox.

## Fixture Fidelity and Retry Stop

Treat every supplied fixture as opaque binary input even when it is a text file. Scaffold the complete case directory tree first, write generated text and code second, then copy fixtures with `../scripts/copy_fixture.py`. Require the helper's source and destination SHA-256 values to match before freezing the case. Do not reproduce a fixture with a patch, here-string, editor, newline conversion, or text copied from terminal output.

When a tool reports `Resource temporarily unavailable`, `Can't fork`, or an equivalent process or namespace-spawn failure, retain that evidence and run no more than one zero-model health probe. If the same failure class repeats, stop further patch and command retries, preserve all artifacts already written, and classify the attempt as blocked. A fresh run requires a healthy environment; repeated retries are not evidence of skill quality and waste the evaluation budget.

## Reproducibility

Before comparing results, keep these identical: case definition, frozen workspace, model, reasoning effort, sandbox, Codex version, verifier, dependencies, repetition count, and price snapshot. Rotate variant order across repeated runs when supported.

Use frozen `cpk_*` and `spk_*` IDs from the approved dry run for the real run. Record the resulting `run_*` and `cmp_*` identifiers, but do not copy credentials or full private traces into governance records.

## Interpretation

Outcome and safety are gates. Efficiency is a secondary comparison among candidates that pass those gates. One run can reveal a clear failure but rarely proves stability; expand repetitions only when the remaining uncertainty affects the decision.
