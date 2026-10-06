# Office-organized review context

Use this workflow for new reviews and repair follow-ups. It prepares unconfirmed drafts and measures input without calling either model. Existing confirmed legacy specs remain readable; do not rewrite historical run specs or confirmations.

## Select one coherent question

Read the target project's Office index, applicable agent rules, relevant contract sections, linked test cases and known-error records locally. Use them to select sources, not as a reason to send all Office records. Keep one brief containing the original requirement, exact review boundary, baseline and limitations. Do not copy full history, original business documents, prior model opinions or raw test logs into it. For mutual first rounds exclude peer conclusions.

First review: include the actual implementation and critical callers. Repair review: compare against the last reviewed source baseline and include the changed implementation, affected callers/contracts and regression tests. Preserve unresolved prior findings in their original records. A narrow follow-up does not re-certify omitted modules or erase pending context requests. Split unrelated audit questions into separate proposed scopes, but never create extra model calls without the user's existing budget/authorization.

Use existing Office paths; a small `office/records/review-context/<task>.json` is a convenient index, not a new mandatory directory tree. It stores references, not copies:

```json
{
  "brief": "office/records/review-brief.md",
  "contracts": [{"path": "office/fixed_contracts.md", "ranges": [[40, 72]]}],
  "changes": ["src/parser.py"],
  "dependencies": [{"path": "src/caller.py", "ranges": [[20, 90]]}],
  "tests": ["tests/test_parser.py"]
}
```

Resolve these example paths and line ranges against real current source. `changes` is the review target list (including for a snapshot audit), not an automatically inferred dependency graph. No recursive folder expansion occurs. Root AGENTS.md, office/README.md and office/AGENTS.md are always included in full. Add relevant nested instructions explicitly and in full.

- `brief` and `contracts` must live under Office. Choose contract sections and test-case records relevant to the behavior. Keep the brief free of private source text.
- Only contracts and dependencies allow ranges: positive, ordered, disjoint inclusive original line numbers. Select complete functions/sections plus necessary imports/constants/callers, not isolated favorable lines.
- Changes and executable regression tests are sent in full. With a Git baseline, any changed file configured as an excerpt is rejected. Non-Git projects require the lead to identify all changed targets explicitly; no implicit baseline is claimed.
- All selected files are hashed in full even when excerpted. Editing an omitted line makes the snapshot stale. Excerpt reports may cite only supplied line ranges. Omitted lines are never marked reviewed.
- The index is hashed into the spec. Updating it requires a new draft/confirmation under the existing authorization rules. Sources remain authoritative; hashes and lead briefs never substitute for source review.

## Prepare and inspect before spending

Start with an ordinary spec containing the agreed models, roles, purpose, criteria, tests and actual baseline. `prepare` replaces its file selection from the Office index and creates a new file without overwriting anything:

```text
python <skill>/scripts/bridge.py prepare --spec <base-spec.json> --index office/records/review-context/<task>.json --output <temporary-draft.json>
python <skill>/scripts/bridge.py inspect --spec <temporary-draft.json>
```

New indexed drafts default to at most 120,000 characters (or the original lower limit). This is an input-size control, not a token/cost estimate. If necessary full source cannot fit, split coherent scopes or provide `--max-packet-chars <justified-limit>` while preparing a draft; do not silently raise a confirmed limit. `inspect` lists largest sources, full/excerpt modes and uncovered changed paths; it can inspect an over-budget draft without invoking a provider. Its count is before current test evidence; `review` checks the final prompt including test/peer data before dispatch. Snapshot and attempt records retain counts/hashes, never packet copies.

Confirm the resulting actual scope/models/billing/budget under the skill's existing human-confirmation rules, then init, confirm, snapshot, test and review. Do not use a directory title or “Office governed” label to waive missing review coverage.

## Reuse and cache limits

The packet orders governance, contracts and unchanged dependencies before per-revision sources, goals, diffs, hashes and execution evidence. This preserves more unchanged prefix text across matching requests. The current CLI transport still sends one text prompt: ordering does not force provider cache breakpoints or guarantee cross-run hits. Keep the existing stable Claude working directory and model settings; new reviewer processes remain independent. Do not use --resume for independent first-round review or switch to a paid API to gain cache controls.

Review metadata records observed cache reads/writes and a warning for a large input with less than 20% cache reads. Missing counters are reported as unavailable. These ratios are not subscription quota or billing multipliers. On a warning, inspect and narrow the next packet before another call; do not automatically retry, prewarm caches, or run keepalive requests. Input reduction remains useful even when cache reuse is unavailable.
