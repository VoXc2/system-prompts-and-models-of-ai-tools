# Builds dealix-marketing-bundle.zip — same layout as frontend/public:
#   dealix-marketing/  (from sales_assets)
#   dealix-presentations/  (from presentations/dealix-2026-sectors)
# So links like ../dealix-presentations/ work after extract (and on Next.js).
# Run from repo:  .\salesflow-saas\scripts\package_dealix_marketing_assets.ps1
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$SaaS = Join-Path $Root "salesflow-saas"
$SrcMarketing = Join-Path $SaaS "sales_assets"
if (-not (Test-Path $SrcMarketing)) {
    Write-Error "Expected sales_assets under $SaaS"
}
$OutZip = Join-Path $SrcMarketing "dealix-marketing-bundle.zip"
$Staging = Join-Path $env:TEMP ("dealix-bundle-" + [Guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $Staging -Force | Out-Null
try {
    $Dm = Join-Path $Staging "dealix-marketing"
    Copy-Item -Path $SrcMarketing -Destination $Dm -Recurse -Force
    Remove-Item (Join-Path $Dm "dealix-marketing-bundle.zip") -Force -ErrorAction SilentlyContinue
    $PresSrc = Join-Path $SaaS "presentations\dealix-2026-sectors"
    if (Test-Path $PresSrc) {
        Copy-Item -Path $PresSrc -Destination (Join-Path $Staging "dealix-presentations") -Recurse -Force
    } else {
        Write-Warning "Missing: $PresSrc (zip will omit dealix-presentations)"
    }
    $Readme = @"
بعد فك الضغط:
- افتح dealix-marketing/index.html في المتصفح (يعمل محلياً بدون خادم إذا بقي dealix-presentations بجانب dealix-marketing).
- لا تنقل مجلداً واحداً فقط؛ الروابط بين المجلدين نسبية.
- عبر Next.js: npm run dev ثم http://localhost:3000/dealix-marketing/
"@
    Set-Content -Path (Join-Path $Staging "README-AR.txt") -Value $Readme -Encoding UTF8
    if (Test-Path $OutZip) { Remove-Item $OutZip -Force }
    Compress-Archive -Path (Join-Path $Staging "*") -DestinationPath $OutZip -CompressionLevel Optimal
    Write-Host "OK: $OutZip"
    (Get-Item $OutZip).Length / 1MB | ForEach-Object { Write-Host ("Size MB: {0:N2}" -f $_) }
}
finally {
    Remove-Item -Path $Staging -Recurse -Force -ErrorAction SilentlyContinue
}
