# Project read-only browsing

Use when the user asks Claude to inspect the project directly and follow call chains on demand. This option adds a code structure document and literal search to the existing frozen reader. It is a snapshot audit, not unrestricted access to a live working directory. It does not authorize implementation, a new provider call, or a different billing route.

## Prepare the code structure and scope

1. Resolve the real project root and read governance. Select source directories, never the user's home, outer business-material directory, or runtime state. Preserve uncommitted source: the working tree, not only HEAD, is the intended snapshot.
2. Generate a candidate inventory without inference:

   ```text
   python <skill>/scripts/project_map.py --root <project-root> --include app brain bridge body contracts frontend --output office/records/review-context/code-catalog.md --manifest .work_tmp/code-catalog.json
   ```

   Use actual directories for the target project. Existing output files are not overwritten. Common private/runtime paths, binary files, vendor bundles, and links/reparse points are excluded. The inventory is limited to 2,000 files / 20 MB, with 2 MB per file. Exclusions mean the map is not a whole-filesystem inventory. Filename filtering cannot detect secrets or private text embedded in source; inspect selections before model access.
3. Write or reuse a concise project-specific structure document under Office. Explain entry points, module responsibilities, main user flows, producer/consumer relationships, important symbols to search, and test locations. Link actual paths. Mark historical architecture and unresolved ownership explicitly. A file catalog alone is not an architecture explanation.
4. Prepare the normal Office index: brief, structure document, applicable full AGENTS.md/CLAUDE.md, selected complete code and synthetic tests. The reviewed source set is explicit; the candidate manifest is not automatically an allowlist. Keep governance, goal, acceptance criteria and structure inline. No original enterprise documents, databases, environment files, credentials, raw logs or prior reviewer conclusions.
5. Use `bridge.py prepare --spec <base-spec> --index <index> --output <draft> --project-structure <Office-structure-path>`, then run `inspect`. Start with a base spec that has `mode: audit`, `base_ref: null` and no `restricted_read`. This prepares (without confirmation or inference) the following option, selecting all indexed files except the brief, structure and governance. All deferred index entries must use complete files. Inspect the resulting list and edit the unconfirmed draft limits if needed before confirmation:

   ```json
   "restricted_read": {
     "mode": "project",
     "structure": "office/records/review-context/code-structure.md",
     "files": ["src/entry.py", "src/service.py", "tests/test_service.py"],
     "max_requests": 24,
     "max_response_chars": 12000,
     "max_total_chars": 120000,
     "max_turns": 12
   }
   ```

   `files` must already be indexed complete files. Root and applicable nested governance, the brief and structure cannot be deferred. This mode is valid only for `mode: audit`, `base_ref: null`, and a Claude reviewer. It intentionally permits changed source and review targets to be read on demand; the original packet-only and dependency-only modes still require changed files inline. It is not an exception allowing excerpts to masquerade as complete changed files. Deleted files and diff reviews use the existing inline workflow.
6. Confirm the exact models, roles, usage route, round limit, selected scope and read/turn budgets through the existing workflow. `init`, `confirm`, `snapshot`, and `review` then work normally. Updating a confirmed scope requires a new spec, never mutation of historical confirmation. Skill installation and inventory generation do not consume a model call.

## What Claude can do

- Start from the supplied structure and exact-path catalog.
- `mcp__review_packet__search_sources` performs a case-sensitive literal search with `query`, `path_prefix`, `offset`, and `limit`. Empty prefix searches the selected catalog. Results contain paths and original line numbers only, with `next_offset` for pagination. No regex, glob expansion, shell or live path lookup.
- `mcp__review_packet__read_source` returns exact selected line ranges. Large functions can be read in consecutive ranges within the confirmed budget.
- Follow call chains across the frozen selected files. If a necessary file is absent, request it as missing context; do not invent its behavior or expand permissions.

Both tools share the request and returned-character budgets. Repeated reads and denied requests count. One CLI invocation may use multiple model turns: call count and returned characters are not token usage or guaranteed savings. Record observed provider/cache counters separately.

## Evidence and boundaries

The model gets one local MCP server and no built-in shell, write, network, or arbitrary-file tools. The reader serves an immutable in-memory source bundle; no reviewer-supplied path opens a live file. Source hashes detect working-tree changes before dispatch and on later status checks. The structure document is a navigation aid, never evidence of a business fact.

Search events record coordinates, query fingerprint and size; they do not record raw query/source text in Office and **do not grant source coverage**. Findings must cite inline or actually returned source lines. Unread ranges remain visible. A report can be received with partial coverage, but project mode blocks full `finalize` while selected source remains unread. Split a later audit into a smaller confirmed scope if appropriate; do not erase unread evidence or broaden a clean conclusion.

Native Claude history remains enabled and may contain the authorized source returned to the model. Temporary source bundles are removed after the invocation. Read-only CLI restrictions are tool-level controls, not a new OS security sandbox. Offline tests verify construction, protocol and evidence gates; they do not prove a live Claude run succeeds.
