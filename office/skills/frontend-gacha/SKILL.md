---
name: frontend-gacha
description: Generate five visually distinct small interactive frontend demos from one brief, compare them, and package the user's choice. Use for frontend style exploration, UI gacha, or requests to compare several design directions. Store demo code under the target project's ./office/frontend-gacha/. Not for a single finished frontend, a full application, or backend implementation.
---

# Frontend Gacha

Turn a prompt into five small, comparable, working demonstrations. The user chooses the direction. Use their language for copy and explanations.

## Agreed defaults

- Scope one representative component, section, or compact screen with 1–2 meaningful interactions. Keep all five variants on the same functional scope, copy, fixture data, and initial state.
- Choose five distinct visual directions from the brief. Differentiate typography, palette, layout, component shapes, spacing, and visual treatment; a recolor alone is insufficient. Explain each direction in one sentence. Respect explicit brand constraints.
- Keep all generated demo code, comparison pages, design notes, screenshots, and selected copies inside the **target project's** office/frontend-gacha/ directory. This is not the installed skill's office directory.
- Preserve every round and all five original demos. Package the selected demo separately. Integration into application routes or production code is a subsequent user request.
- This skill guides Codex to write the demos. The helper only manages directories, comparison pages, and selection copies; it does not call a model or invent designs.

## 1. Resolve the brief

Resolve the target project root from its checkout or the user-selected directory and read applicable governance. If project adoption requires an Office bootstrap, use that project's approved bootstrap before work.

Use the prompt and project context to identify the product, audience, one demo slice, common content/data, and key interaction. Infer ordinary choices; ask only if the missing product or target prevents a useful demo. Avoid an interview when the prompt already supplies enough.

Default to standalone HTML/CSS/JavaScript for a small offline demo; this is a preview delivery format, not a decision about the application's stack. Follow an explicit framework requirement using an isolated preview under office/. Keep dependencies local to that preview. Each variant must have a self-contained variants/A/index.html (through E) with its assets inside that variant directory. Use fictional data, local/system fonts and local assets where practical. Buttons must visibly perform the demonstrated action.

Read [the output contract](references/output-contract.md) for the manifest and helper commands.

## 2. Choose the visual directions

Use the installed ui-ux-pro-max skill as the design reference:
1. Locate it in the active skill catalog; otherwise inspect the sibling personal skill directory, then the standard .agents/skills and .codex/skills locations. Read its SKILL.md and invoke its search script by its actual absolute path.
2. Query one relevant design system and focused style guidance as needed. Check the returned product/category; retry once if mismatched. A recommendation is a starting point, not a requirement for all five variants to share its style.
3. Record only the useful source identities and decisions in the run's brief.md. Do not copy its whole catalog or license it as your own.
4. If unavailable or unmatched, disclose the missing reference and proceed with clearly labeled design judgment; do not silently install it or fabricate search results.

Choose directions for this subject, not the same five presets every time. Before coding, compare every pair: aim for meaningful differences on at least three visual axes while preserving the common task. Keep motion restrained and honor reduced-motion preferences.

## 3. Make a round

Run the helper's init command to allocate a new numbered round. Complete brief.md, fixture.json and manifest.json, then implement A–E. Put each complete demo and its relative assets inside its own variant folder. Embed fixture values for file-based previews rather than fetching sibling JSON at runtime.

Use UI behavior appropriate to the small slice: filtering, selecting, expanding, toggling, or a mocked form confirmation. Do not add accounts, backend services, payments, or full multi-page flows just for comparison.

Run build only when all five demos and their descriptions are ready. It creates the comparison index.html. For a user-requested reroll, create the next round; copy any retained variants into it and regenerate only requested directions. Do not erase older rounds.

## 4. Verify and present

Open the built comparison and each demo when browser tools are available. Check desktop and narrow mobile widths, one common interaction in every variant, keyboard focus, text readability, layout overflow, and missing assets. Inspect the actual rendered result. If visual verification is unavailable, say so and distinguish it from helper/static checks.

The gallery supports choosing a favorite and copying a follow-up request. Explain that the user must paste the copied text into this task; it does not automatically send a message or save a selected code package.

For offline HTML, provide the actual file link. When a localhost server is needed, serve only this round, bind to 127.0.0.1, use a verified free port, and start it without a visible helper window. Keep the port and URL accurate. Do not change application routes to show the demo.

Summarize A–E briefly, link the comparison, and wait for the user's choice. Do not choose a winner for them.

## 5. Preserve the choice

For a clear choice such as "B", run select. It copies the whole selected variant into a new selections/<timestamp>-B-<id>/code/ directory and records source file hashes in selection.json. Preserve all originals and earlier selections.

If the user asks to combine A's layout with C's typography, build and verify the combined demo in a new round (copy the retained variants), then package the new chosen variant. Record what was combined; do not label an unchanged copy as a synthesis.

Return links to the selected code entry and selection record. Demo selection alone does not authorize application integration. Follow an explicit later integration request normally.

## Attribution

The five-variant comparison, feedback, and synthesis workflow is informed by 0xdesigner's Design Lab. This package's helper and gallery are independently authored. See [sources and licensing](references/sources.md) and the [README](README.md). Preserve those notices when distributing this skill.
