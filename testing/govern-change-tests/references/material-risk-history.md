# Materials, Risk Coverage, and Error History

Read this reference for real-document suites, repeated failures, multi-layer changes, or a requested repair plan. Extend existing project records; do not build a parallel test registry. A small local change does not require a full material inventory or broad suite.

## Material identity and roles

For real inputs record a stable material ID, private locator, SHA256, format, project/package, issuer or subject, document role, relevant section roles, revision, and original/derived relationship. Distinguish inspected, inferred, user-confirmed, and unresolved assignments.

- Confirm roles from cover/body and project context; filenames, folders, quoted requirements, and part numbers are clues, not authority. A response may contain buyer templates or multiple sections without becoming a requirements document.
- Role confirmation does not establish authenticity, completeness, or applicability. Record uncertainty about procurement round, effective version, or subject separately.
- Assemble each case from an explicit requirements version and response set for one subject/package. Do not combine different bidders or revision variants to manufacture completeness. Joint submissions need their own confirmed scope.
- Hash-deduplicate copies without collapsing distinct revisions. Archive membership is not a new test execution; unresolved archived inputs remain unverified. Count materials, unique content, scenarios, assertions, and executed cases separately.
- Keep originals read-only. Make authorized derivatives in isolated storage; record exact mutations, allowed changes, preserved content, and pre/post hashes. Keep private originals, text, images, and DB dumps outside governance and commits.
- Record unsupported format, absent text, OCR/partial parsing, unavailable source, and hash mismatch as limitations or explicit gate failures. They are not proof of missing business evidence.

## Coverage matrix

Link each material risk to the observable contract, current evidence, relevant historical error, case ID, executable path/command, test layer, affected producer/consumer/persistence/UI paths, expected result source, and remaining gap.

Use distinct evidence labels: code-inferred risk, directly reproduced behavior, historical execution, current execution, user manual acceptance, and unverified live/provider behavior. Do not convert a code risk into a reproduced incident.

Cover combinations that can defeat an otherwise passing check: source selection after conflict detection, different response revisions, unrelated subjects in one project, truncated scope after retrieval, save/reload, and failed model fallback. Choose combinations from concrete contracts rather than an exhaustive Cartesian product.

Useful contract tests include transformations whose expected invariants are explicit:
- Change source order or presentation budget without changing an existing conflict or business uncertainty.
- Duplicate a document without increasing distinct-document evidence.
- Change an authorized scope or revision and prevent reuse of the old assessment/cache.
- Keep an alternate valid source while removing one occurrence; absence must not be inferred from a single location.

Use malformed/confusing/fuzz tests through robustness-testing.md. Do not assume a generated corpus covers domain logic, concurrency, binary parsing, or all material layouts.

## Historical errors and reasons

Use known-error-lifecycle.md for each error record. Maintain a concise history index when repeated errors or a multi-error repair requires comparison. Keep current summaries easy to find and dated observations append-only.

For each substantial event record:
- observation date, candidate/environment, symptom and trigger;
- product defect, test/fixture defect, environment/provider failure, or documentation/evidence defect;
- observed cause and certainty (confirmed, inferred, unknown), evidence, and disproved explanations;
- attempted action and its rationale, actual outcome and side effects, follow-up, linked case/run, and prevention mechanism;
- local, CI, production and manual status separately; historical pass vs current freshness separately.

Explain causality, not only chronology. Separate the upstream trigger from why the system accepted or concealed it. Do not claim a particular change caused an old incident from commit titles or timing alone.

When a later trace corrects a hypothesis, append the correction and link the earlier claim. Do not erase failed runs, blame a product for a fixture failure, count reruns as extra independent coverage, or generalize a narrow pass into complete business accuracy. If record header and historical body disagree, identify the latest authoritative checkpoint and state that older wording is historical.

## Repair planning and discussion

Build the plan from the matrix and error history; use repair-plan-template.md for a substantial plan.

- Separate reproduced defects needing repair, risks needing a probe first, historically fixed cases needing renewal, and deferred architecture work.
- Prefer shared invariants and scope/state fixes over filenames, fixed pages, or test-specific vocabulary. Include producers, consumers, persisted results, old-result compatibility, affected tests, rollback and remaining limits.
- Discuss unresolved behavior, scope, data contracts, external-model use, OCR/format support, and rollout choices with the human before implementing dependent changes. Prior authorization still applies; do not repeatedly ask about settled decisions. If the user explicitly reserves implementation details for discussion, keep product changes pending while completing the concrete plan and authorized skill/record work.
- Name only skills relevant to each phase. Skill invocation does not authorize paid calls, external review, production access, deployment, or additional agent delegation. Independent review and release procedures are conditional on explicit user scope and their own requirements.
- State cost/call/time limits and stop conditions for proposed provider or broad exploratory runs; preserve uncertainty when limits are reached.

## Summary and evidence

For real-material or multi-risk work use test-summary-template.md. Update the existing project summary and link it from the ledger, rather than repeatedly adding disconnected reports. Choose a new dated report only when the scope/identity differs materially.

Record actual command, candidate/fingerprint, material/fixture hash, environment, timestamp, executed counts, failures/skips/timeouts, and scope limits for each run. Keep pre-fix/post-fix evidence separate. An inventory check, corpus generation, grammar check, or skill validation is not a product test pass. A prior full-suite run before final changes is a prior run; report the final delta tests separately.

Known errors require their linked deterministic regression to pass before verified. If affected content changes, invalidate matching prior evidence and renew only the checks actually executed. A new untested combination is a gap even when nearby tests remain valid. Formal business golds require human-confirmed purpose/process/expected result; model suggestions and syntactic validity never establish business facts.
