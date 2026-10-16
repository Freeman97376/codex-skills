# Office Governance Test Cases

The self-tests are derived regression coverage for the maintained scripts, not
separately user-confirmed canonical acceptance cases. They verify:

1. Required seed structure, manifest sources/targets, skill frontmatter and script syntax.
2. Read-only preview reports missing files and conflicts without creating files or directories.
3. Fresh initialization creates exactly the explicit whitelist; the generated seed can initialize another project.
4. Repeated initialization changes no file bytes; custom record content remains intact.
5. Differing root and Office policies block all writes; legacy `-Force` is rejected.
6. Synthetic private connection profiles, unrelated skills, demos, records and caches never enter the copied seed.
7. Missing references, missing records and truncated PowerShell examples fail validation.
8. Missing source files stop copying before any target changes.
9. Git subdirectories are rejected rather than silently widening the selected root.
10. Target directory junctions are rejected and their destinations remain untouched.
11. Existing change-test self-tests cover confirmation, regression evidence, stale invalidation and manual waiver rules.

The suite creates a synthetic Git repository and directory junction inside its
GUID-named OS temporary directory. No network, installation, provider call or
other project is involved. It verifies the absolute cleanup boundary and removes
the junction before recursively removing its own fixture root. Sandboxes must
permit these local fixture operations; a denial is not a passing test.

This proves local structural and helper behavior only. Agent instruction compliance,
product correctness, live model review and release readiness require their own evidence.
