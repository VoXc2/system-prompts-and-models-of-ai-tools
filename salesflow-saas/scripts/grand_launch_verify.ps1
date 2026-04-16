# Dealix grand launch: backend pytest, frontend lint + build, optional HTTP checks (API must be up).
# Run from salesflow-saas (this file lives in scripts\):
#   .\scripts\grand_launch_verify.ps1
#   .\scripts\grand_launch_verify.ps1 -HttpCheck -SoftReady
# Or from repo root: .\salesflow-saas\verify-launch.ps1 -HttpCheck
# From salesflow-saas\frontend: ..\scripts\grand_launch_verify.ps1 -HttpCheck
#
# -HttpOnly : only hit the API (py scripts/full_stack_launch_test.py --http-only); skips pytest/lint/build.
# -BaseUrl : sets DEALIX_BASE_URL for HTTP phase (e.g. http://127.0.0.1:8001 when 8000 runs an old build).

param(
    [switch]$HttpCheck,
    [switch]$SoftReady,
    [switch]$HttpOnly,
    [string]$BaseUrl = ""
)

$ErrorActionPreference = "Stop"

# ── Path Resolution ───────────────────────────────
. "$PSScriptRoot\lib\Resolve-DealixPaths.ps1"
$root = $ProjectRoot
$backend = $BackendDir
$frontend = $FrontendDir

if ($BaseUrl -ne "") {
    $env:DEALIX_BASE_URL = $BaseUrl.TrimEnd("/")
    Write-Host "Using DEALIX_BASE_URL=$($env:DEALIX_BASE_URL)" -ForegroundColor DarkGray
}

if (-not $HasBackend) {
    Write-Host "[SKIP] Backend not found in this layout." -ForegroundColor Yellow
    if ($HttpOnly -or $HttpCheck) {
        Write-Host "FAIL: Backend required for HTTP checks." -ForegroundColor Red
        exit 1
    }
}

if ($HttpOnly) {
    Write-Host "Dealix root: $root" -ForegroundColor DarkGray
    Write-Host "== HTTP only (API must be running on `$env:DEALIX_BASE_URL or http://127.0.0.1:8000) ==" -ForegroundColor Cyan
    Push-Location $backend
    try {
        $pyArgs = @("scripts/full_stack_launch_test.py", "--http-only")
        if ($SoftReady) { $pyArgs += "--soft-ready" }
        & py @pyArgs
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    } finally {
        Pop-Location
    }
    Write-Host "HTTP-only verify OK." -ForegroundColor Green
    exit 0
}

Write-Host "Dealix root: $root" -ForegroundColor DarkGray

if ($HasBackend) {
    Write-Host "== Backend: pytest ==" -ForegroundColor Cyan
    Push-Location $backend
    try {
        & py -m pytest tests -q --tb=line
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    } finally {
        Pop-Location
    }
} else {
    Write-Host "== Backend: SKIPPED (not found) ==" -ForegroundColor Yellow
}

Write-Host "== Sync marketing -> frontend/public ==" -ForegroundColor Cyan
Push-Location $root
try {
    & node scripts/sync-marketing-to-public.cjs
    if ($LASTEXITCODE -ne 0) { Write-Host "[WARN] marketing sync failed" -ForegroundColor Yellow }
} finally {
    Pop-Location
}

if ($HasFrontend) {
    Write-Host "== Frontend: lint ==" -ForegroundColor Cyan
    Push-Location $frontend
    try {
        & npm run lint
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        Write-Host "== Frontend: build ==" -ForegroundColor Cyan
        & npm run build
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    } finally {
        Pop-Location
    }
} else {
    Write-Host "== Frontend: SKIPPED (not found) ==" -ForegroundColor Yellow
}

if ($HttpCheck) {
    if (-not $HasBackend) {
        Write-Host "FAIL: Backend required for HTTP checks." -ForegroundColor Red
        exit 1
    }
    Write-Host "== HTTP: full_stack_launch_test ==" -ForegroundColor Cyan
    Push-Location $backend
    try {
        $pyArgs = @("scripts/full_stack_launch_test.py")
        if ($SoftReady) { $pyArgs += "--soft-ready" }
        Write-Host 'Hint: cd backend; py -m uvicorn app.main:app --host 127.0.0.1 --port 8000' -ForegroundColor DarkGray
        & py @pyArgs
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    } finally {
        Pop-Location
    }
} else {
    Write-Host 'Skip HTTP. To verify API: .\scripts\grand_launch_verify.ps1 -HttpCheck' -ForegroundColor Yellow
}

Write-Host "Grand launch verify OK." -ForegroundColor Green
