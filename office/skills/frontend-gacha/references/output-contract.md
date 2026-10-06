# Output contract

Resolve SKILL_DIR from the path of this installed skill. Pass the target project's absolute root explicitly. Python 3.12+ and its standard library are sufficient.

## Commands

    python "<SKILL_DIR>/scripts/gacha.py" init --project-root "<PROJECT_ROOT>" --name reading-demo
    python "<SKILL_DIR>/scripts/gacha.py" build --project-root "<PROJECT_ROOT>" --run "office/frontend-gacha/reading-demo/round-01"
    python "<SKILL_DIR>/scripts/gacha.py" select --project-root "<PROJECT_ROOT>" --run "office/frontend-gacha/reading-demo/round-01" --variant B --note "Prefer the compact layout"

init requires a lowercase slug and allocates the next round without replacing an existing round. Use the run path it prints. build validates all required inputs before generating the gallery. select refuses incomplete rounds and copies local assets along with the entrypoint.

## Files in one round

    office/frontend-gacha/<slug>/round-01/
      brief.md
      fixture.json
      manifest.json
      index.html
      variants/
        A/index.html
        B/index.html
        C/index.html
        D/index.html
        E/index.html
      selections/<timestamp>-B-<unique-id>/
        selection.json
        code/index.html

brief.md: short product/scope description, common interactions, content rules, the five direction decisions, useful design-source identities, and verification notes. Do not paste private prompts or credentials into it.

fixture.json: common fictional example data used by every variant. Copy these values into standalone pages as needed; this file documents parity, not a required runtime request.

manifest.json (schema version 1):

    {
      "schema_version": 1,
      "title": "Reading list",
      "summary": "Compare the same reading-list interaction in five styles.",
      "variants": [
        {"id": "A", "name": "Quiet catalog", "rationale": "Grid, restrained type, and generous spacing."},
        {"id": "B", "name": "Compact console", "rationale": "Dense list, mono accents, and dark surfaces."},
        {"id": "C", "name": "Soft library", "rationale": "Warm surfaces, serif titles, and rounded controls."},
        {"id": "D", "name": "Bold blocks", "rationale": "Heavy borders, strong type, and offset shapes."},
        {"id": "E", "name": "Reading journal", "rationale": "Editorial rows, paper tones, and a personal note style."}
      ]
    }

The array must contain A–E once, in order. Names/rationales are descriptions, not executable markup; the helper escapes them. Entry paths are fixed at variants/<ID>/index.html. The example directions above demonstrate the schema, not mandatory presets.

Each variant must be independently portable: use relative links only to files within its own directory, inline tiny shared behavior, and avoid root-relative URLs or references to sibling variants. For an explicit framework demo, emit a self-contained static build here before building the gallery.

The helper rejects traversal and linked/junction paths, refuses to replace an unrelated index.html, and never deletes variants. Gallery UI selection is only a review convenience. The select command is the operation that creates the durable code package and source hashes.
