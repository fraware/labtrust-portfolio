# Run cross-cutting workflow: thin-slice, load-profile, check-conformance, release (PowerShell).
# Usage: from repo root, .\scripts\run_workflow.ps1 [run_id] [release_id]
# Default run_id=demo, release_id=my_release
$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path (Join-Path $repoRoot "kernel"))) {
    throw "Repo root not found (expected kernel/ at $repoRoot)"
}
$env:LABTRUST_KERNEL_DIR = Join-Path $repoRoot "kernel"
$env:PYTHONPATH = Join-Path $repoRoot "impl/src"
Set-Location $repoRoot

$runId = if ($args[0]) { $args[0] } else { "demo" }
$releaseId = if ($args[1]) { $args[1] } else { "my_release" }
$runDir = "datasets/runs/$runId"

Write-Host "Run thin-slice -> $runDir"
python -m labtrust_portfolio run-thinslice --out-dir $runDir
Write-Host "Load profile"
python -m labtrust_portfolio load-profile
Write-Host "Check conformance"
python -m labtrust_portfolio check-conformance $runDir
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "Release dataset -> datasets/releases/$releaseId"
python -m labtrust_portfolio release-dataset $runDir $releaseId
Write-Host "Done."
