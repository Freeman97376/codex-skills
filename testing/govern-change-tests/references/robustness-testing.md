# Robustness and Confusing-Input Tests

Use this workflow for requested fuzzing, malformed or confusing inputs (including 混淆输入 / 混肴输入), or a changed input boundary with a concrete regression risk. During read-only review, propose the target, families, oracle, and coverage gaps without generating files or executing a campaign.

## Select the target and the expected behavior

Start from a real input entry point and small synthetic examples shaped like its current contract. Keep at least one valid baseline. Choose relevant families instead of testing every endpoint indiscriminately:

| Family | Useful mutations | Contract to check |
| --- | --- | --- |
| Boundary | Empty values, actual minimum/maximum and adjacent values, long text, numeric precision edges | Correct acceptance/rejection; no silent truncation or overflow |
| Structure | Missing/extra fields, wrong types, duplicates, reordered collections | Schema and required-field behavior; data integrity |
| Unicode/confusion | Zero-width characters, fullwidth text, confusable letters, combining marks, direction markers | The documented normalization, identity, search, or validation policy |
| Noise | Typos, irrelevant text, repetition, punctuation, control characters | Validation, parsing, and error handling |
| Syntax/transport | Truncated JSON, trailing junk/comma, duplicate keys, invalid encoding | Raw parser and transport contract |
| Domain/semantic | Contradictory dates or units, conflicting requirements, ambiguous text | Defined business rules or clarification behavior |

For every selected family, establish an **oracle**: the assertion that decides whether the application behaved correctly. Use the existing specification, confirmed cases, and observable contract; do not infer correctness from the implementation being tested.

- An invalid input may correctly return a validation error. Rejection is not automatically a bug.
- Assert observable results and side effects: returned value/error, saved state, permission boundary, and bounded execution where relevant. “Did not crash” alone is insufficient for a functional claim.
- A transformation may preserve meaning only if the contract says so. Do not require fullwidth/confusable identifiers to compare equal, remove zero-width characters globally, or weaken validation just to make tests pass.
- When the intended semantics are unresolved, report a characterization result and propose a draft expectation. Do not label a disputed business outcome a failure or promote it to confirmed.
- Derive actual size, numeric, and date boundaries from the target. The generic helper's values are starting points, not a complete boundary analysis.

## Generate with the native framework or the bundled helper

Prefer the project's existing property-based generators, fuzz harness, fixtures, and shrinkers when they fit. Otherwise, use the dependency-free Python helper to create a deterministic corpus, then connect it to project-native tests.

From the target project's root, save synthetic seeds in its normal test-fixture area. The outer array is a list of seed inputs; testing an array input requires an additional array layer.

Example seed file:

~~~json
[
  {"name": "cafe", "count": 1, "tags": ["sample"]},
  "cafe\u0301"
]
~~~

Run with the actual path of the loaded skill (replace <skill-dir>):

~~~text
python "<skill-dir>/scripts/generate_input_cases.py" --input tests/fixtures/robustness-seeds.json --output tests/fixtures/robustness-corpus.json --seed 20260915 --max-cases 100 --max-input-bytes 8192
~~~

Use --families boundary,structure,unicode,noise,syntax to select a subset. Defaults are all five families, seed 0, 100 total cases including baselines, and 8192 bytes per input. The helper:

- Mutates root and nested JSON values and field names; keeps originals unchanged and includes unique baseline inputs.
- Samples deterministic noise using the recorded seed; deduplicates by transport and payload, and interleaves seeds/families within the case budget.
- Records generator version/hash, Python version, source hash, limits, count, skipped oversized candidates, and whether the candidate pool or case budget ended the run. Same input bytes, options, generator, and Python version produce identical output bytes.
- Accepts 1–32 seed values in a UTF-8 JSON file up to 1 MiB, with at most 32 nesting levels. Case limits are 1–1000 and input-byte limits 32–65536. It rejects oversized seeds and skips oversized mutations. A small budget can omit nested paths or entire categories; inspect actual coverage.
- Writes a new file only; existing output files are preserved. Use a new output path for another corpus.

The output is an object with metadata and a cases array. Each case contains id, seed_index, family, mutation, path, transport, and input. path identifies the original subtree being mutated; inspect changed keys/items within that subtree when needed.

**The transport field matters:**

- json_value: pass input directly to an in-process validator, or serialize it exactly once for a JSON endpoint.
- raw_json: input is the literal malformed or unusual request body. Pass it directly to the raw parser/body interface; JSON-encoding it again would test a valid string instead. Duplicate keys and null bytes are preserved this way.

The byte cap is measured on canonical ASCII-escaped JSON for json_value and UTF-8 bytes for raw_json. Invisible characters in the corpus are escaped; preserve decoded code points in the fixture and show escapes when reporting findings.

The helper generates candidate inputs only. It neither calls the target nor assigns expected/pass/fail outcomes. It does not generate domain contradictions, binary invalid UTF-8, stateful/concurrent sequences, or domain-specific security payloads; add these only where the target contract and task call for them. For AI text targets, create synthetic ambiguous/conflicting examples and apply the project's explicit evaluation criteria; use the existing authority rules for external model calls.

## Execute a bounded campaign

1. Add a project-native adapter/test that selects the appropriate target and oracle for each chosen family and transport. Do not send raw_json cases to a typed function or blindly apply one exact expected value to the entire corpus.
2. Start with valid baselines and deterministic boundary cases, then run generated cases with recorded seed and limits. Set a finite case budget, target-call timeout, total duration, and failure/sample limit appropriate to the harness. The generator's size budget does not bound target execution time.
3. Keep execution local and isolated using project fixtures, mocks, and rollback/reset between stateful cases as needed. Retain the existing task's authority boundary for paid calls, production data, and external services.
4. Capture counts actually attempted, passed, failed, skipped, and timed out, plus the command, environment, code fingerprint, generator/corpus hash, seed, and limits. Generation success is not a test pass. A budget-ended campaign does not prove exhaustive coverage.

## Reproduce, reduce, and retain failures

For each distinct failing behavior:

1. Save the exact original failing input/bytes with its case ID, transport, seed, generator version/hash, oracle, failure signature, and replay command in the project's normal test-fixture or test-artifact area. Preserve invisible characters and byte encoding; use synthetic/redacted examples that still reproduce.
2. Replay that exact input independently against the same code/environment. If it does not recur, report intermittent or unreproduced evidence; do not mark the error reproduced from an unverified suspicion.
3. Use the native framework's shrinking facility first. Otherwise attempt bounded reductions (remove fields/items/text spans, shorten repetitions, move numbers toward simpler values). Re-run the same oracle after every candidate reduction and accept only reductions that preserve the same failure signature. Record the reduction budget and stop at its limit. Keep the original and reduced samples separately; call the result a reduced reproducer, not a globally minimal input unless proven.
4. Add the reduced reproducer as a deterministic regression test; retain generation as additional exploration. Future regression replay should use the saved fixture and not depend on rediscovering it randomly.
5. Link durable errors through [known-error-lifecycle.md](known-error-lifecycle.md) and governed cases through [test-case-schema.md](test-case-schema.md). Keep the existing confirmation, versioning, actual-execution, and stale-evidence rules.

If reduction is unavailable, retain the original reproducible input and state the limitation. The bundled helper does not implement an application-specific runner or reducer; implement these with the target's native harness.

## Handoff

Report the target and input families, oracle source, generated versus executed counts, seed and budgets, command and actual outcome, fixture/regression links, remaining coverage gaps, and evidence level. Put concise references in Office records; keep the corpus, raw bodies, and executable tests in the project's native test area.
