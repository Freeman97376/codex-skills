@{
    Version = 1
    # Exact files only. Sources are relative to office/; targets to the project root.
    Files = @(
        @{ Source = 'skills/manage-agent-governance/references/records.md'; Target = 'office/skills/manage-agent-governance/references/records.md' }
        @{ Source = 'templates/records-human.template.md'; Target = 'office/templates/records-human.template.md' }
        @{ Source = 'templates/records-agent.template.md'; Target = 'office/templates/records-agent.template.md' }
        @{ Source = 'templates/records-overview.template.md'; Target = 'office/templates/records-overview.template.md' }
        @{ Source = 'templates/records-state.template.md'; Target = 'office/templates/records-state.template.md' }
        @{ Source = 'templates/records-architecture.template.md'; Target = 'office/templates/records-architecture.template.md' }
        @{ Source = 'templates/record-change.template.md'; Target = 'office/templates/record-change.template.md' }
        @{ Source = 'templates/record-handoff.template.md'; Target = 'office/templates/record-handoff.template.md' }
        @{ Source = 'templates/records-human.template.md'; Target = 'office/records/README.md' }
        @{ Source = 'templates/records-agent.template.md'; Target = 'office/records/agent-index.md' }
        @{ Source = 'templates/records-overview.template.md'; Target = 'office/records/overview.md' }
        @{ Source = 'templates/records-state.template.md'; Target = 'office/records/current-state.md' }
        @{ Source = 'templates/records-architecture.template.md'; Target = 'office/records/architecture/overview.md' }
        @{ Source = 'templates/root-AGENTS.template.md'; Target = 'AGENTS.md' }
        @{ Source = 'templates/office-AGENTS.template.md'; Target = 'office/AGENTS.md' }
        @{ Source = 'templates/office-README.template.md'; Target = 'office/README.md' }
        @{ Source = 'skills/manage-agent-governance/SKILL.md'; Target = 'office/skills/manage-agent-governance/SKILL.md' }
        @{ Source = 'skills/manage-agent-governance/agents/openai.yaml'; Target = 'office/skills/manage-agent-governance/agents/openai.yaml' }
        @{ Source = 'skills/manage-agent-governance/references/maintenance.md'; Target = 'office/skills/manage-agent-governance/references/maintenance.md' }
        @{ Source = 'scripts/Initialize-Office.ps1'; Target = 'office/scripts/Initialize-Office.ps1' }
        @{ Source = 'scripts/Test-OfficeGovernance.ps1'; Target = 'office/scripts/Test-OfficeGovernance.ps1' }
        @{ Source = 'scripts/Test-ChangeTestGovernance.ps1'; Target = 'office/scripts/Test-ChangeTestGovernance.ps1' }
        @{ Source = 'tests/Test-OfficeGovernance.ps1'; Target = 'office/tests/Test-OfficeGovernance.ps1' }
        @{ Source = 'tests/Test-ChangeTestGovernance.ps1'; Target = 'office/tests/Test-ChangeTestGovernance.ps1' }
        @{ Source = 'tests/cases.md'; Target = 'office/tests/cases.md' }
        @{ Source = 'templates/bootstrap-manifest.psd1'; Target = 'office/templates/bootstrap-manifest.psd1' }
        @{ Source = 'templates/root-AGENTS.template.md'; Target = 'office/templates/root-AGENTS.template.md' }
        @{ Source = 'templates/office-AGENTS.template.md'; Target = 'office/templates/office-AGENTS.template.md' }
        @{ Source = 'templates/office-README.template.md'; Target = 'office/templates/office-README.template.md' }
        @{ Source = 'templates/global-AGENTS.md'; Target = 'office/templates/global-AGENTS.md' }
        @{ Source = 'templates/decision-log.template.md'; Target = 'office/templates/decision-log.template.md' }
        @{ Source = 'templates/task-log.template.md'; Target = 'office/templates/task-log.template.md' }
        @{ Source = 'templates/test-ledger.template.md'; Target = 'office/templates/test-ledger.template.md' }
        @{ Source = 'templates/test-case.template.md'; Target = 'office/templates/test-case.template.md' }
        @{ Source = 'templates/known-error.template.md'; Target = 'office/templates/known-error.template.md' }
        @{ Source = 'templates/decision-log.template.md'; Target = 'office/records/decision-log.md' }
        @{ Source = 'templates/task-log.template.md'; Target = 'office/records/task-log.md' }
        @{ Source = 'templates/test-ledger.template.md'; Target = 'office/records/test-ledger.md' }
    )
}
