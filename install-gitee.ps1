# install-gitee.ps1 — Windows PowerShell installer for technical-docs-fetch (via Gitee mirror)
# Usage: iwr -useb https://gitee.com/frankshi2024/technical-docs-fetch/raw/main/install-gitee.ps1 | iex

$ErrorActionPreference = "Stop"

$Repo = "https://gitee.com/frankshi2024/technical-docs-fetch.git"
$SkillDirs = @(
    "$env:USERPROFILE\.config\agents\skills\technical-docs-fetch",
    "$env:USERPROFILE\.agents\skills\technical-docs-fetch"
)
$SkillUrl = "https://gitee.com/frankshi2024/technical-docs-fetch/raw/main/skill/SKILL.md"

# Old skill dirs from previous versions (named nic2markdown)
$OldSkillDirs = @(
    "$env:USERPROFILE\.config\agents\skills\nic2markdown",
    "$env:USERPROFILE\.agents\skills\nic2markdown"
)

Write-Host "====================================="
Write-Host "  technical-docs-fetch installer (Windows)"
Write-Host "====================================="
Write-Host ""

# Check prerequisites
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] uv is required but not installed."
    Write-Host "  Install it: https://docs.astral.sh/uv/#installation"
    exit 1
}

Write-Host "[1/3] Installing technical-docs-fetch CLI (via uv tool install)..."
uv tool install "git+$Repo" --force

Write-Host ""
Write-Host "[2/3] Cleaning up old nic2markdown skill directories..."
$foundOld = $false
foreach ($oldDir in $OldSkillDirs) {
    if (Test-Path $oldDir) {
        $foundOld = $true
        Write-Host "  Found: $oldDir"
    }
}

if ($foundOld) {
    $answer = Read-Host "  Remove old nic2markdown skill directories? [y/N]"
    if ($answer -eq "y" -or $answer -eq "Y") {
        foreach ($oldDir in $OldSkillDirs) {
            if (Test-Path $oldDir) {
                Remove-Item -Recurse -Force $oldDir
                Write-Host "  Removed: $oldDir"
            }
        }
    } else {
        Write-Host "  Skipped."
    }
} else {
    Write-Host "  None found."
}

Write-Host ""
Write-Host "[3/3] Installing agent skill..."
foreach ($SkillDir in $SkillDirs) {
    New-Item -ItemType Directory -Force -Path $SkillDir | Out-Null
    Invoke-WebRequest -Uri $SkillUrl -OutFile "$SkillDir\SKILL.md"
    Write-Host "  -> $SkillDir\SKILL.md"
}

Write-Host ""
Write-Host "====================================="
Write-Host "  Installation complete!"
Write-Host "====================================="
Write-Host ""
Write-Host "Try it out:"
Write-Host "  technical-docs-fetch --help"
Write-Host "  technical-docs-fetch https://soc.ustc.edu.cn/COD/lab5/"
