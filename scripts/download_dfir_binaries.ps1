# =========================================================================
# download_dfir_binaries.ps1 - DFIR 핵심 도구(Hayabusa, Chainsaw, EZ-Tools) 원클릭 다운로더
# Bring-your-own-binary: LazyForensic에 바이너리 미포함, 별도 다운로드 래퍼
# 다운로드 후 SHA256 수동 검증 필요. 자동 검증/SBOM 미제공.
# =========================================================================

param(
    [string]$TargetDir = "$PSScriptRoot\..\tools\bin",
    [switch]$VerifyHash
)

$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

if (!(Test-Path $TargetDir)) {
    New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  LazyForensic DFIR Binary Setup (Windows x64)" -ForegroundColor Cyan
Write-Host "  Target Directory: $TargetDir" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Hayabusa (Yamato Security)
Write-Host "`n[1/3] Checking Hayabusa (Fast EVTX Sigma Threat Hunter)..." -ForegroundColor Yellow
$HayabusaExe = Join-Path $TargetDir "hayabusa.exe"
if (Test-Path $HayabusaExe) {
    Write-Host "  [✓] Hayabusa already exists at $HayabusaExe" -ForegroundColor Green
} else {
    Write-Host "  Downloading latest Hayabusa release from GitHub..." -ForegroundColor Gray
    try {
        $HayaApi = Invoke-RestMethod -Uri "https://api.github.com/repos/Yamato-Security/hayabusa/releases/latest"
        $HayaAsset = $HayaApi.assets | Where-Object { $_.name -like "*win-x64*.zip" } | Select-Object -First 1
        if ($HayaAsset) {
            $ZipPath = Join-Path $env:TEMP "hayabusa.zip"
            Invoke-WebRequest -Uri $HayaAsset.browser_download_url -OutFile $ZipPath
            Expand-Archive -Path $ZipPath -DestinationPath $TargetDir -Force
            Remove-Item $ZipPath -Force
            Write-Host "  [✓] Hayabusa installed successfully." -ForegroundColor Green
        }
    } catch {
        Write-Warning "  Failed to download Hayabusa automatically: $_. Please download manually from github.com/Yamato-Security/hayabusa."
    }
}

# 2. Chainsaw (WithSecure Labs)
Write-Host "`n[2/3] Checking Chainsaw (Cross-Artifact Threat Hunting Engine)..." -ForegroundColor Yellow
$ChainsawExe = Join-Path $TargetDir "chainsaw.exe"
if (Test-Path $ChainsawExe) {
    Write-Host "  [✓] Chainsaw already exists at $ChainsawExe" -ForegroundColor Green
} else {
    Write-Host "  Downloading latest Chainsaw release from GitHub..." -ForegroundColor Gray
    try {
        $ChainApi = Invoke-RestMethod -Uri "https://api.github.com/repos/WithSecureLabs/chainsaw/releases/latest"
        $ChainAsset = $ChainApi.assets | Where-Object { $_.name -like "*x86_64-pc-windows-msvc*.zip" } | Select-Object -First 1
        if ($ChainAsset) {
            $ZipPath = Join-Path $env:TEMP "chainsaw.zip"
            Invoke-WebRequest -Uri $ChainAsset.browser_download_url -OutFile $ZipPath
            Expand-Archive -Path $ZipPath -DestinationPath $TargetDir -Force
            Remove-Item $ZipPath -Force
            Write-Host "  [✓] Chainsaw installed successfully." -ForegroundColor Green
        }
    } catch {
        Write-Warning "  Failed to download Chainsaw automatically: $_. Please download manually from github.com/WithSecureLabs/chainsaw."
    }
}

# 3. Eric Zimmerman Tools (MFTECmd, PECmd)
Write-Host "`n[3/3] Checking Eric Zimmerman Tools (MFTECmd, PECmd)..." -ForegroundColor Yellow
$MfteExe = Join-Path $TargetDir "MFTECmd.exe"
if (Test-Path $MfteExe) {
    Write-Host "  [✓] MFTECmd already exists at $MfteExe" -ForegroundColor Green
} else {
    Write-Host "  Downloading Zimmerman Tools Updater..." -ForegroundColor Gray
    try {
        $EzScript = Join-Path $env:TEMP "Get-ZimmermanTools.ps1"
        Invoke-WebRequest -Uri "https://raw.githubusercontent.com/EricZimmerman/Get-ZimmermanTools/master/Get-ZimmermanTools.ps1" -OutFile $EzScript
        & $EzScript -Dest $TargetDir
        Remove-Item $EzScript -Force
        Write-Host "  [✓] Eric Zimmerman Tools installed successfully." -ForegroundColor Green
    } catch {
        Write-Warning "  Failed to download EZ-Tools: $_."
    }
}

Write-Host "`n[!] SECURITY: Downloaded binaries are NOT auto hash-verified. Use -VerifyHash or check manually:" -ForegroundColor Yellow
Write-Host "    Hayabusa: https://github.com/Yamato-Security/hayabusa/releases (compare SHA256 from release notes)" -ForegroundColor Gray
Write-Host "    Chainsaw: https://github.com/WithSecureLabs/chainsaw/releases" -ForegroundColor Gray
Write-Host "    EZ-Tools: https://ericzimmerman.github.io/#!index.md" -ForegroundColor Gray

if ($VerifyHash) {
    Write-Host "`n[VerifyHash] Computing SHA256 for downloaded binaries..." -ForegroundColor Cyan
    Get-ChildItem -Path $TargetDir -File -ErrorAction SilentlyContinue | ForEach-Object {
        $hash = (Get-FileHash $_.FullName -Algorithm SHA256).Hash
        Write-Host ("  {0}  {1}" -f $hash.ToLower(), $_.Name) -ForegroundColor Gray
    }
    $sbom = Join-Path $TargetDir "sbom.json"
    $entries = Get-ChildItem -Path $TargetDir -File | ForEach-Object {
        @{ name = $_.Name; sha256 = (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLower(); size = $_.Length; path = $_.FullName }
    }
    @{ generated_at = (Get-Date -Format o); target_dir = $TargetDir; binaries = $entries } | ConvertTo-Json -Depth 4 | Out-File -Encoding utf8 $sbom
    Write-Host "  SBOM written to $sbom (manual compare with official release hashes required)" -ForegroundColor Green
} else {
    Write-Host "`n  Tip: Re-run with -VerifyHash to compute SHA256 and write tools/bin/sbom.json" -ForegroundColor DarkGray
}

Write-Host "`n[✓] Setup complete! To add to PATH in current session:" -ForegroundColor Green
Write-Host "    `$env:Path += ';$TargetDir'" -ForegroundColor White
