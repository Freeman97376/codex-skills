[CmdletBinding()]
param(
    [Parameter()]
    [string]$ProjectRoot = (Get-Location).Path,

    [Parameter()]
    [switch]$Quiet,

    [Parameter()]
    [switch]$NoExit
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$resolvedRoot = [System.IO.Path]::GetFullPath($ProjectRoot).TrimEnd([System.IO.Path]::DirectorySeparatorChar)
$failures = [System.Collections.Generic.List[string]]::new()

function Add-Failure {
    param([Parameter(Mandatory)][string]$Message)
    $script:failures.Add($Message)
}

$requiredFiles = @(
    'AGENTS.md',
    'office\README.md',
    'office\AGENTS.md',
    'office\skills\manage-agent-governance\SKILL.md',
    'office\skills\manage-agent-governance\agents\openai.yaml',
    'office\scripts\Initialize-Office.ps1',
    'office\scripts\Test-OfficeGovernance.ps1',
    'office\scripts\Test-ChangeTestGovernance.ps1',
    'office\records\decision-log.md',
    'office\records\task-log.md',
    'office\records\test-ledger.md',
    'office\templates\decision-log.template.md',
    'office\templates\task-log.template.md',
    'office\templates\test-ledger.template.md',
    'office\templates\test-case.template.md',
    'office\templates\known-error.template.md',
    'office\templates\global-AGENTS.md',
    'office\templates\bootstrap-manifest.psd1',
    'office\templates\root-AGENTS.template.md',
    'office\templates\office-AGENTS.template.md',
    'office\templates\office-README.template.md',
    'office\skills\manage-agent-governance\references\maintenance.md',
    'office\tests\cases.md',
    'office\tests\Test-OfficeGovernance.ps1',
    'office\tests\Test-ChangeTestGovernance.ps1'
)

foreach ($relativePath in $requiredFiles) {
    $fullPath = Join-Path $resolvedRoot $relativePath
    if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
        Add-Failure "Missing required file: $relativePath"
    }
}

$rootAgents = Join-Path $resolvedRoot 'AGENTS.md'
if (Test-Path -LiteralPath $rootAgents -PathType Leaf) {
    $rootContent = Get-Content -LiteralPath $rootAgents -Raw
    foreach ($requiredText in @('office/README.md', 'office/AGENTS.md', '<!-- office-governance:start -->', '<!-- office-governance:end -->')) {
        if ($rootContent -notlike "*$requiredText*") {
            Add-Failure "Root AGENTS.md does not contain: $requiredText"
        }
    }
}

$officeAgents = Join-Path $resolvedRoot 'office\AGENTS.md'
if (Test-Path -LiteralPath $officeAgents -PathType Leaf) {
    $officeContent = Get-Content -LiteralPath $officeAgents -Raw
    if ($officeContent -notmatch '<!-- test-governance:start -->' -or $officeContent -notmatch '<!-- test-governance:end -->') {
        Add-Failure 'Office AGENTS.md is missing the change-test governance block.'
    }
}

function Test-ContainedFile {
    param([string]$Base, [string]$Relative)
    if ([IO.Path]::IsPathRooted($Relative)) { return $false }
    $path = [IO.Path]::GetFullPath((Join-Path $Base $Relative))
    if (-not $path.StartsWith($resolvedRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { return $false }
    $cursor = $path
    while ($cursor) {
        if (Test-Path -LiteralPath $cursor) {
            if ((Get-Item -LiteralPath $cursor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { return $false }
        }
        $cursor = Split-Path -Parent $cursor
    }
    return (Test-Path -LiteralPath $path -PathType Leaf)
}

$manifestPath = Join-Path $resolvedRoot 'office\templates\bootstrap-manifest.psd1'
if (Test-Path -LiteralPath $manifestPath -PathType Leaf) {
    try {
        $manifest = Import-PowerShellDataFile -LiteralPath $manifestPath
        if ($manifest.Version -ne 1) { Add-Failure 'Unsupported bootstrap manifest version.' }
        $targets = @{}
        foreach ($entry in $manifest.Files) {
            $targetKey = $entry.Target.Replace('\', '/').ToLowerInvariant()
            if ($targets.ContainsKey($targetKey)) { Add-Failure "Duplicate bootstrap destination: $targetKey" }
            $targets[$targetKey] = $true
            foreach ($relative in @($entry.Source, $entry.Target)) {
                if ($relative -match '(^|[\\/])(\.\.|\.local|\.publish|\.skillbench|__pycache__|node_modules|frontend-gacha)([\\/]|$)') {
                    Add-Failure "Excluded bootstrap path: $relative"
                }
            }
            if (-not (Test-ContainedFile -Base (Join-Path $resolvedRoot 'office') -Relative $entry.Source)) {
                Add-Failure "Missing or unsafe bootstrap source: $($entry.Source)"
            }
            if (-not (Test-ContainedFile -Base $resolvedRoot -Relative $entry.Target)) {
                Add-Failure "Missing or unsafe bootstrap target: $($entry.Target)"
            }
        }
    } catch { Add-Failure "Invalid bootstrap manifest: $($_.Exception.Message)" }
}

# Validate bundled references and executable examples, not arbitrary external links.
$packageDocs = @(
    'office/skills/manage-agent-governance/SKILL.md',
    'office/skills/manage-agent-governance/references/maintenance.md',
    'office/skills/manage-agent-governance/references/records.md',
    'office/records/README.md',
    'office/records/agent-index.md',
    'office/records/overview.md',
    'office/records/current-state.md',
    'office/records/architecture/overview.md',
    'office/templates/global-AGENTS.md',
    'office/templates/office-README.template.md'
)
foreach ($relative in $packageDocs) {
    $doc = Join-Path $resolvedRoot $relative
    if (-not (Test-ContainedFile -Base $resolvedRoot -Relative $relative)) { continue }
    $body = Get-Content -LiteralPath $doc -Raw
    foreach ($link in [regex]::Matches($body, '\]\(([^)]+)\)')) {
        $href = $link.Groups[1].Value
        if ($href -match '^(?:[a-zA-Z][a-zA-Z0-9+.-]*:|#)') { continue }
        $href = ($href -split '#', 2)[0]
        if (-not (Test-ContainedFile -Base (Split-Path -Parent $doc) -Relative $href)) {
            Add-Failure "Broken or unsafe local reference in ${relative}: $href"
        }
    }
    foreach ($block in [regex]::Matches($body, '(?s)```powershell\s*\r?\n(.*?)```')) {
        $exampleTokens = $null
        $exampleErrors = $null
        [void][Management.Automation.Language.Parser]::ParseInput($block.Groups[1].Value, [ref]$exampleTokens, [ref]$exampleErrors)
        foreach ($parseError in $exampleErrors) { Add-Failure "Invalid PowerShell example in ${relative}: $($parseError.Message)" }
    }
}

$misCasedAgents = Get-ChildItem -LiteralPath $resolvedRoot -File -ErrorAction SilentlyContinue | Where-Object {
    $_.Name -ieq 'AGENTS.md' -and $_.Name -cne 'AGENTS.md'
}
foreach ($file in $misCasedAgents) {
    Add-Failure "Use exact AGENTS.md casing instead of: $($file.Name)"
}

$skillFile = Join-Path $resolvedRoot 'office\skills\manage-agent-governance\SKILL.md'
if (Test-Path -LiteralPath $skillFile -PathType Leaf) {
    $skillContent = Get-Content -LiteralPath $skillFile -Raw
    if ($skillContent -notmatch '(?s)^---\s*\r?\nname:\s*manage-agent-governance\s*\r?\ndescription:\s*\S.+?\r?\n---') {
        Add-Failure 'Skill frontmatter must contain a valid name and non-empty description.'
    }
    if ($skillContent -match '\[TODO') {
        Add-Failure 'Skill contains unresolved TODO placeholders.'
    }
}

$scriptDirectory = Join-Path $resolvedRoot 'office\scripts'
$testDirectory = Join-Path $resolvedRoot 'office\tests'
$powerShellFiles = @()
if (Test-Path -LiteralPath $scriptDirectory -PathType Container) {
    $powerShellFiles += Get-ChildItem -LiteralPath $scriptDirectory -Filter '*.ps1' -File
}
if (Test-Path -LiteralPath $testDirectory -PathType Container) {
    $powerShellFiles += Get-ChildItem -LiteralPath $testDirectory -Filter '*.ps1' -File
}
foreach ($file in $powerShellFiles) {
    $tokens = $null
    $parseErrors = $null
    [void][System.Management.Automation.Language.Parser]::ParseFile($file.FullName, [ref]$tokens, [ref]$parseErrors)
    foreach ($parseError in $parseErrors) {
        Add-Failure "PowerShell parse error in $($file.Name): $($parseError.Message)"
    }
}

$changeTestValidator = Join-Path $PSScriptRoot 'Test-ChangeTestGovernance.ps1'
if (Test-Path -LiteralPath $changeTestValidator -PathType Leaf) {
    try {
        $changeTestValid = & $changeTestValidator -ProjectRoot $resolvedRoot -Quiet -NoExit
        if (-not $changeTestValid) {
            Add-Failure 'Change-test governance validation failed.'
        }
    } catch {
        Add-Failure "Change-test governance validation errored: $($_.Exception.Message)"
    }
}

$valid = $failures.Count -eq 0
if (-not $Quiet) {
    if ($valid) {
        Write-Output "[PASS] Office governance structure is valid: $resolvedRoot"
    } else {
        foreach ($failure in $failures) {
            Write-Output "[FAIL] $failure"
        }
        Write-Output "[FAIL] Office governance structure has $($failures.Count) error(s)."
    }
}

if ($NoExit) {
    return $valid
}
if ($valid) {
    exit 0
}
exit 1
