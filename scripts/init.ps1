$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$InstallDir = Join-Path $env:APPDATA "autoconfigoscli"
$RepoDir = Join-Path $InstallDir "repo"
$VenvDir = Join-Path $InstallDir "venv"
$BinDir = Join-Path $env:LOCALAPPDATA "CoreUtils\bin"
$Launcher = Join-Path $BinDir "autoconfigoscli.cmd"

Write-Host "AutoConfigOSCLI Installer"

New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $InstallDir "data") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $InstallDir "logs") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $InstallDir "backups") | Out-Null

if (Test-Path $RepoDir) { Remove-Item -Recurse -Force $RepoDir }
Copy-Item -Recurse -Force $RepoRoot $RepoDir

if (-not (Test-Path (Join-Path $VenvDir "Scripts\python.exe"))) {
    python -m venv $VenvDir
}

$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
& $VenvPython -m pip install -r (Join-Path $RepoDir "requirements.txt") --upgrade --quiet

New-Item -ItemType Directory -Force -Path $BinDir | Out-Null
@"
@echo off
set "PYTHONPATH=$RepoDir"
"$VenvPython" -m autoconfigoscli.cli %*
"@ | Set-Content -Path $Launcher -Encoding ASCII

Write-Host "Installation complete."
Write-Host "Launcher installed at $Launcher"
