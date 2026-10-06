[CmdletBinding()]
param(
    [ValidateSet("Check", "Build", "DryRun", "Run", "Analyze")]
    [string]$Mode = "Check",

    [string]$ImageName = "codex-skillbench:0.1.0-codex-0.146.0",

    [string]$Model = "gpt-5.6-luna",

    [ValidateSet("low", "medium", "high", "xhigh", "max", "ultra")]
    [string]$Reasoning = "medium",

    [string]$CasePackId,

    [string]$BaselineSkillPackId,

    [string]$CandidateSkillPackId,

    [string]$ComparisonId,

    [ValidateRange(0, 2)]
    [int]$ConfirmModelSessions = 0
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$dockerContext = (Resolve-Path (Join-Path $PSScriptRoot "..\docker")).Path
$dockerfile = Join-Path $dockerContext "Dockerfile"
$seccompProfile = Join-Path $dockerContext "seccomp-codex-sandbox.json"
$expectedSeccompSha256 = "d7101c1e039436f05158bfd2b7848d298b57814522cbd70ae19c87f9af441f60"
$authFile = Join-Path $env:USERPROFILE ".codex\auth.json"

$casePath = "benchmarks/build-and-benchmark-skills/case.json"
$baselinePath = "benchmarks/build-and-benchmark-skills/variants/baseline"
$candidatePath = "workflow/build-and-benchmark-skills"
$budgetScript = "workflow/build-and-benchmark-skills/scripts/plan_skillbench_budget.py"

function Assert-CommandSucceeded {
    param([string]$Operation)

    if ($LASTEXITCODE -ne 0) {
        throw "$Operation failed with exit code $LASTEXITCODE."
    }
}

function Assert-DockerEngine {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        throw "Docker CLI is not installed or is not on PATH."
    }

    & docker version --format "client={{.Client.Version}} server={{.Server.Version}}"
    Assert-CommandSucceeded "Docker engine check"
}

function Assert-ImageExists {
    & docker image inspect $ImageName *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker image '$ImageName' is missing. Run this script with -Mode Build first."
    }
}

function Assert-AuthFile {
    if (-not (Test-Path -LiteralPath $authFile -PathType Leaf)) {
        throw "Codex auth file was not found. Run codex login on the host before a real benchmark."
    }
}

function Assert-FrozenId {
    param(
        [string]$Value,
        [string]$Prefix,
        [string]$Label
    )

    if ([string]::IsNullOrWhiteSpace($Value) -or $Value -notmatch "^${Prefix}[A-Z0-9]+$") {
        throw "$Label must be a frozen ${Prefix} ID from the approved dry run."
    }
}

function Assert-SeccompProfile {
    if (-not (Test-Path -LiteralPath $seccompProfile -PathType Leaf)) {
        throw "Pinned Codex sandbox seccomp profile is missing: $seccompProfile"
    }

    $actualSha256 = (Get-FileHash -LiteralPath $seccompProfile -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualSha256 -ne $expectedSeccompSha256) {
        throw "Pinned Codex sandbox seccomp profile hash mismatch. Expected $expectedSeccompSha256 but found $actualSha256."
    }
}

function Invoke-Container {
    param(
        [string[]]$Command,
        [switch]$MountAuth
    )

    Assert-SeccompProfile

    $dockerArguments = @(
        "run",
        "--rm",
        "--security-opt", "no-new-privileges:true",
        "--security-opt", "seccomp=$seccompProfile",
        "--cap-drop", "ALL",
        "--pids-limit", "256",
        "--cpus", "2",
        "--memory", "4g",
        "--mount", "type=bind,source=$projectRoot,target=/workspace",
        "--workdir", "/workspace"
    )

    if ($MountAuth) {
        Assert-AuthFile
        $dockerArguments += @(
            "--mount", "type=bind,source=$authFile,target=/run/codex-auth/auth.json,readonly",
            "--env", "SKILLBENCH_AUTH_HOME=/run/codex-auth"
        )
    }

    $dockerArguments += $ImageName
    $dockerArguments += $Command

    & docker @dockerArguments
    Assert-CommandSucceeded "Docker SkillBench command"
}

function Assert-CodexSandbox {
    $probeScript = @'
set -eu
probe=$(mktemp /workspace/.codex-sandbox-preflight.XXXXXX)
cleanup() { rm -f $probe; }
trap cleanup EXIT
printf codex-sandbox-ok >$probe
test -s $probe
    printf codex-sandbox-ok
'@
    Invoke-Container -Command @(
        "codex", "sandbox", "-c", 'sandbox_mode="workspace-write"',
        "sh", "-lc", $probeScript
    )
}

if ($Mode -eq "Run" -and $ConfirmModelSessions -ne 2) {
    throw "Real benchmark blocked. Re-run with -ConfirmModelSessions 2 only after approving exactly two model sessions."
}

Assert-DockerEngine

if ($Mode -eq "Build") {
    & docker build --pull --file $dockerfile --tag $ImageName $dockerContext
    Assert-CommandSucceeded "Docker image build"
    Write-Output "Built $ImageName. No model session was started."
    exit 0
}

Assert-ImageExists

if ($Mode -eq "Check") {
    Assert-AuthFile
    Invoke-Container -Command @(
        "sh", "-lc",
        "codex --version && skillbench --version && git --version && python --version"
    )
    Assert-CodexSandbox
    Write-Output "Environment check passed. No model session was started."
    exit 0
}

if ($Mode -eq "DryRun") {
    Invoke-Container -Command @(
        "python3", $budgetScript,
        "--cases", "1",
        "--variants", "2",
        "--runs", "1",
        "--max-sessions", "2",
        "--json"
    )
    Invoke-Container -Command @(
        "skillbench", "bench", $casePath,
        "--variant", "baseline=$baselinePath",
        "--variant", "candidate=$candidatePath",
        "--runs", "1",
        "--model", $Model,
        "--reasoning", $Reasoning,
        "--sandbox", "workspace-write",
        "--dry-run",
        "--offline",
        "--root", "."
    )
    Write-Output "Dry run completed. No model session was started."
    exit 0
}

if ($Mode -eq "Run") {
    Assert-FrozenId -Value $CasePackId -Prefix "cpk_" -Label "CasePackId"
    Assert-FrozenId -Value $BaselineSkillPackId -Prefix "spk_" -Label "BaselineSkillPackId"
    Assert-FrozenId -Value $CandidateSkillPackId -Prefix "spk_" -Label "CandidateSkillPackId"
    Assert-CodexSandbox

    Invoke-Container -Command @(
        "python3", $budgetScript,
        "--cases", "1",
        "--variants", "2",
        "--runs", "1",
        "--max-sessions", "2",
        "--json"
    )
    Invoke-Container -MountAuth -Command @(
        "skillbench", "bench", $CasePackId,
        "--variant", "baseline=$BaselineSkillPackId",
        "--variant", "candidate=$CandidateSkillPackId",
        "--runs", "1",
        "--model", $Model,
        "--reasoning", $Reasoning,
        "--sandbox", "workspace-write",
        "--offline",
        "--root", "."
    )
    exit 0
}

if ($Mode -eq "Analyze") {
    Assert-FrozenId -Value $ComparisonId -Prefix "cmp_" -Label "ComparisonId"
    Invoke-Container -Command @(
        "skillbench", "analyze", $ComparisonId,
        "--by", "human",
        "--root", "."
    )
    Write-Output "Human analysis bundle created. No model session was started."
    exit 0
}

throw "Unsupported mode: $Mode"
