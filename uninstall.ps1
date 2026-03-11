# =============================================================================
#  eesti.ai - Clean Uninstall (for iteration)
#  Soft: powershell -File uninstall.ps1
#  Full: powershell -File uninstall.ps1 -Full
# =============================================================================

param(
    [switch]$Full       # Also remove config.env and downloaded ffmpeg
)

$ErrorActionPreference = "Continue"
$PROJECT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "  ========================================" -ForegroundColor Yellow
Write-Host "    eesti.ai - Cleanup" -ForegroundColor Yellow
Write-Host "  ========================================" -ForegroundColor Yellow
Write-Host ""

if ($Full) {
    Write-Host "  Mode: FULL (everything except source code)" -ForegroundColor Red
} else {
    Write-Host "  Mode: SOFT (keeps config.env + ffmpeg)" -ForegroundColor Cyan
}

$confirm = Read-Host "  Continue? (y/N)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "  Cancelled."; exit 0
}

function Remove-SafeDir($path, $label) {
    if (Test-Path $path) {
        Remove-Item $path -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "  [x] Removed: $label" -ForegroundColor Green
    } else {
        Write-Host "  [-] Skipped: $label (not found)" -ForegroundColor Gray
    }
}

function Remove-SafeFile($path, $label) {
    if (Test-Path $path) {
        Remove-Item $path -Force -ErrorAction SilentlyContinue
        Write-Host "  [x] Removed: $label" -ForegroundColor Green
    } else {
        Write-Host "  [-] Skipped: $label (not found)" -ForegroundColor Gray
    }
}

Write-Host ""

# Always clean these
Remove-SafeDir  (Join-Path $PROJECT_DIR "venv")     "Python virtual environment (venv/)"
Remove-SafeDir  (Join-Path $PROJECT_DIR "models")   "Whisper models (models/)"
Remove-SafeDir  (Join-Path $PROJECT_DIR "output")   "Output files (output/)"
Remove-SafeFile (Join-Path $PROJECT_DIR "ffmpeg-temp.zip") "Temp ffmpeg archive"

# Clean __pycache__ everywhere
Get-ChildItem -Path $PROJECT_DIR -Directory -Recurse -Filter "__pycache__" -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
}
Write-Host "  [x] Removed: all __pycache__ dirs" -ForegroundColor Green

# Full mode: also nuke ffmpeg and config
if ($Full) {
    Remove-SafeDir  (Join-Path $PROJECT_DIR "ffmpeg")    "ffmpeg binaries (ffmpeg/)"
    Remove-SafeFile (Join-Path $PROJECT_DIR "config.env") "Configuration (config.env)"
}

Write-Host ""
Write-Host "  ========================================" -ForegroundColor Green
Write-Host "    Cleanup complete!" -ForegroundColor Green
Write-Host "  ========================================" -ForegroundColor Green
Write-Host ""

if (-not $Full) {
    Write-Host "  Kept: config.env, ffmpeg/, src/" -ForegroundColor Gray
    Write-Host "  To remove everything: uninstall.ps1 -Full" -ForegroundColor Gray
}

Write-Host ""
Read-Host "Press Enter to close"
