---
name: piecewise-alignment
description: Run one-question-at-a-time incremental alignment only when the user invokes /piecewise or $piecewise-alignment, or explicitly asks for piecewise alignment. Persist a living checkpoint under the project's office directory; never activate from task complexity alone or use during implementation.
---

# Piecewise Alignment

Turn a user-selected topic into a durable, reviewable agreement without starting implementation early.

## Enter and Leave the Mode

- Enter only when the user invokes `/piecewise` or `$piecewise-alignment`, or explicitly asks for one-question-at-a-time piecewise alignment.
- Never enter because a task is complex, ambiguous, or would benefit from more planning.
- Keep the mode active until the user asks to stop, pause, finalize, implement, or switch workflows.
- Treat `implement` as leaving alignment mode. Finalize the checkpoint handoff before beginning implementation.
- Do not activate this mode for ordinary questions or planning without an explicit invocation, or for implementation requests.

## Resolve the Checkpoint

1. Resolve the real project root. Use the Git root for a checkout; otherwise use the user-selected project directory.
2. Read the active root and `office/` governance before writing. If the project is missing its required governance structure, follow the active governance bootstrap instead of creating a partial `office/` tree.
3. Store the canonical checkpoint under `<project-root>/office/piecewise/<type>/<topic-slug>.md`.
4. Use one of these types:
   - `requirements` for product behavior, scope, and acceptance decisions.
   - `design` for architecture, UI, interaction, and data-shape decisions.
   - `planning` for implementation sequencing, migration, and release decisions.
   - `governance` for agent rules, skills, workflows, and operating policy.
   - `general` only when no other type clearly fits.
   Keep these as routing and storage categories within this one skill. Split a type into a separate skill only through a later skill-maintenance change after its workflow materially diverges.
5. Prefer a short, stable lowercase kebab-case topic slug. Reuse the same file for the same active topic; do not create a dated duplicate.
6. If the user names another document, treat it as a source or final deliverable unless they explicitly ask to make it the canonical checkpoint. Keep the canonical checkpoint under `office/piecewise/` by default.
7. State the resolved checkpoint path when the mode starts or resumes.

Create type folders only when first needed. Do not split Confirmed, TBD, or Working assumptions into separate files.

This version is instruction-only. Do not create helper scripts during an alignment run. Consider scripts only as a separate skill-maintenance change after repeated use demonstrates a material need for deterministic checkpoint creation, validation, or archiving.

## Maintain the Conversation

1. Ask exactly one focused question in each final response.
2. Before asking the next question, briefly paraphrase the user's latest answer.
3. If an answer is ambiguous, state the current interpretation and ask one clarification instead of advancing.
4. Keep `Confirmed`, `TBD`, and `Working assumptions` distinct.
5. A bare yes or no applies only to the most recent unanswered question.
6. When exactly one yes/no confirmation is active, treat a standalone `y` or `Y` as yes. Do not apply this shorthand inside other text or to an open-ended question.
7. A correction supersedes the earlier interpretation. Update conflicting checkpoint text rather than preserving both as current truth.
8. When the user marks a detail TBD, record it as TBD and move to the next framework-level decision.
9. Prefer structure, boundaries, and flow before numerical tuning or content polish.
10. Do not implement, prototype, or expand scope while the mode is active.

## Persist After Every Decision

After each explicit decision, update the checkpoint before asking the next question. Preserve this structure:

```markdown
---
piecewise_version: 1
status: active
type: governance
topic: example-topic
updated_at: 2026-08-28T12:00:00-07:00
next_question: "Exact next unanswered question"
---

# Example Topic

## Confirmed

- Durable decisions that the user explicitly confirmed.

## TBD

- Details intentionally deferred.

## Working assumptions

- Tentative interpretations that are not confirmed requirements.

## Unresolved conflicts

- Conflicting decisions or constraints that still need resolution.

## Next question

Exact next unanswered question.
```

- Use an ISO 8601 timestamp with the local UTC offset.
- Keep `next_question` identical in the frontmatter and body.
- Do not store credentials, private keys, unnecessary personal data, raw chain-of-thought, or full chat transcripts.
- If persistence fails, say that the checkpoint was not saved and preserve the exact next question in the response. Do not claim a successful checkpoint update.

## Pause, Resume, and Finalize

- On pause, set `status: paused` and preserve the exact next question.
- On resume, inspect `office/piecewise/` and load the matching checkpoint. If it is active or paused, paraphrase the latest confirmed state and continue with its exact next question. If it is finalized but still valid context for the same topic, reactivate and reuse it instead of creating a duplicate.
- If multiple checkpoints plausibly match, ask one focused question to choose among them.
- On finalize, set `status: finalized` and produce a clean handoff separating Confirmed, TBD, Working assumptions, and Unresolved conflicts.
- Completion or finalization alone does not require archiving. Leave a checkpoint at its stable path while it remains valid context.
- A checkpoint is eligible for archiving only when it has been replaced, abandoned, or merged and should no longer be loaded as default context.
- When a checkpoint is eligible, ask the user for confirmation immediately before moving it to `office/piecewise/archive/<type>/<topic-slug>.md`. Never archive automatically.
