---
name: frontend-gacha
description: Generate five visually distinct small interactive frontend demos from one brief, compare them, and package the user's choice. Use for frontend style exploration, UI gacha, or requests to compare several design directions. Store demo code under the target project's ./office/frontend-gacha/. Not for a single finished frontend, a full application, or backend implementation.
---

# Frontend Gacha

Turn a prompt into five small, comparable, working demonstrations. The user chooses the direction. Use their language for copy and explanations.

## Agreed defaults

- Scope one representative component, section, or compact screen with 1–2 meaningful interactions. Keep all five variants on the same functional scope, copy, fixture data, and initial state.
- Choose five distinct visual directions from the brief. Differentiate typography, palette, layout, component shapes, spacing, and visual treatment; a recolor alone is insufficient. Explain each direction in one sentence. Respect explicit brand constraints.
- Ground the directions in several comparable real webpages before coding. Treat typography and composition as design decisions, not a shared template with five skins.
- Give all five directions a shared readability baseline: sufficiently substantial text strokes, readable foreground/background pairs, and clear controls. Thin type, pale secondary text, and faint hairline borders are not default signals of sophistication.
- Identify missing materials early. Do not generate new icons, illustrations, images, or other custom visual assets without the user's explicit authorization for those materials. Reuse existing authorized assets or show labeled placeholders while awaiting a decision.
- Keep all generated demo code, comparison pages, design notes, screenshots, and selected copies inside the **target project's** office/frontend-gacha/ directory. This is not the installed skill's office directory.
- Preserve every round and all five original demos. Package the selected demo separately. Integration into application routes or production code is a subsequent user request.
- This skill guides Codex to write the demos. The helper only manages directories, comparison pages, and selection copies; it does not call a model or invent designs.

## 1. Resolve the brief

Resolve the target project root from its checkout or the user-selected directory and read applicable governance. If shared records are adopted, read the Agent entrance/current state and relevant design decisions or handoffs; do not mistake an earlier selected demo for an integrated product feature. If project adoption requires an Office bootstrap, use that project's approved bootstrap before work.

Use the prompt and project context to identify the product, audience, one demo slice, common content/data, and key interaction. Infer ordinary design choices; clarify missing product/target information only when it prevents a useful demo. Separately surface material needs and obtain any missing asset-generation authorization as described below. Avoid an interview when the prompt already supplies enough.

Default to standalone HTML/CSS/JavaScript for a small offline demo; this is a preview delivery format, not a decision about the application's stack. Follow an explicit framework requirement using an isolated preview under office/. Keep dependencies local to that preview. Each variant must have a self-contained variants/A/index.html (through E) with its assets inside that variant directory. Use fictional data, local/system fonts and local assets where practical. Buttons must visibly perform the demonstrated action.

Read [the output contract](references/output-contract.md) for the manifest and helper commands.

## 2. Research references and materials

Before designing a new set of directions, read [reference research and materials](references/reference-research-and-materials.md). Normally inspect 3–5 relevant pages across at least two sites, including user-supplied references. Choose comparable page types and content, not just famous homepages. Technical blogs can start with AWS Blogs and Microsoft Developer Blogs. Record actual inspected URLs, access/visual-inspection limits, useful observations, and how those observations inform the variants in brief.md. Search snippets alone are not visual research. If browsing is unavailable or prohibited, disclose the limitation and label provisional design assumptions.

Inventory the materials the demo actually needs: existing assets, missing assets, and any proposed generation. Prompt the user about consequential gaps with concrete options (provide material, reuse available assets, authorize specified generation, or use placeholders). Existing explicit authorization remains valid within its scope; an unanswered question or a general request to make a frontend attractive does not authorize asset generation. Continue independent layout and interaction work while waiting; keep affected material placeholders and limitations visible. Never quietly omit a required material.

Use the installed ui-ux-pro-max skill to supplement the website research:
1. Locate it in the active skill catalog; otherwise inspect the sibling personal skill directory, then the standard .agents/skills and .codex/skills locations. Read its SKILL.md and invoke its search script by its actual absolute path.
2. Query one relevant design system and focused style guidance as needed. Check the returned product/category; retry once if mismatched. A recommendation is a starting point, not a requirement for all five variants to share its style.
3. Record only the useful source identities and decisions in the run's brief.md. Do not copy its whole catalog or license it as your own.
4. If unavailable or unmatched, disclose the missing reference and proceed with clearly labeled design judgment; do not silently install it or fabricate search results.

## 3. Choose the visual directions

Choose directions for this subject, not the same five presets every time. For A–E, record the reference influence, typography roles, composition, and material plan in brief.md. Give headings, body, metadata, and code deliberate roles; vary type families or weight, scale, measure, and rhythm rather than applying one undifferentiated font treatment everywhere. Verify available fonts and the user's language, including CJK fallback. A brand-constrained single family can still have a strong hierarchy.

Apply the guide's reading-comfort checks to weight, size, foreground/background contrast, and meaningful borders together. Prefer regular/medium body strokes as a starting point; judge the actual font rather than enforcing one numeric weight across families. Keep secondary text readable. Distinguish decorative separators from boundaries needed to recognize a control, and check their visibility in each supplied theme/state. Record readability choices alongside the style choices.

Avoid repeating identical cards, centered sections, equal columns, and uniform edges throughout every variant. Use content-led changes in alignment, column proportion, feature size, indentation, and whitespace where the references support them. Keep coherent local alignment and a readable mobile order; arbitrary rotation, ragged controls, and overflow are not substitutes for composition. At set level, typography and layout must both vary meaningfully unless explicit constraints fix them. Compare every pair for meaningful differences on at least three visual axes while preserving the common task. Keep motion restrained and honor reduced-motion preferences.

## 4. Make a round

Run the helper's init command to allocate a new numbered round. Complete brief.md, fixture.json and manifest.json, then implement A–E. Put each complete demo and its relative assets inside its own variant folder. Embed fixture values for file-based previews rather than fetching sibling JSON at runtime.

Use UI behavior appropriate to the small slice: filtering, selecting, expanding, toggling, or a mocked form confirmation. Do not add accounts, backend services, payments, or full multi-page flows just for comparison.

Run build only when all five demos and their descriptions are ready. It creates the comparison index.html. For a user-requested reroll, create the next round; copy any retained variants into it and regenerate only requested directions. Do not erase older rounds.

## 5. Verify and present

Open the built comparison and each demo when browser tools are available. Check desktop and narrow mobile widths, one common interaction in every variant, keyboard focus, text readability, layout overflow, and missing assets. Inspect the actual rendered result. If visual verification is unavailable, say so and distinguish it from helper/static checks.

Review the five together: can their typography and composition be distinguished without relying on color? Check actual font rendering/fallbacks and long titles, including mixed Chinese/Latin text when relevant. Confirm reference observations were translated into deliberate choices. Check every required material against the inventory; surface placeholders and pending permissions instead of presenting them as finished assets. Helper validation alone does not establish these qualities.

At normal viewing size, inspect the smallest meaningful text, a representative paragraph, secondary labels, input boundaries, and selected/focus states. Measure relevant foreground/background contrast, accounting for transparency and variable backgrounds; retain measured pairs/results in brief.md and label anything unmeasured. A numeric contrast pass does not excuse visually fragile strokes. Fix readability problems before presenting a direction as ready, and distinguish contrast checks from a full accessibility audit.

The gallery supports choosing a favorite and copying a follow-up request. Explain that the user must paste the copied text into this task; it does not automatically send a message or save a selected code package.

For offline HTML, provide the actual file link. When a localhost server is needed, serve only this round, bind to 127.0.0.1, use a verified free port, and start it without a visible helper window. Keep the port and URL accurate. Do not change application routes to show the demo.

Summarize A–E briefly with their reference influences and type/layout differences, link the comparison and research notes, and state outstanding material needs (or that none remain). A round with placeholders is a provisional style comparison; identify any direction whose appeal depends on unavailable artwork. Wait for the user's choice. Do not choose a winner for them.

## 6. Preserve the choice

For a clear choice such as "B", run select. It copies the whole selected variant into a new selections/<timestamp>-B-<id>/code/ directory and records source file hashes in selection.json. Preserve all originals and earlier selections.

If the user asks to combine A's layout with C's typography, build and verify the combined demo in a new round (copy the retained variants), then package the new chosen variant. Record what was combined; do not label an unchanged copy as a synthesis.

Return links to the selected code entry and selection record. Demo selection alone does not authorize application integration. Follow an explicit later integration request normally.

If selected code still uses placeholders, carry its pending material list into the handoff and keep its provisional status explicit. Choosing a variant does not itself authorize generating its missing assets.

## Project records and handoff

The round's brief/manifest owns design intent, inspected references, verification and material limits; selection.json owns the packaged selection and source hashes. Keep demos/screenshots/assets in the existing round, not project fact records. Do not duplicate a design registry in the human and Agent entrances.

After an authorized round or selection, update only affected project design decisions, blockers or next-action facts with links to that round/selection. Keep prototype created, user selected, application integrated and product verified distinct. Preserve earlier rounds; a later integration needs its own code/test evidence. A placeholder remains provisional after selection.

Follow the project's completion contract: report records updated or why none were affected, and deferred updates with impact/next step. Update entrances only when their navigation or summary changes. Read-only review writes no rounds or records. These record steps do not authorize asset generation, extra rerolls, application integration or publishing.

## Attribution

The five-variant comparison, feedback, and synthesis workflow is informed by 0xdesigner's Design Lab. This package's helper and gallery are independently authored. See [sources and licensing](references/sources.md) and the [README](README.md). Preserve those notices when distributing this skill.
