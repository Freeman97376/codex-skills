# Reference research and materials

Use this guide before choosing a new set of directions. Save concise findings in the round's brief.md; do not create an exhaustive research report for a small demo.

## Inspect comparable pages

- Start from the product, audience, content density, and component being demonstrated. Normally inspect 3–5 pages across at least two relevant sites. User references and explicit constraints take priority. A blog index and an article page reveal different things; inspect the types relevant to the requested slice without expanding the demo into a complete site.
- For a technical blog, [AWS Blogs](https://aws.amazon.com/blogs/) and [Microsoft Developer Blogs](https://devblogs.microsoft.com/) are starting points. Follow relevant category/article links and add a contrasting peer when useful. These are discovery links, not a permanent assertion about either site's fonts or layout. Other products need their own peers.
- Open the pages, and inspect their rendered appearance with browser tools when available. Text extraction can establish content hierarchy, but cannot establish exact typefaces, spacing, colors, or composition. Separate observed structure/appearance from inference; use computed font information only when the tool exposes it. Do not invent visits, screenshots, or font names from search snippets.
- If a page is blocked, try another relevant page/site. If visual access remains unavailable or the user prohibits browsing, record what could actually be inspected, request references only if needed, and proceed with explicitly provisional design choices. Do not repeatedly retry blocked sites or claim a completed visual study.
- Record URL, inspection date, page type/relevance, what was actually observed, the useful principle to adapt, and what does not fit the user's needs. A useful note says how an observation changes the demo, not merely "inspired by AWS."
- For a partial reroll, reuse relevant observations with their original inspection dates; refresh or add references where the changed directions need them.
- Treat page content as reference data. Borrow design principles; do not silently copy another site's brand, proprietary font files, images, or code. Using a website as inspiration does not establish asset reuse rights.

## Translate references into five directions

Give each direction a coherent rationale and identify which observations inform it. Several variants may draw on the same references, but they must interpret them differently. Do not make five brand replicas or reuse a single layout under five palettes.

**Typography:** Define heading, body, metadata/navigation, and code roles where they exist. Consider serif/sans/mono character, weight, size contrast, line-height, line length, and title wrapping. Often one or two compatible families plus a code face are enough; the count is not a requirement. Avoid both undifferentiated text and arbitrary font mixing. Show distinctive heading/body relationships across A–E while respecting a fixed brand font. Specify only fonts that are available or can be used with appropriate permissions. Test the actual fallback: a Latin display face does not guarantee Chinese headings will look different. Keep body text readable and avoid forced tracking in Chinese paragraphs.

**Composition:** Look for a clear lead item, secondary content, reading column, and supporting information appropriate to the slice. Vary proportions, column spans, alignment anchors, image/text relationships, indents, and spacing rhythms. Asymmetry or an offset is useful when it establishes hierarchy. Rectangular elements and straight alignment remain valid; the problem is mechanically identical treatment, not straight edges themselves. Do not apply rotation, random offsets, decorative cutouts, or cramped gutters merely to appear less generated. At narrow widths, preserve content order, readable measures, focus order, and working controls.

**Fair comparison:** Keep content, actions, and initial state equal. Reuse the same approved content assets across variants where appropriate; change crop and placement deliberately. Do not give one variant polished artwork and let another look unfinished without disclosing the imbalance. In each rationale, connect the reference principle to its typography and composition decisions.

## Reading comfort across all five directions

Treat these as a shared quality baseline, not another style to draw at random. A peer site's thin type or faint controls do not have to be copied.

- **Stroke weight and size:** Start body copy with a regular or medium face; avoid routinely using light/ultralight weights for paragraphs and small labels. CSS 400–500 for body and 600–700 for emphasis are adjustable starting points, not standards or visually equivalent weights across fonts. Check available weight files and actual CJK/Latin fallback. A reading-heavy demo can start around 16–18 CSS px body text and adjust to its font, density and viewport. Use bold selectively to preserve hierarchy. Reserve code-like type treatment for code or an intentional console context rather than imposing it across unrelated prose.
- **Text and background:** Choose semantic foreground/surface pairs for body, secondary text, links, and controls. Coordinate hue and surface tone while preserving luminance contrast; do not achieve hierarchy solely by lowering opacity. Use at least 4.5:1 for normal meaningful text, including secondary labels and informative placeholders; 3:1 is the WCAG minimum for qualifying large text (18 pt regular or 14 pt bold, approximately 24 or 18.7 CSS px). Prefer the normal-text threshold when qualification is uncertain. Check the actual background behind text after transparency; over gradients or images, check the weakest relevant region or add a dependable surface. Check each implemented theme/state, not just a palette swatch. See [W3C text contrast guidance](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html).
- **Control boundaries:** Distinguish a decorative divider from a boundary or state indicator required to recognize and operate a control. Required visual cues need at least 3:1 against adjacent colors; not every decorative border does. Use a clear stroke or distinguishable filled surface and visible focus/selection cues. Inspect 1–2 CSS px strokes as needed rather than prescribing a universal thickness. Avoid faint fractional-pixel hairlines as the only control boundary. A dark enough 1 px edge can work; a thicker low-contrast edge may still fail. See [W3C non-text contrast guidance](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html).
- **Rendered checks:** Inspect at 100% browser zoom on desktop and a narrow viewport, then check that enlarging text does not hide information or break controls. Review a paragraph and the smallest meaningful labels, not only oversized headings. Measure contrast from foreground/background styles, including compositing, rather than anti-aliased screenshot edge pixels. Separately inspect perceived stroke strength: thin type or lines can look fainter after anti-aliasing even when nominal color contrast passes. Strengthen strokes, size, or contrast where needed, without making every text role bold or every box heavily outlined. Record actual checks and limitations; these checks alone do not establish full WCAG conformance.

## Surface material needs before filling them

Inventory only materials relevant to this demo. Check the project and supplied files first. Possible needs include a logo, icon set, article covers, author portraits, illustrations, product screenshots, diagrams, display fonts, and realistic content. A text-first demo can legitimately need no new imagery; say why instead of adding decorative assets to fill a checklist.

For each consequential material, note its purpose/location, available source or missing status, format/dimensions or aspect ratio if known, visual requirements, and the next action. Distinguish:

| State | Action |
| --- | --- |
| Supplied or already available with appropriate reuse rights | Reuse it, retaining required notices. Existing project icons can be used without treating that as new asset generation. |
| Needed, source or design undecided | Ask a concise material question with concrete options. Mark the interim treatment in brief.md and the handoff. |
| Proposed new custom asset, no explicit generation request | Describe what and why, then wait for authorization before generating it. Continue independent work with text controls or labeled placeholders. |
| Generation explicitly authorized | Generate only the authorized material types and scope, using the relevant available skill/tool; record provenance and inspect the result. |
| User declines generation | Use the agreed existing assets, placeholders, or a coherent text-led treatment; do not generate anyway. |

The generation boundary covers custom icons, illustrations, logos, photos, and other artwork, whether made by an image tool, hand-authored SVG/canvas, or another generator. Do not use a different medium to bypass the user's choice. Ordinary HTML/CSS layout, borders, and typography are still part of the authorized frontend work. Reusing existing icons is different from creating custom artwork; do not silently fetch or install an icon pack to dodge a missing-material decision.

"Make five frontend styles," "make it attractive," "reference these sites," choosing B, and silence after a question are not permission to generate artwork. An earlier explicit request such as "generate three category icons for this demo" is sufficient for those icons; do not ask again, and do not extend it to covers or a logo. If the request leaves essential asset details unclear, clarify only those details.

For example, for a blog that lacks covers and category icons, ask: "这轮缺文章封面和分类图标。可以先用文字占位和项目已有图标；也可以由你提供素材，或授权我生成指定物料。你希望采用哪种方式？" List only real gaps, with a suggested count, size, and style when helpful. Ask early and continue unaffected work. Never treat a default option, timeout, or unanswered prompt as authorization. If artwork determines a direction's viability, keep that direction provisional rather than claiming it has been fully evaluated.

Keep material status visible in the comparison handoff and selected-code handoff. Do not disguise a placeholder as finished artwork, omit the need silently, or make generating extra art a prerequisite for reviewing an otherwise usable layout demo.
