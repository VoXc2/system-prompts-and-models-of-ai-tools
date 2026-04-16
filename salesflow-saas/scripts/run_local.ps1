<#
  Run Dealix locally: backend (8000) + frontend (3000) in new windows.
  Requires: Python 3 with deps, Node.js, npm install in frontend.
#>

# ── Path Resolution ───────────────────────────────
. "$PSScriptRoot\lib\Resolve-DealixPaths.ps1"

if (-not $HasBackend) { throw "Backend folder not found. Cannot start Dealix." }

Write-Host "Starting backend: uvicorn app.main:app --reload --port 8000" -ForegroundColor Cyan
Start-Process powershell -WorkingDirectory $BackendDir -ArgumentList @(
  "-NoExit", "-Command",
  "`$env:PYTHONIOENCODING='utf-8'; py -3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
)

if ($HasFrontend) {
  Write-Host "Starting frontend: npm run dev (port 3000)" -ForegroundColor Cyan
  Start-Process powershell -WorkingDirectory $FrontendDir -ArgumentList @(
    "-NoExit", "-Command", "npm run dev"
  )
} else {
  Write-Host "[SKIP] Frontend not found. Only backend will be started." -ForegroundColor Yellow
}

Write-Host "`nURLs:" -ForegroundColor Green
Write-Host "  API docs: http://127.0.0.1:8000/api/docs"
Write-Host "  Health:   http://127.0.0.1:8000/api/v1/health"
if ($HasFrontend) {
  Write-Host "  Frontend: http://localhost:3000"
}
