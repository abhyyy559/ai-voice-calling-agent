# scripts/dev-local.ps1 - one-command local stack launcher (Windows, NO Docker).
#
# Starts (skipping anything already listening):
#   1. LiveKit server      tools\livekit\livekit-server.exe   :7880
#   2. FastAPI backend     uvicorn app.main:app               :8000  (SQLite)
#   3. Voice-agent worker  python agent.py dev                (LiveKit worker)
#   4. React frontend      npm run dev                        :3000
#
# Then polls http://127.0.0.1:8000/api/health (max 60s) and prints a URL
# cheat-sheet. Logs land in <repo>\logs\. PowerShell 5.1 compatible.
#
# Usage:  powershell -ExecutionPolicy Bypass -File scripts\dev-local.ps1

$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
$LogsDir  = Join-Path $RepoRoot 'logs'
$RootEnv  = Join-Path $RepoRoot '.env'

$BackendDir    = Join-Path $RepoRoot 'backend'
$BackendVenvPy = Join-Path $BackendDir '.venv\Scripts\python.exe'
$BackendEnv    = Join-Path $BackendDir '.env'

$WorkerDir    = Join-Path $RepoRoot 'voice-agent'
$WorkerVenvPy = Join-Path $WorkerDir '.venv\Scripts\python.exe'

$LiveKitExe = Join-Path $RepoRoot 'tools\livekit\livekit-server.exe'

$FrontendDir      = Join-Path $RepoRoot 'frontend'
$FrontendNodeMods = Join-Path $FrontendDir 'node_modules'

function Test-PortListening {
    param([int]$Port)
    try {
        $conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop
        return ($null -ne $conn)
    } catch {
        return $false
    }
}

function Get-DotEnvValue {
    param([string]$Path, [string]$Key)
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    foreach ($line in Get-Content -LiteralPath $Path) {
        $trimmed = $line.Trim()
        if ($trimmed.StartsWith('#')) { continue }
        $idx = $trimmed.IndexOf('=')
        if ($idx -lt 1) { continue }
        $k = $trimmed.Substring(0, $idx).Trim()
        if ($k -eq $Key) { return $trimmed.Substring($idx + 1).Trim() }
    }
    return $null
}

function Test-WorkerRunning {
    # The worker dials OUT to LiveKit, so there is no port to probe; look for
    # a python process whose command line is running agent.py in dev mode.
    try {
        $procs = Get-CimInstance Win32_Process -Filter "Name LIKE 'python%'" -ErrorAction Stop
        foreach ($p in $procs) {
            if ($p.CommandLine -and $p.CommandLine -match 'agent\.py' -and $p.CommandLine -match '\sdev\b') {
                return $true
            }
        }
    } catch { }
    return $false
}

function Write-Step {
    param([string]$Message)
    Write-Host "==> $Message" -ForegroundColor Cyan
}

if (-not (Test-Path -LiteralPath $RootEnv)) {
    Write-Host "ERROR: root .env not found at $RootEnv - create it from .env.example first." -ForegroundColor Red
    exit 1
}
New-Item -ItemType Directory -Force -Path $LogsDir | Out-Null

# ---------------------------------------------------------------------------
# 1. backend\.env (copy from root .env, force SQLite database URL)
# ---------------------------------------------------------------------------
Write-Step 'Ensuring backend\.env (SQLite)'
if (Test-Path -LiteralPath $BackendEnv) {
    Write-Host '    backend\.env already exists - leaving it untouched.'
} else {
    Copy-Item -LiteralPath $RootEnv -Destination $BackendEnv
    $lines  = Get-Content -LiteralPath $BackendEnv
    $found  = $false
    $output = New-Object System.Collections.Generic.List[string]
    foreach ($line in $lines) {
        if ($line -match '^DATABASE_URL=') {
            $found = $true
            $output.Add('DATABASE_URL=sqlite:///./voice_agent.db')
        } else {
            $output.Add($line)
        }
    }
    if (-not $found) {
        $output.Add('DATABASE_URL=sqlite:///./voice_agent.db')
    }
    Set-Content -LiteralPath $BackendEnv -Value $output
    Write-Host '    created backend\.env from root .env with DATABASE_URL=sqlite:///./voice_agent.db'
}

# ---------------------------------------------------------------------------
# 2. LiveKit server (:7880)
# ---------------------------------------------------------------------------
if (Test-PortListening -Port 7880) {
    Write-Step 'LiveKit :7880 already listening - skipping'
} elseif (-not (Test-Path -LiteralPath $LiveKitExe)) {
    Write-Host "WARN: livekit-server.exe not found at $LiveKitExe - skipping LiveKit (playground will not connect)." -ForegroundColor Yellow
} else {
    Write-Step 'Starting LiveKit server on :7880'
    $lkKey    = Get-DotEnvValue -Path $RootEnv -Key 'LIVEKIT_API_KEY'
    $lkSecret = Get-DotEnvValue -Path $RootEnv -Key 'LIVEKIT_API_SECRET'
    if ([string]::IsNullOrEmpty($lkKey) -or [string]::IsNullOrEmpty($lkSecret)) {
        Write-Host 'WARN: LIVEKIT_API_KEY / LIVEKIT_API_SECRET missing from root .env - skipping LiveKit.' -ForegroundColor Yellow
    } else {
        # PS 5.1 joins Start-Process ArgumentList with spaces WITHOUT quoting,
        # so the quotes around the space-separated key:secret pair are embedded
        # manually: --keys="devkey: s3cret"
        $keysArg = '--keys="' + $lkKey + ': ' + $lkSecret + '"'
        Start-Process -FilePath $LiveKitExe `
            -ArgumentList @('--bind', '0.0.0.0', $keysArg) `
            -WorkingDirectory $RepoRoot `
            -WindowStyle Hidden `
            -RedirectStandardOutput (Join-Path $LogsDir 'livekit_out.log') `
            -RedirectStandardError  (Join-Path $LogsDir 'livekit_err.log')
        Write-Host '    started (logs\livekit_out.log)'
    }
}

# ---------------------------------------------------------------------------
# 3. Backend uvicorn (:8000)
# ---------------------------------------------------------------------------
if (Test-PortListening -Port 8000) {
    Write-Step 'Backend :8000 already listening - skipping'
} elseif (-not (Test-Path -LiteralPath $BackendVenvPy)) {
    Write-Host "ERROR: backend venv python not found at $BackendVenvPy" -ForegroundColor Red
    exit 1
} else {
    Write-Step 'Starting backend uvicorn app.main:app on :8000'
    Start-Process -FilePath $BackendVenvPy `
        -ArgumentList @('-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000') `
        -WorkingDirectory $BackendDir `
        -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $LogsDir 'backend_out.log') `
        -RedirectStandardError  (Join-Path $LogsDir 'backend_err.log')
    Write-Host '    started (logs\backend_out.log)'
}

# ---------------------------------------------------------------------------
# 4. Voice-agent worker (LiveKit agent process)
# ---------------------------------------------------------------------------
if (-not (Test-Path -LiteralPath $WorkerVenvPy)) {
    Write-Host "INFO: voice-agent venv not found ($WorkerVenvPy) - skipping worker." -ForegroundColor Yellow
} elseif (Test-WorkerRunning) {
    Write-Step 'Voice-agent worker already running - skipping'
} else {
    Write-Step 'Starting voice-agent worker (agent.py dev)'
    # The worker walks up from its config module looking for the nearest .env,
    # so starting it with cwd=voice-agent picks up the ROOT .env credentials.
    Start-Process -FilePath $WorkerVenvPy `
        -ArgumentList @('agent.py', 'dev') `
        -WorkingDirectory $WorkerDir `
        -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $RepoRoot 'worker_out.log') `
        -RedirectStandardError  (Join-Path $RepoRoot 'worker_err.log')
    Write-Host '    started (worker_out.log)'
}

# ---------------------------------------------------------------------------
# 5. Frontend vite dev server (:3000)
# ---------------------------------------------------------------------------
if (Test-PortListening -Port 3000) {
    Write-Step 'Frontend :3000 already listening - skipping'
} elseif (-not (Test-Path -LiteralPath (Join-Path $FrontendNodeMods '.package-lock.json')) -and -not (Test-Path -LiteralPath (Join-Path $FrontendNodeMods 'vite'))) {
    Write-Host "INFO: frontend\node_modules not found - run 'npm install' in frontend\ first to enable this." -ForegroundColor Yellow
} else {
    Write-Step 'Starting frontend npm run dev on :3000'
    Start-Process -FilePath 'cmd.exe' `
        -ArgumentList @('/c', 'npm run dev') `
        -WorkingDirectory $FrontendDir `
        -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $LogsDir 'frontend_out.log') `
        -RedirectStandardError  (Join-Path $LogsDir 'frontend_err.log')
    Write-Host '    started (logs\frontend_out.log)'
}

# ---------------------------------------------------------------------------
# 6. Wait for backend health (max ~60s)
# ---------------------------------------------------------------------------
Write-Step 'Waiting for http://127.0.0.1:8000/api/health'
$healthy = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $resp = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/health' -UseBasicParsing -TimeoutSec 3
        if ($resp.StatusCode -eq 200) {
            $healthy = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 2
    }
}
if ($healthy) {
    Write-Host '    backend is healthy.' -ForegroundColor Green
} else {
    Write-Host '    WARNING: backend did not become healthy within 60s - check logs\backend_err.log.' -ForegroundColor Yellow
}

# ---------------------------------------------------------------------------
# 7. Cheat-sheet
# ---------------------------------------------------------------------------
Write-Host ''
Write-Host '================ LOCAL STACK CHEAT-SHEET ================' -ForegroundColor Magenta
Write-Host '  App (admin UI):   http://localhost:3000'
Write-Host '  API docs:         http://127.0.0.1:8000/docs'
Write-Host '  Health check:     http://127.0.0.1:8000/api/health'
Write-Host '  Dev login:        demo@example.com / demo1234'
Write-Host '  Logs:             logs\*.log (+ worker_out.log in repo root)'
Write-Host '==========================================================' -ForegroundColor Magenta
