[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$ProjectRoot,
    [switch]$Plan,
    [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ($Force) { throw '-Force is no longer supported. Preview with -Plan and merge existing rules separately.' }

function Get-SafePath {
    param([string]$Root, [string]$Relative = '')
    if ($Relative -and ([IO.Path]::IsPathRooted($Relative) -or $Relative -match '(^|[\\/])\.\.([\\/]|$)')) {
        throw "Unsafe manifest path: $Relative"
    }
    $full = [IO.Path]::GetFullPath((Join-Path $Root $Relative))
    $cursor = $full
    while ($cursor) {
        if (Test-Path -LiteralPath $cursor) {
            $item = Get-Item -LiteralPath $cursor -Force
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Linked paths are not supported: $cursor" }
        }
        $cursor = Split-Path -Parent $cursor
    }
    return $full
}

$resolvedProjectRoot = Get-SafePath -Root $ProjectRoot
if (-not (Test-Path -LiteralPath $resolvedProjectRoot -PathType Container)) { throw 'ProjectRoot must be an existing directory.' }
if ($resolvedProjectRoot.TrimEnd('\', '/') -eq [IO.Path]::GetPathRoot($resolvedProjectRoot).TrimEnd('\', '/')) {
    throw 'Refusing to initialize a filesystem root.'
}
$git = Get-Command git -ErrorAction SilentlyContinue
if ($git) {
    $savedPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $gitRoot = & $git.Source -C $resolvedProjectRoot rev-parse --show-toplevel 2>$null
        $gitExit = $LASTEXITCODE
    } finally { $ErrorActionPreference = $savedPreference }
    if ($gitExit -eq 0 -and [IO.Path]::GetFullPath([string]$gitRoot).TrimEnd('\', '/') -ine $resolvedProjectRoot.TrimEnd('\', '/')) {
        throw "ProjectRoot differs from the Git root ($gitRoot). Select the intended root explicitly; no files were written."
    }
    if ($gitExit -ne 0) {
        $cursor = $resolvedProjectRoot
        while ($cursor) {
            if (Test-Path -LiteralPath (Join-Path $cursor '.git')) { throw 'Git root verification failed for this checkout; no files were written.' }
            $cursor = Split-Path -Parent $cursor
        }
    }
} else {
    $cursor = $resolvedProjectRoot
    while ($cursor) {
        if (Test-Path -LiteralPath (Join-Path $cursor '.git')) { throw 'Git is required to verify this checkout root.' }
        $cursor = Split-Path -Parent $cursor
    }
}

$sourceOffice = Get-SafePath -Root (Join-Path $PSScriptRoot '..')
$manifestPath = Get-SafePath -Root $sourceOffice -Relative 'templates/bootstrap-manifest.psd1'
$manifest = Import-PowerShellDataFile -LiteralPath $manifestPath
if ($manifest.Version -ne 1) { throw 'Unsupported bootstrap manifest version.' }
$entries = [Collections.Generic.List[object]]::new()
$destinations = @{}
foreach ($entry in $manifest.Files) {
    foreach ($relative in @($entry.Source, $entry.Target)) {
        if ($relative -match '(^|[\\/])(\.local|\.publish|\.skillbench|__pycache__|node_modules|frontend-gacha)([\\/]|$)') {
            throw "Excluded bootstrap content: $relative"
        }
    }
    $source = Get-SafePath -Root $sourceOffice -Relative $entry.Source
    $target = Get-SafePath -Root $resolvedProjectRoot -Relative $entry.Target
    if ($destinations.ContainsKey($target)) { throw "Duplicate bootstrap destination: $target" }
    $destinations[$target] = $true
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Missing bootstrap source: $source" }
    $sourceHash = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
    $targetHash = $null
    $state = 'Create'
    if (Test-Path -LiteralPath $target) {
        if (-not (Test-Path -LiteralPath $target -PathType Leaf)) { throw "Destination is not a file: $target" }
        $targetHash = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash
        if ($entry.Target -like 'office/records/*') { $state = 'PreserveRecord' }
        elseif ($targetHash -eq $sourceHash) { $state = 'Unchanged' }
        else { $state = 'ReviewRequired' }
    }
    $entries.Add([pscustomobject]@{State=$state; Source=$source; Target=$target; SourceHash=$sourceHash; TargetHash=$targetHash})
}
if ($Plan) {
    # No directory creation, logs, validators, or test execution in preview mode.
    return $entries
}
$conflicts = @($entries | Where-Object State -eq 'ReviewRequired')
if ($conflicts.Count) {
    $conflicts | ForEach-Object { Write-Warning "Review required: $($_.Target) (seed: $($_.Source))" }
    throw 'Existing governance differs from the seed. No files were written. Review -Plan and merge under separate upgrade authorization.'
}
foreach ($entry in $entries) {
    if ($entry.State -ne 'Create') { continue }
    [void](Get-SafePath -Root $resolvedProjectRoot -Relative $entry.Target.Substring($resolvedProjectRoot.TrimEnd('\', '/').Length + 1))
    [void][IO.Directory]::CreateDirectory((Split-Path -Parent $entry.Target))
    # Reject a destination created after the plan, too.
    [IO.File]::Copy($entry.Source, $entry.Target, $false)
}
# Execute only the trusted seed validator, never a preserved target script.
$validator = Get-SafePath -Root $sourceOffice -Relative 'scripts/Test-OfficeGovernance.ps1'
$valid = & $validator -ProjectRoot $resolvedProjectRoot -Quiet -NoExit
if (-not $valid) { throw "Initialization left structural gaps; inspect the validator output: $resolvedProjectRoot" }
Write-Output "Office governance structure is ready: $resolvedProjectRoot. This is not product or release validation."
