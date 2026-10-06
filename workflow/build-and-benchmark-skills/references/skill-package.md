# Skill Package Contract

Use this reference when creating or substantially restructuring a skill.

## Required Contract

Every skill is a directory named after the skill and contains:

```text
skill-name/
|-- SKILL.md
`-- agents/
    `-- openai.yaml
```

`SKILL.md` frontmatter requires a lowercase kebab-case `name` matching the directory and a concise `description` that says both what the skill does and when it applies. Keep the frontmatter limited to supported fields.

The Markdown body should contain the purpose, decisions, invariants, authorization boundaries, and links needed for the workflow. It should not repeat generic agent capabilities or turn one fixture into a universal rule.

`agents/openai.yaml` may provide:

```yaml
interface:
  display_name: "Human-facing name"
  short_description: "Short user-facing description"
  default_prompt: "Use $skill-name to complete a representative task."
policy:
  allow_implicit_invocation: true
```

Quote string values. The default prompt must explicitly name `$skill-name`. Omit optional UI fields that have no supplied asset or concrete purpose.

## Resource Decisions

Add a resource only when it improves repeated use:

- `scripts/`: deterministic or repeatedly reimplemented mechanics. Execute new scripts during validation.
- `references/`: substantial schemas, policies, examples, or mode-specific procedures. Link each reference from `SKILL.md` and say when to read it.
- `assets/`: templates or media copied into generated output. Do not load assets as instructions by default.

Avoid placeholder directories, duplicate manuals, README files that only restate `SKILL.md`, and absolute machine-specific paths.

## Validation Bar

Before benchmarking:

1. Run the available skill structure validator.
2. Confirm there are no `TODO` or scaffold placeholders.
3. Resolve every relative resource link.
4. Execute added scripts on a disposable fixture.
5. Confirm the description routes narrowly enough to avoid unrelated requests.
6. Confirm the skill preserves user intent and requires fresh authorization before destructive or external mutations.
7. Scaffold all required parent directories before any multi-file patch, then verify that every required artifact exists.
8. For supplied fixtures that must be preserved, use `../scripts/copy_fixture.py` and confirm the source and destination SHA-256 values are identical. Never recreate fixture bytes from rendered text.
