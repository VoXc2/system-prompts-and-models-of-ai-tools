# Builds dealix-marketing-bundle.zip: sales_assets + presentations/dealix-2026-sectors
# Run from repo root or salesflow-saas:
#   .\salesflow-saas\scripts\package_dealix_marketing_assets.ps1
#   .\scripts\package_dealix_marketing_assets.ps1
$ErrorActionPreference = "Stop"

# ── Path Resolution ───────────────────────────────
. "$PSScriptRoot\lib\Resolve-DealixPaths.ps1"

if (-not $HasSalesAssets) {
    Write-Error "sales_assets directory not found in this layout."
}

$OutZip = Join-Path $SalesAssetsDir "dealix-marketing-bundle.zip"
$Staging = Join-Path $env:TEMP ("dealix-bundle-" + [Guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $Staging -Force | Out-Null
try {
    Copy-Item -Path $SalesAssetsDir -Destination (Join-Path $Staging "sales_assets") -Recurse -Force
    Remove-Item (Join-Path $Staging "sales_assets\dealix-marketing-bundle.zip") -Force -ErrorAction SilentlyContinue
    $PresSrc = Join-Path $ProjectRoot "presentations\dealix-2026-sectors"
    if (Test-Path $PresSrc) {
        Copy-Item -Path $PresSrc -Destination (Join-Path $Staging "presentations-dealix-2026-sectors") -Recurse -Force
    }
    if (Test-Path $OutZip) { Remove-Item $OutZip -Force }
    Compress-Archive -Path (Join-Path $Staging "*") -DestinationPath $OutZip -CompressionLevel Optimal
    Write-Host "OK: $OutZip"
    (Get-Item $OutZip).Length / 1MB | ForEach-Object { Write-Host ("Size MB: {0:N2}" -f $_) }
}
finally {
    Remove-Item -Path $Staging -Recurse -Force -ErrorAction SilentlyContinue
}
