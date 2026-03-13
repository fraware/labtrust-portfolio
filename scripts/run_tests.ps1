# Run tests with correct env for labtrust-portfolio (PowerShell).
# Usage: from repo root, .\scripts\run_tests.ps1
$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path (Join-Path $repoRoot "kernel"))) {
    throw "Repo root not found (expected kernel/ at $repoRoot)"
}
$env:LABTRUST_KERNEL_DIR = Join-Path $repoRoot "kernel"
$env:PYTHONPATH = Join-Path $repoRoot "impl/src"
Set-Location $repoRoot
python -m unittest discover -s tests -v
