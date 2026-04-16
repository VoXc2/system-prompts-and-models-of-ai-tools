# Dealix — shared path resolution library (PowerShell).
# Dot-source from any script:  . "$PSScriptRoot\lib\Resolve-DealixPaths.ps1"
#
# Exports:
#   $RepoRoot, $ProjectRoot,
#   $BackendDir, $FrontendDir, $SalesAssetsDir,
#   $HasBackend, $HasFrontend, $HasSalesAssets  ($true | $false)
#   function Require-Component($Name) — returns $true or prints warning + $false

# ── 1. Repository root ────────────────────────────
$RepoRoot = (git rev-parse --show-toplevel 2>$null)
if (-not $RepoRoot) { $RepoRoot = $PWD.Path }

# ── 2. Project root detection ─────────────────────
$ProjectRoot = $null
$_candidates = @(
    (Join-Path $RepoRoot "salesflow-saas"),
    $RepoRoot
)
foreach ($_c in $_candidates) {
    if (Test-Path (Join-Path $_c "CLAUDE.md")) {
        $ProjectRoot = $_c
        break
    }
    if ((Test-Path (Join-Path $_c "docker-compose.yml")) -and (Test-Path (Join-Path $_c "backend"))) {
        $ProjectRoot = $_c
        break
    }
}
if (-not $ProjectRoot) {
    Write-Warning "Could not detect Dealix project root. Falling back to repo root."
    $ProjectRoot = $RepoRoot
}

# ── 3. Component detection ────────────────────────
function _Detect-Dir {
    param([string[]]$Candidates)
    foreach ($p in $Candidates) {
        if (Test-Path $p -PathType Container) { return $p }
    }
    return $null
}

$BackendDir = _Detect-Dir @(
    (Join-Path $ProjectRoot "backend"),
    (Join-Path $RepoRoot "backend")
)
$HasBackend = [bool]$BackendDir

$FrontendDir = _Detect-Dir @(
    (Join-Path $ProjectRoot "frontend"),
    (Join-Path $RepoRoot "frontend")
)
$HasFrontend = [bool]$FrontendDir

$SalesAssetsDir = _Detect-Dir @(
    (Join-Path $ProjectRoot "sales_assets"),
    (Join-Path $RepoRoot "sales_assets"),
    (Join-Path $RepoRoot "salesflow-saas" "sales_assets")
)
$HasSalesAssets = [bool]$SalesAssetsDir

# ── 4. Helper: require a component or skip ────────
function Require-Component {
    param([string]$Name)
    $varName = "Has$Name"
    $val = Get-Variable -Name $varName -ValueOnly -ErrorAction SilentlyContinue
    if (-not $val) {
        Write-Host "[SKIP] $Name not found in this layout." -ForegroundColor Yellow
        return $false
    }
    return $true
}
