---
name: piecewise-alignment
description: Run persistent incremental alignment in Standard one-question mode or Range grouped-question mode when explicitly invoked with /piecewise, /range, $piecewise-alignment, or a matching user request. Keep a project Office checkpoint; do not activate from complexity alone or implement while alignment is active.
---

# Piecewise Alignment

Turn a user-selected topic into a durable, reviewable agreement without starting implementation early.

## Enter and Leave the Mode

- Enter **Standard** mode when the user invokes `/piecewise` or `$piecewise-alignment`, or explicitly asks for one-question-at-a-time alignment. Enter **Range** mode when the user invokes `/range` or explicitly requests its grouped form; `/range` may start alignment directly.
- `/piecewise` or `/range off` switches an active Range session to Standard. Preserve the chosen mode until an explicit switch or exit; mode switching does not reset decisions or authorize implementation.
- Never enter because a task is complex, ambiguous, or would benefit from more planning.
- Keep the mode active until the user asks to stop, pause, finalize, implement, or switch workflows.
- Treat `implement` as leaving alignment mode. Finalize the checkpoint handoff before beginning implementation.
- Do not activate this mode for ordinary questions or planning without an explicit invocation, or for implementation requests.

## Resolve the Checkpoint

1. Resolve the real project root. Use the Git root for a checkout; otherwise use the user-selected project directory.
2. Read the active root and `office/` governance before writing. If adopted, read the project's Agent entrance and current state, then the matching checkpoint and relevant decisions/handoffs. Follow the active governance bootstrap only within its applicable authorization; report missing records during read-only work instead of creating a partial `office/` tree.
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

1. While actively eliciting decisions, Standard asks exactly one focused question per turn. Range asks one small numbered batch of similar, independent questions; do not batch decisions whose answers depend on one another. Pause/finalize/implementation handoffs need not ask another question.
2. Before asking the next question, briefly paraphrase the user's latest answer.
3. If an answer is ambiguous, state the interpretation and clarify it before dependent decisions. In Range, retain confirmed independent answers and carry unresolved items with their original numbers.
4. Keep `Confirmed`, `TBD`, and `Working assumptions` distinct.
5. In Standard, a bare yes/no applies only to the most recent unanswered question; standalone `y` or `Y` means yes only for that unambiguous yes/no item.
6. In Range, a bare `y` confirms the whole currently presented batch only when every item is an unambiguous yes/no question. Otherwise require numbered answers; do not infer choices for unanswered or open-ended items. Partial answers confirm only their identified items. An answer to an older batch never silently confirms a later one.
7. A correction supersedes the earlier interpretation. Keep one current decision and a short dated supersession note or link for material changes; do not leave incompatible decisions current or erase their durable history.
8. When the user marks a detail TBD, record it as TBD and move to the next framework-level decision.
9. Prefer structure, boundaries, and flow before numerical tuning or content polish.
10. Do not implement, prototype, or expand scope while the mode is active.

## Persist After Every Decision

After each explicit decision, update the checkpoint before asking the next question. Preserve this structure:

```markdown
---
piecewise_version: 1
status: active
mode: standard
type: governance
topic: example-topic
updated_at: 2026-08-28T12:00:00-07:00
next_question: "Exact next unanswered question."
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
- Keep `next_question` identical in the frontmatter and body. For Range, store the full numbered unanswered batch as a YAML block scalar (`next_question: |-`) and repeat the same numbered text under Next question; use `mode: range`. Keep item numbers stable while the batch is pending.
- Existing version-1 checkpoints without `mode` default to Standard unless the current user explicitly selects Range. Add the field on the next authorized update; do not bulk-migrate historical checkpoints.
- Do not store credentials, private keys, unnecessary personal data, raw chain-of-thought, or full chat transcripts.
- If persistence fails, say that the checkpoint was not saved and preserve the exact next question in the response. Do not claim a successful checkpoint update.

## Pause, Resume, and Finalize

- On pause, set `status: paused` and preserve the exact next question.
- On explicit resume, inspect `office/piecewise/` and load the matching checkpoint. If active or paused, restore its mode, paraphrase the latest confirmed state and continue with its exact unanswered question/batch. A current explicit mode command overrides the saved mode. Reactivate a finalized checkpoint only when the user actually resumes that topic; merely reading it at project startup does not reopen it.
- If multiple checkpoints plausibly match, ask one focused question to choose among them.
- On finalize, set `status: finalized` and produce a clean handoff separating Confirmed, TBD, Working assumptions, and Unresolved conflicts.
- Completion or finalization alone does not require archiving. Leave a checkpoint at its stable path while it remains valid context.
- A checkpoint is eligible for archiving only when it has been replaced, abandoned, or merged and should no longer be loaded as default context.
- When a checkpoint is eligible, ask the user for confirmation immediately before moving it to `office/piecewise/archive/<type>/<topic-slug>.md`. Never archive automatically.


## Shared facts and implementation handoff

The stable Piecewise checkpoint owns this topic's Confirmed, TBD, assumptions and unanswered questions; do not create a competing decision list in the human or Agent entrance. Confirmed means an agreed requirement or decision, not implemented, tested or deployed.

Within authorized persistence, link material accepted decisions from the existing project decision index and update only affected planned scope, blocker or next-action facts. On finalization or implementation handoff, identify the accepted scope, unresolved decisions and checkpoint path; use an existing handoff if needed rather than copying the full checkpoint. Product completion changes only after implementation evidence exists. General questions or explicit read-only requests do not write checkpoints or shared records.

At pause, finalization or implementation handoff, report the saved checkpoint and affected shared records, or the no-update reason; disclose failed/deferred persistence and its next step. Do not append a task log or rewrite both entrances after every answer. Preserve the project's current human and Agent reading levels.
