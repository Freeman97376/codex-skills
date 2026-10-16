# Office: Agent Governance Center

The root AGENTS.md delegates to office/AGENTS.md. Read both before project work.

| Location | Purpose |
| --- | --- |
| skills/manage-agent-governance/ | Governance maintenance procedure |
| scripts/ | Initialization and structural checks |
| templates/bootstrap-manifest.psd1 | Exact reusable bootstrap file list |
| records/ | Durable decisions, concise task evidence and test index |
| records/README.md | Human reading entrance |
| records/agent-index.md | Agent navigation over the same facts |
| tests/ | Isolated governance verification |

To preview initialization from a trusted seed without writing or running tests:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File 'C:\path\to\trusted-seed\office\scripts\Initialize-Office.ps1' -ProjectRoot 'C:\path\to\project' -Plan
```

After authorization, omit -Plan to fill missing files. Existing differing
governance files stop initialization before any writes. Review and merge them
separately; do not delete existing rules to make initialization pass. Records are
preserved. Optional skills are explicit dependencies, not automatically installed.
Initialization copies only generic seed files, not this project's policies,
private configuration, demonstrations or runtime evidence.
