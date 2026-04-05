# Dealix — محاكاة تحقق إطلاق (Launch verification)
# التشغيل من مجلد salesflow-saas:  .\scripts\launch-verify.ps1
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Py = $env:PYTHON_EXE
if (-not $Py) {
  $Py = (Get-Command python -ErrorAction SilentlyContinue).Source
  if (-not $Py) { $Py = "python" }
}

Write-Host "== Backend: pytest (full) + launch matrix ==" -ForegroundColor Cyan
Set-Location "$Root\backend"
& $Py -m pytest -q --tb=short
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Py -m pytest -q -m launch --tb=short
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "== Frontend: vitest + lint + build + Playwright ==" -ForegroundColor Cyan
Set-Location "$Root\frontend"
npm run test
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
npm run lint
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
npm run build
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
npx playwright test
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "OK — launch verification complete." -ForegroundColor Green
