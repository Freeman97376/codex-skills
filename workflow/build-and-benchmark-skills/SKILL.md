---
name: build-and-benchmark-skills
description: Create or revise focused Codex skills and evaluate them by executing a deterministic, frozen SkillBench A/B comparison under an explicit model-session budget. Use when the user wants a skill produced with empirical validation; do not use for ordinary explanations about skills.
---

# Build and Benchmark Skills

Produce the smallest skill package that changes agent behavior usefully, then measure that change with reproducible evidence instead of judging the prose in isolation.

## Resolve the Work

1. Resolve the real project root and read its applicable `AGENTS.md` and governance files. If shared records are adopted, read the Agent entrance/current state and only relevant prior evaluation/handoff evidence; a prior verdict is tied to its frozen inputs, not the current editable source.
2. Inspect existing skills, tests, and uncommitted work before choosing a destination or baseline. Preserve user-owned files.
3. Extract the requested outcome, trigger boundary, required artifacts, permission limits, and observable success criteria. Make low-risk assumptions when these are clear; ask only when a missing choice would materially change the result.
4. Read [references/skill-package.md](references/skill-package.md) before creating or substantially restructuring a skill.

## Build the Skill

- Keep the `SKILL.md` entrypoint focused on decisions another agent would not reliably infer.
- Put conditional detail in linked references, repeatable mechanics in scripts, and output material in assets only when each resource has a concrete use.
- Use the system `$skill-creator` workflow when it is available. Otherwise create the required `SKILL.md` and optional `agents/openai.yaml` manually using the package contract in the reference.
- Preserve normal implicit discovery unless the user explicitly requests explicit-only invocation.
- Scaffold every required parent directory before applying a multi-file patch. Do not depend on a patch operation to create nested directories or treat a partially applied patch as success.
- Treat supplied benchmark fixtures as opaque bytes. Copy them with `scripts/copy_fixture.py`, verify the reported hash, and never reconstruct them from terminal output or displayed text.
- Validate frontmatter, resource links, scripts, and observable behavior. Remove unfinished placeholders before evaluation.

## Maintaining this workflow

Editing this skill's instructions does not invoke its benchmark workflow on itself or authorize nested model sessions, Docker installation/builds, credentials or publication. Use proportionate static/local checks for such maintenance and label the changed instructions empirically unverified unless a separately authorized comparison actually runs. When the user requests a skill produced with empirical evaluation through this workflow, the evaluation contract below still applies.

## Require SkillBench Evaluation

A skill-production request handled by this workflow includes actual SkillBench execution by default. Creating a case, writing a plan, or running only static checks is not a completed evaluation.

After the candidate passes static validation:

1. Create a meaningful baseline, isolated fixture, and deterministic verifier.
2. Calculate and enforce the approved model-session budget.
3. Run SkillBench dry-run and freeze the exact CasePack and SkillPacks.
4. Execute at least one real baseline/candidate sentinel comparison from those frozen IDs when the effective environment satisfies the case permissions.
5. Inspect the saved verifier, token, timing, and artifact evidence with human analysis before reporting a verdict.

On Windows, when a Codex Desktop-launched nested session receives `read-only` despite requesting `workspace-write`, use the Docker launcher documented in the evaluation reference. Build, check, and dry-run are zero-session operations. The launcher must still refuse the real run until the frozen IDs and explicit two-session confirmation are supplied.

Report exactly one completion state:

- **evaluated:** both variants executed under equivalent valid conditions and produced interpretable verifier evidence;
- **blocked:** a permission, dependency, authentication, or environment failure invalidated the comparison; state that the skill is not yet empirically evaluated and do not infer a winner;
- **design-only:** the user explicitly asked not to start model sessions; deliver the case and dry-run plan without calling it an evaluation.

## Design the Benchmark

Read [references/skillbench-evaluation.md](references/skillbench-evaluation.md) for every skill-production request handled by this workflow.

1. State one narrow comparison question, such as whether the candidate preserves correctness while reducing unnecessary reads.
2. Use the same case, workspace, prompt, skill name, model, reasoning, sandbox, verifier, and external dependencies for every variant.
3. Explicitly invoke the shared skill name in the case prompt when measuring skill-body quality. Test trigger discovery separately when that is the actual question.
4. Prefer deterministic verification of outcomes and safety boundaries. Do not use an LLM judge when files, schemas, exact values, exit codes, or project-native tests can decide the result.
5. Scaffold the full case layout, write generated text and code, copy immutable fixtures byte-for-byte, and run the deterministic verifier in that order.
6. Freeze the case and skill variants with a dry run before launching model sessions. Promote the resulting immutable pack IDs to the real run.

If a command reports `Resource temporarily unavailable`, `Can't fork`, or a namespace/process-spawn failure, run at most one zero-model health probe. If the same failure class repeats, stop retrying, preserve the first and repeated errors, and report the work as blocked. Do not spend tokens on repeated patch or command attempts against an unhealthy sandbox.

## Enforce the Usage Budget

Calculate the session count before every real benchmark:

```text
benchmark sessions = cases * variants * repetitions
total model sessions = benchmark sessions + Codex analysis sessions
```

Use `scripts/plan_skillbench_budget.py` to make the calculation explicit. A dry run and human analysis use zero model sessions.

- Within a request to build and evaluate a skill, cap the default sentinel at **2 model sessions**: one case, two variants, one repetition, and human analysis.
- Do not start a real run when the calculated total exceeds the user's stated cap or the 2-session default. Ask before expanding it.
- Start with one representative case. Add repetitions only after the sentinel is valid and observed variance matters to the decision.
- Use the intended production model for a release conclusion. A cheaper model may be used for a smoke test only when the result is labeled model-specific.
- Never start nested SkillBench or Codex sessions from inside a benchmark case unless the user separately authorizes that additional budget.

## Interpret and Hand Off

- Evaluate outcome and safety before time, tokens, or estimated cost.
- Prefer human analysis of the saved comparison evidence. Use Codex analysis only when requested or when the additional model session is approved and materially useful.
- Accept a candidate only when the evidence supports the stated comparison question. Treat a one-run tie as inconclusive, not proof of equivalence.
- Never describe a generated case, dry-run, or environment-blocked comparison as a completed empirical evaluation.
- Report changed files, static validation, exact model-session count, verifier outcome, model and reasoning settings, limitations, and the next smallest useful action.


## Shared project facts and evidence boundaries

Frozen cases, SkillPacks and run/comparison evidence remain immutable evaluation sources. Keep fixtures, raw traces, caches and large generated artifacts in their existing benchmark/output locations, outside Office records and publishable skill content. Governance keeps concise IDs, hashes, environment, verdict, limitations and links; do not regenerate or copy benchmark artifacts merely to update a summary.

After an authorized build/evaluation, update affected project capability/readiness facts with the narrow result, exact frozen candidate and actual model/environment. Editing the maintained skill afterward makes that verdict historical for the new source; a sentinel result never proves broad quality or global installation/publication. Distinguish edited source, frozen candidate, evaluated result and installed/published version.

Use the target project's completion contract: update authoritative evidence first, then affected shared facts, and entrance navigation only as needed. Report updated records, no-impact reasons and deferred items with impact/next step. Read-only review writes no records; an environment-blocked run preserves failed evidence and cannot be reclassified as success to finish the task.
