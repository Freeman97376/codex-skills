[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$initializer = Join-Path $projectRoot 'office\scripts\Initialize-Office.ps1'
$validator = Join-Path $projectRoot 'office\scripts\Test-OfficeGovernance.ps1'
$powershellExe = (Get-Command powershell.exe -ErrorAction Stop).Source
$testRoot = Join-Path ([IO.Path]::GetTempPath()) ('office-governance-tests-' + [guid]::NewGuid().ToString('N'))
$failures = [Collections.Generic.List[string]]::new()

function Invoke-ScriptProcess {
    param([string]$Script, [string[]]$Arguments = @())
    $savedPreference = $ErrorActionPreference
    try {
        # Negative cases intentionally emit stderr; judge their process exit code.
        $ErrorActionPreference = 'Continue'
        & $powershellExe -NoProfile -ExecutionPolicy Bypass -File $Script @Arguments *> $null
        return $LASTEXITCODE
    } finally { $ErrorActionPreference = $savedPreference }
}
function Assert-True {
    param([bool]$Condition, [string]$Name)
    if ($Condition) { Write-Output "[PASS] $Name" }
    else { $script:failures.Add($Name); Write-Output "[FAIL] $Name" }
}
function Get-Snapshot {
    param([string]$Root)
    return ((Get-ChildItem -LiteralPath $Root -Recurse -Force | Sort-Object FullName | ForEach-Object {
        if ($_.PSIsContainer) { 'D:' + $_.FullName }
        else { $_.FullName + ':' + (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash }
    }) -join "`n")
}
function New-Fixture {
    param([string]$Name)
    $path = Join-Path $testRoot $Name
    [void][IO.Directory]::CreateDirectory($path)
    return $path
}

try {
    [void][IO.Directory]::CreateDirectory($testRoot)
    Assert-True ((Invoke-ScriptProcess $validator @('-ProjectRoot', $projectRoot)) -eq 0) 'Current seed validates'
    Assert-True ((Invoke-ScriptProcess (Join-Path $PSScriptRoot 'Test-ChangeTestGovernance.ps1')) -eq 0) 'Change-test governance self-tests pass'

    $fresh = New-Fixture 'fresh'
    $plan = @(& $initializer -ProjectRoot $fresh -Plan)
    Assert-True ($plan.Count -gt 0 -and @($plan | Where-Object State -ne 'Create').Count -eq 0) 'Preview lists missing files'
    Assert-True (@(Get-ChildItem -LiteralPath $fresh -Force).Count -eq 0) 'Preview creates no files or directories'
    Assert-True ((Invoke-ScriptProcess $initializer @('-ProjectRoot', $fresh)) -eq 0) 'Fresh initialization validates'
    $manifest = Import-PowerShellDataFile -LiteralPath (Join-Path $projectRoot 'office\templates\bootstrap-manifest.psd1')
    $expected = @($manifest.Files | ForEach-Object { $_.Target.Replace('\', '/') } | Sort-Object)
    $actual = @(Get-ChildItem -LiteralPath $fresh -File -Recurse -Force | ForEach-Object { $_.FullName.Substring($fresh.Length + 1).Replace('\', '/') } | Sort-Object)
    Assert-True (($expected -join "`n") -eq ($actual -join "`n")) 'Fresh target contains exactly the whitelist'
    $before = Get-Snapshot $fresh
    Assert-True ((Invoke-ScriptProcess $initializer @('-ProjectRoot', $fresh)) -eq 0) 'Repeated initialization succeeds'
    Assert-True ((Get-Snapshot $fresh) -ceq $before) 'Repeated initialization changes no file content'

    $ledger = Join-Path $fresh 'office\records\test-ledger.md'
    Add-Content -LiteralPath $ledger -Value '<!-- preserve custom records -->'
    $before = Get-Snapshot $fresh
    Assert-True ((Invoke-ScriptProcess $initializer @('-ProjectRoot', $fresh)) -eq 0) 'Existing records do not block initialization'
    Assert-True ((Get-Snapshot $fresh) -ceq $before) 'Existing records remain byte-identical'
    Assert-True ((Invoke-ScriptProcess $initializer @('-ProjectRoot', $fresh, '-Force')) -ne 0) 'Legacy Force is rejected'
    Assert-True ((Get-Snapshot $fresh) -ceq $before) 'Rejected Force changes nothing'

    $existing = New-Fixture 'existing-rules'
    [void][IO.Directory]::CreateDirectory((Join-Path $existing 'office'))
    Set-Content -LiteralPath (Join-Path $existing 'AGENTS.md') -Value '# Strict project rules'
    Set-Content -LiteralPath (Join-Path $existing 'office\AGENTS.md') -Value '# Strict Office rules'
    $before = Get-Snapshot $existing
    $plan = @(& $initializer -ProjectRoot $existing -Plan)
    Assert-True (@($plan | Where-Object State -eq 'ReviewRequired').Count -eq 2) 'Preview identifies both policy conflicts'
    Assert-True ((Invoke-ScriptProcess $initializer @('-ProjectRoot', $existing)) -ne 0) 'Conflicting rules stop initialization'
    Assert-True ((Get-Snapshot $existing) -ceq $before) 'Conflicts preserve all bytes and create nothing'

    # This isolated generated seed includes fake private/project data to prove exclusion.
    foreach ($path in @('office\.local\connections.json', 'office\skills\mantle-server-ops\.local\connections.json', 'office\frontend-gacha\demo.bin', 'office\scripts\__pycache__\cache.bin', 'office\records\private-run.txt', 'office\skills\unrelated\SKILL.md')) {
        $file = Join-Path $fresh $path
        [void][IO.Directory]::CreateDirectory((Split-Path -Parent $file))
        Set-Content -LiteralPath $file -Value 'synthetic exclusion sentinel'
    }
    $clean = New-Fixture 'clean-copy'
    $fixtureInitializer = Join-Path $fresh 'office\scripts\Initialize-Office.ps1'
    Assert-True ((Invoke-ScriptProcess $fixtureInitializer @('-ProjectRoot', $clean)) -eq 0) 'Generated seed remains reusable'
    $actual = @(Get-ChildItem -LiteralPath $clean -File -Recurse -Force | ForEach-Object { $_.FullName.Substring($clean.Length + 1).Replace('\', '/') } | Sort-Object)
    Assert-True (($expected -join "`n") -eq ($actual -join "`n")) 'Private profiles, demos, caches and unrelated skills are excluded'

    $brokenRef = Join-Path $clean 'office\skills\manage-agent-governance\SKILL.md'
    $original = [IO.File]::ReadAllBytes($brokenRef)
    Add-Content -LiteralPath $brokenRef -Value '[broken reference](references/missing.md)'
    Assert-True ((Invoke-ScriptProcess $validator @('-ProjectRoot', $clean)) -ne 0) 'Validator rejects a missing bundled reference'
    [IO.File]::WriteAllBytes($brokenRef, $original)
    $example = Join-Path $clean 'office\templates\global-AGENTS.md'
    $original = [IO.File]::ReadAllBytes($example)
    Add-Content -LiteralPath $example -Value ('```powershell' + "`n" + "powershell -File 'C:\broken" + "`n" + '```')
    Assert-True ((Invoke-ScriptProcess $validator @('-ProjectRoot', $clean)) -ne 0) 'Validator rejects a truncated command example'
    [IO.File]::WriteAllBytes($example, $original)
    Remove-Item -LiteralPath (Join-Path $clean 'office\records\task-log.md')
    Assert-True ((Invoke-ScriptProcess $validator @('-ProjectRoot', $clean)) -ne 0) 'Validator rejects a missing required record'

    Remove-Item -LiteralPath (Join-Path $fresh 'office\templates\root-AGENTS.template.md')
    $missingSource = New-Fixture 'missing-source-target'
    Assert-True ((Invoke-ScriptProcess $fixtureInitializer @('-ProjectRoot', $missingSource)) -ne 0) 'Missing seed file stops before copying'
    Assert-True (@(Get-ChildItem -LiteralPath $missingSource -Force).Count -eq 0) 'Missing seed file leaves target empty'

    $repo = New-Fixture 'git-project'
    & git -c init.defaultBranch=main init --quiet $repo
    if ($LASTEXITCODE -ne 0) { throw 'Cannot create isolated Git fixture.' }
    $child = Join-Path $repo 'subdirectory'
    [void][IO.Directory]::CreateDirectory($child)
    Assert-True ((Invoke-ScriptProcess $initializer @('-ProjectRoot', $child)) -ne 0) 'Git subdirectory is rejected instead of widening scope'
    Assert-True (@(Get-ChildItem -LiteralPath $child -Force).Count -eq 0) 'Git root mismatch creates nothing'

    $linked = New-Fixture 'linked-target'
    $external = New-Fixture 'link-destination'
    $junction = Join-Path $linked 'office'
    try {
        New-Item -ItemType Junction -Path $junction -Target $external | Out-Null
        Assert-True ((Invoke-ScriptProcess $initializer @('-ProjectRoot', $linked)) -ne 0) 'Target junction is rejected'
        Assert-True (@(Get-ChildItem -LiteralPath $external -Force).Count -eq 0) 'Junction destination remains untouched'
    } finally {
        if (Test-Path -LiteralPath $junction) { [IO.Directory]::Delete($junction) }
    }
}
finally {
    if (Test-Path -LiteralPath $testRoot) {
        $resolvedTestRoot = [IO.Path]::GetFullPath($testRoot)
        $tempBoundary = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
        if (-not $resolvedTestRoot.StartsWith($tempBoundary, [StringComparison]::OrdinalIgnoreCase) -or (Split-Path -Leaf $resolvedTestRoot) -notmatch '^office-governance-tests-[0-9a-f]{32}$') { throw 'Unsafe fixture cleanup path.' }
        Remove-Item -LiteralPath $resolvedTestRoot -Recurse -Force
    }
}
if ($failures.Count) { throw "$($failures.Count) governance tests failed." }
Write-Output '[PASS] All office governance tests passed.'
