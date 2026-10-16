# Restricted reading of frozen review materials

Use for Codex-led Claude reviews when optional contracts or dependencies make the initial packet large. This is an opt-in transport capability, not authorization to start a new model run. Existing exact model, effort, role, billing and round confirmation still applies. Codex reviewers and mutual audits currently reject this option before dispatch; they retain packet-only operation.

For project-wide navigation with a code structure and literal search, use the separate opt-in [project mode](project-reading.md). The rules below describe the original dependency-only mode and remain unchanged.

## Prepare the scope

1. Prepare the normal Office index and draft. Keep the original goal, criteria, governance, brief, changed implementations and regression tests inline. Applicable nested agent rules must also remain inline. Defer only context that is optional for the initial question; no core evidence should depend on a successful later read.
2. In the unconfirmed prepared spec, add `restricted_read` below. Every listed file must already be an indexed `contracts` or `dependencies` entry. Existing line ranges remain the entire readable boundary: a path in the catalog does not grant access to omitted lines. A changed or deleted dependency cannot be deferred. For non-Git projects, the lead must identify changed dependencies and keep them inline.
3. Run `inspect`, review both initial size and maximum returned content, then confirm the actual scope and limits through the normal workflow. Never retrofit an existing confirmed spec. To expand the allowlist, prepare a new confirmed run under the existing rules.

```json
"restricted_read": {
  "files": ["src/dependency.py", "office/contracts.md"],
  "max_requests": 8,
  "max_response_chars": 12000,
  "max_total_chars": 48000,
  "max_turns": 6
}
```

These are adjustable example limits, not automatic defaults. Limits are validated: requests 1–32, per-response characters 256–50000, cumulative returned characters 256–200000, agentic turns 2–20; per-response must not exceed cumulative. The regular `max_packet_chars` still bounds the initial prompt. Characters are not tokens. Read budgets count each returned JSON text payload once, including repeated reads; they do not measure repeated context processing inside subsequent model turns, tool schemas, CLI/system prompts, or subscription consumption. Record provider token/cache counters separately; missing counters remain unknown. A single CLI invocation may contain several model turns and incur more usage than packet-only review.

## Read contract and enforcement

The model sees a catalog with exact relative paths, allowed original line ranges and content fingerprints. Its sole data tool is `mcp__review_packet__read_source`, taking exactly `path`, `start`, `end` (inclusive, one-based). It reads a frozen in-memory copy loaded from a fingerprint-checked temporary bundle, not the working tree. There is no search, glob, directory listing, network, shell, write, or arbitrary path endpoint. Unknown paths, traversal, aliases, omitted lines, disjoint gaps and invalid types are denied. Returned excerpts preserve original line numbers.

Each read attempt, including invalid and repeated requests, consumes the request budget. Content is never silently truncated. A response that exceeds the per-read limit is denied and may be replaced by a smaller request within remaining limits. Exhausted limits require an explicit coverage gap/context request, not a new automatic invocation. A reader reconnect cannot reset its audit or budgets. The CLI has the confirmed turn limit plus the existing timeout; bridge retries remain disabled.

The Claude command retains `--restricted`, no built-in tools, disabled skills/hooks, isolated setting sources, and strict MCP configuration. It allows only this reader tool from one local server. Unlike packet-only mode, it cannot use `--safe-mode`, which disables MCP. Do not substitute `--bare`, which changes authentication behavior. Auto memory and discovered CLAUDE.md content are disabled through explicit settings. This is a tool-level boundary under the CLI's permissions and managed policy, not a new OS sandbox or a boundary against a malicious local user. If organizational policy or CLI compatibility prevents reader startup, the attempt is blocked without silently widening access or switching billing routes.

Official CLI flag behavior: [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference). Offline tests establish the reader/protocol and generated adapter behavior; they do not establish successful live model tool use.

## Evidence and completion

The selected source hashes remain part of the revision fingerprint. The invocation copies already-collected content into a temporary bundle; it never grants the reviewer the repository path. Edits to selected files, including omitted lines, retain the existing stale-evidence behavior. Runtime read audits live beside the temporary bundle, outside Office. Only fingerprints, exact returned ranges, counters and denial counts enter durable records; raw content and arbitrary denied arguments do not. Claude native session history may contain returned material, just as it contains the initial prompt. Temporary bundles are removed after invocation; saved history does not restore the expired reader or authorize another call.

An initialized reader audit matching the bundle is mandatory. Missing, malformed or mismatched audit evidence blocks report acceptance. Findings must cite inline lines or actual successful reads; catalog presence never establishes coverage. Metadata retains read events and unread ranges; `status`, `finalize` and the acceptance record expose remaining unread ranges. Unused optional context does not automatically block scoped acceptance, but necessary missing context must remain in `context_requests` and prevents completion. Describe the result as review of supplied and returned evidence, never as complete review of the allowlist. A served range proves delivery, not the quality or completeness of reasoning about it.

Keep the existing distinction between one invocation attempt, internal model turns, effective reports and actual token usage. No extra model call is made by the MCP server. No cache or total-usage improvement is claimed until measured in authorized real runs.
