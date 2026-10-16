# Global Agent Instructions

## Mandatory Governance Bootstrap for New Projects

Whenever creating a new project or adopting an existing directory as a project, establish agent governance before substantive feature work:

1. Resolve the real project root. Use `git rev-parse --show-toplevel` for a Git checkout; otherwise use the user-selected project directory.
2. Ensure the root contains a Codex-discoverable `AGENTS.md` that delegates detailed governance to `office/README.md` and `office/AGENTS.md`.
3. Ensure `office/` contains, at minimum, `README.md`, `AGENTS.md`, `skills/`, `scripts/`, `records/`, `templates/`, and `tests/`.
4. Prefer the trusted seed initializer when it exists:

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File 'C:\path\to\trusted-seed\office\scripts\Initialize-Office.ps1' -ProjectRoot 'C:\path\to\project' -Plan
   ```

5. Preview first. Within initialization authority omit `-Plan` to copy the explicit generic whitelist. Existing differing governance files require a separately scoped merge; `-Force` is unsupported. If the seed is unavailable, create only the generic structure manually. Never overwrite or weaken existing rules or import another project's private configuration.
6. Run the generated `office/scripts/Test-OfficeGovernance.ps1` before feature work. Apply stricter project-specific rules when needed.

Use exact `AGENTS.md` casing. Keep detailed agent interaction governance in `office/`, log only durable decisions and substantial task evidence, and never store credentials or unnecessary private user content in governance records.

An explicit read-only review does not adopt or initialize a project and does not
authorize records, repairs or test execution. Follow the user's execution limits.
Do not automatically install optional skills, run model collaboration or publish.

## Change-Test Governance

After authorized implementation changes functional behavior, fixes a known error, or changes an API, schema, permission, migration, or fixed contract, use `$govern-change-tests` to analyze test impact. During implementation, relevant project-native test creation is in scope; during review or diagnosis, remain read-only and report gaps. Keep canonical test cases and known errors governed under `office/`, and keep executable product tests in their native project locations.
