# =============================================================================
#  eesti.ai — e-etteütlus AI Competition Installer
#  Run: Right-click → Run with PowerShell (or: powershell -ExecutionPolicy Bypass -File install.ps1)
# =============================================================================

$ErrorActionPreference = "Stop"
$PROJECT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$VENV_DIR = Join-Path $PROJECT_DIR "venv"
$FFMPEG_DIR = Join-Path $PROJECT_DIR "ffmpeg"
$MODELS_DIR = Join-Path $PROJECT_DIR "models"
$PYTHON_MIN_VERSION = [version]"3.10.0"
$PYTHON_MAX_VERSION = [version]"3.13.0"

# --- Helpers ----------------------------------------------------------------

function Write-Step($msg) {
    Write-Host ""
    Write-Host "  [$([char]0x2713)] $msg" -ForegroundColor Green
}

function Write-Info($msg) {
    Write-Host "      $msg" -ForegroundColor Gray
}

function Write-Err($msg) {
    Write-Host "  [X] $msg" -ForegroundColor Red
}

function Test-Command($cmd) {
    try { Get-Command $cmd -ErrorAction Stop | Out-Null; return $true }
    catch { return $false }
}

# --- Banner -----------------------------------------------------------------

Write-Host ""
Write-Host "  ========================================" -ForegroundColor Cyan
Write-Host "    eesti.ai - e-etteytlus Setup" -ForegroundColor Cyan
Write-Host "  ========================================" -ForegroundColor Cyan
Write-Host ""

# --- Step 1: Check/Install Python ------------------------------------------

Write-Host "  [1/6] Checking Python..." -ForegroundColor Yellow

$pythonCmd = $null

# Check common locations
foreach ($cmd in @("python", "python3", "py")) {
    if (Test-Command $cmd) {
        try {
            $ver = & $cmd --version 2>&1 | Select-String -Pattern "(\d+\.\d+\.\d+)" | ForEach-Object { $_.Matches[0].Value }
            $verObj = [version]$ver
            if ($verObj -ge $PYTHON_MIN_VERSION -and $verObj -lt $PYTHON_MAX_VERSION) {
                $pythonCmd = $cmd
                Write-Step "Found $cmd $ver"
                break
            } else {
                Write-Info "Found $cmd $ver but need >= $PYTHON_MIN_VERSION and < $PYTHON_MAX_VERSION"
            }
        } catch {
            continue
        }
    }
}

if (-not $pythonCmd) {
    Write-Host "  [1/6] Python not found. Attempting install via winget..." -ForegroundColor Yellow

    if (Test-Command "winget") {
        try {
            winget install Python.Python.3.11 --accept-source-agreements --accept-package-agreements --silent
            # Refresh PATH
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

            if (Test-Command "python") {
                $pythonCmd = "python"
                Write-Step "Python installed via winget"
            } else {
                # winget installs to AppData, try to find it
                $pyPath = "$env:LOCALAPPDATA\Programs\Python\Python311"
                if (Test-Path "$pyPath\python.exe") {
                    $env:Path += ";$pyPath;$pyPath\Scripts"
                    $pythonCmd = "$pyPath\python.exe"
                    Write-Step "Python installed via winget (found at $pyPath)"
                }
            }
        } catch {
            Write-Err "winget install failed: $_"
        }
    }

    if (-not $pythonCmd) {
        Write-Err "Could not install Python automatically."
        Write-Host ""
        Write-Host "  Please install Python 3.11 manually:" -ForegroundColor White
        Write-Host "    1. Go to https://www.python.org/downloads/" -ForegroundColor White
        Write-Host "    2. Download Python 3.11.x" -ForegroundColor White
        Write-Host "    3. IMPORTANT: Check 'Add python.exe to PATH'" -ForegroundColor White
        Write-Host "    4. Run this script again" -ForegroundColor White
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# --- Step 2: Download ffmpeg ------------------------------------------------

Write-Host "  [2/6] Checking ffmpeg..." -ForegroundColor Yellow

$ffmpegExe = Join-Path $FFMPEG_DIR "ffmpeg.exe"

if (Test-Path $ffmpegExe) {
    Write-Step "ffmpeg already present"
} else {
    Write-Info "Downloading ffmpeg (this may take a minute)..."
    New-Item -ItemType Directory -Path $FFMPEG_DIR -Force | Out-Null

    $ffmpegUrl = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    $ffmpegZip = Join-Path $PROJECT_DIR "ffmpeg-temp.zip"
    $ffmpegExtract = Join-Path $PROJECT_DIR "ffmpeg-temp"

    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        # Disable progress bar — it slows Invoke-WebRequest by 10-100x in PowerShell 5.1
        $prevProgress = $ProgressPreference
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $ffmpegUrl -OutFile $ffmpegZip -UseBasicParsing
        $ProgressPreference = $prevProgress

        Expand-Archive -Path $ffmpegZip -DestinationPath $ffmpegExtract -Force

        # Find ffmpeg.exe inside extracted folder
        $found = Get-ChildItem -Path $ffmpegExtract -Recurse -Filter "ffmpeg.exe" | Select-Object -First 1
        if ($found) {
            Copy-Item $found.FullName -Destination $ffmpegExe
            # Also copy ffprobe if available
            $probe = Get-ChildItem -Path $ffmpegExtract -Recurse -Filter "ffprobe.exe" | Select-Object -First 1
            if ($probe) { Copy-Item $probe.FullName -Destination (Join-Path $FFMPEG_DIR "ffprobe.exe") }
            Write-Step "ffmpeg downloaded and extracted"
        } else {
            Write-Err "Could not find ffmpeg.exe in downloaded archive"
        }
    } catch {
        Write-Err "ffmpeg download failed: $_"
        Write-Host "  You can manually download ffmpeg from https://ffmpeg.org/download.html" -ForegroundColor White
        Write-Host "  Place ffmpeg.exe in the 'ffmpeg' folder" -ForegroundColor White
    } finally {
        Remove-Item -Path $ffmpegZip -Force -ErrorAction SilentlyContinue
        Remove-Item -Path $ffmpegExtract -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# --- Step 3: Create virtual environment -------------------------------------

Write-Host "  [3/6] Setting up Python environment..." -ForegroundColor Yellow

if (Test-Path (Join-Path $VENV_DIR "Scripts\python.exe")) {
    Write-Step "Virtual environment already exists"
} else {
    & $pythonCmd -m venv $VENV_DIR
    Write-Step "Virtual environment created"
}

$venvPython = Join-Path $VENV_DIR "Scripts\python.exe"
$venvPip = Join-Path $VENV_DIR "Scripts\pip.exe"

# --- Step 4: Install Python packages ----------------------------------------

Write-Host "  [4/6] Installing Python packages..." -ForegroundColor Yellow

# Temporarily relax error handling for native commands (pip writes to stderr even on success)
$prevEAP = $ErrorActionPreference
$ErrorActionPreference = "SilentlyContinue"

& $venvPip install --upgrade pip --quiet 2>&1 | Out-Null
& $venvPip install -r (Join-Path $PROJECT_DIR "requirements.txt") --quiet

$ErrorActionPreference = $prevEAP

if ($LASTEXITCODE -eq 0) {
    Write-Step "All packages installed"
} else {
    Write-Err "Some packages failed to install. Check output above."
    Write-Info "Try running: venv\Scripts\pip install -r requirements.txt"
}

# --- Step 5: Download Whisper model -----------------------------------------

Write-Host "  [5/6] Downloading Whisper model (this takes a few minutes on first run)..." -ForegroundColor Yellow

New-Item -ItemType Directory -Path $MODELS_DIR -Force | Out-Null

& $venvPython -c @"
import os, sys
os.environ['HF_HOME'] = os.path.join(os.path.dirname(os.path.abspath('$PROJECT_DIR')), 'eesti-ai', 'models')
try:
    from faster_whisper import WhisperModel
    model = WhisperModel('medium', device='auto', compute_type='auto',
                         download_root=r'$MODELS_DIR')
    print('Whisper medium model ready.')
except Exception as e:
    print(f'Warning: {e}', file=sys.stderr)
    print('Whisper model will download on first run.', file=sys.stderr)
"@

Write-Step "Whisper model check complete"

# --- Step 6: Verify config --------------------------------------------------

Write-Host "  [6/6] Checking configuration..." -ForegroundColor Yellow

$configFile = Join-Path $PROJECT_DIR "config.env"

if (Test-Path $configFile) {
    $config = Get-Content $configFile -Raw
    if ($config -match "YOUR_.*_KEY_HERE") {
        Write-Info "config.env exists but API key needs to be set"
        Write-Host ""
        Write-Host "  IMPORTANT: Edit config.env and set:" -ForegroundColor White
        Write-Host "    1. MODEL= (claude, gpt, grok, or gemini)" -ForegroundColor White
        Write-Host "    2. The matching API key" -ForegroundColor White
    } else {
        Write-Step "config.env looks configured"
    }
} else {
    Write-Err "config.env not found - will be created from template"
    Copy-Item (Join-Path $PROJECT_DIR "config.env.example") $configFile -ErrorAction SilentlyContinue
}

# --- Done -------------------------------------------------------------------

Write-Host ""
Write-Host "  ========================================" -ForegroundColor Green
Write-Host "    Setup complete!" -ForegroundColor Green
Write-Host "  ========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Next steps:" -ForegroundColor White
Write-Host "    1. Edit config.env with your MODEL and API key" -ForegroundColor White
Write-Host "    2. Double-click start.bat to run" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to close"
