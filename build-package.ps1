#!/usr/bin/env powershell
# BioInsight Deployment Package Builder
# Creates a deployable ZIP file with installation scripts

param(
    [string]$OutputDir = "dist",
    [string]$PackageName = "BioInsight"
)

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "BioInsight Deployment Package Builder" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Get version from package.json or use default
$Version = "1.0.0"
$PackageJson = Join-Path $PSScriptRoot "package.json"
if (Test-Path $PackageJson) {
    $Json = Get-Content $PackageJson | ConvertFrom-Json
    if ($Json.version) {
        $Version = $Json.version
    }
}

Write-Host "Building deployment package v$Version..." -ForegroundColor Yellow

# Create output directory
$DistDir = Join-Path $PSScriptRoot $OutputDir
$PackageDir = Join-Path $DistDir "${PackageName}-${Version}"
$ZipFile = Join-Path $DistDir "${PackageName}-${Version}.zip"

if (Test-Path $DistDir) {
    Remove-Item -Recurse -Force $DistDir
}
New-Item -ItemType Directory -Force -Path $PackageDir | Out-Null

Write-Host "[1/5] Copying backend files..." -ForegroundColor Green
Copy-Item -Path (Join-Path $PSScriptRoot "backend") -Destination $PackageDir -Recurse -Force

Write-Host "[2/5] Copying frontend files..." -ForegroundColor Green
Copy-Item -Path (Join-Path $PSScriptRoot "central-dashboard") -Destination $PackageDir -Recurse -Force
Copy-Item -Path (Join-Path $PSScriptRoot "pwa-client") -Destination $PackageDir -Recurse -Force

Write-Host "[3/5] Copying installation scripts..." -ForegroundColor Green
Copy-Item -Path (Join-Path $PSScriptRoot "install.bat") -Destination $PackageDir -Force
Copy-Item -Path (Join-Path $PSScriptRoot "start_bioinsight.bat") -Destination $PackageDir -Force
Copy-Item -Path (Join-Path $PSScriptRoot "README.md") -Destination $PackageDir -Force

Write-Host "[4/5] Creating deployment archive..." -ForegroundColor Green
if (Test-Path $ZipFile) {
    Remove-Item -Force $ZipFile
}

# Use .NET for compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$CompressionLevel = [System.IO.Compression.CompressionLevel]::Optimal
[System.IO.Compression.ZipFile]::CreateFromDirectory($PackageDir, $ZipFile, $CompressionLevel, $true)

# Clean up temp directory
Remove-Item -Recurse -Force $PackageDir

Write-Host "[5/5] Verifying package..." -ForegroundColor Green
$ZipSize = (Get-Item $ZipFile).Length / 1MB
Write-Host "Package size: $($ZipSize.ToString('F2')) MB" -ForegroundColor Cyan

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Deployment Package Created!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Location: $ZipFile" -ForegroundColor Yellow
Write-Host ""
Write-Host "Installation Instructions:" -ForegroundColor Cyan
Write-Host "  1. Extract $([System.IO.Path]::GetFileName($ZipFile)) to a folder" -ForegroundColor White
Write-Host "  2. Double-click install.bat" -ForegroundColor White
Write-Host "  3. Wait for dependencies to install" -ForegroundColor White
Write-Host "  4. Run start_bioinsight.bat to start the server" -ForegroundColor White
Write-Host ""
Write-Host "Or use PowerShell:" -ForegroundColor Cyan
Write-Host "  Expand-Archive -Path '$([System.IO.Path]::GetFileName($ZipFile))' -DestinationPath 'BioInsight'" -ForegroundColor Gray
Write-Host "  cd BioInsight" -ForegroundColor Gray
Write-Host "  .\install.bat" -ForegroundColor Gray
Write-Host ""
