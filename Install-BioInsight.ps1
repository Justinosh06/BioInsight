# BioInsight Installer Script
# Run this in PowerShell to install BioInsight

param(
    [string]$InstallPath = "$env:LOCALAPPDATA\Programs\BioInsight"
)

$ErrorActionPreference = "Stop"

function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-ColorOutput Green "========================================"
Write-ColorOutput Green "    BioInsight Installer v1.0.0"
Write-ColorOutput Green "========================================"
Write-Output ""

$SourceDir = "$PSScriptRoot\dist\BioInsight_Deploy"

if (-not (Test-Path $SourceDir)) {
    Write-ColorOutput Red "ERROR: Cannot find BioInsight_Deploy folder!"
    Write-Output "Expected location: $SourceDir"
    exit 1
}

Write-Output "Install location: $InstallPath"
Write-Output "Source: $SourceDir"
Write-Output ""

# Create installation directory
if (-not (Test-Path $InstallPath)) {
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
    Write-ColorOutput Green "[✓] Created installation directory"
} else {
    Write-ColorOutput Yellow "[!] Directory exists, will overwrite files"
}

# Copy files
Write-Output ""
Write-Output "Copying files..."
$files = Get-ChildItem -Path $SourceDir -Recurse
$total = $files.Count
$current = 0

foreach ($file in $files) {
    $current++
    $relativePath = $file.FullName.Substring($SourceDir.Length + 1)
    $destPath = Join-Path $InstallPath $relativePath
    
    if ($file.PSIsContainer) {
        if (-not (Test-Path $destPath)) {
            New-Item -ItemType Directory -Path $destPath -Force | Out-Null
        }
    } else {
        $destDir = Split-Path -Parent $destPath
        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }
        Copy-Item -Path $file.FullName -Destination $destPath -Force
    }
    
    if ($current % 100 -eq 0) {
        Write-Output "  Progress: $current / $total files..."
    }
}

Write-ColorOutput Green "[✓] Copied $total files"

# Create shortcuts
Write-Output ""
Write-Output "Creating shortcuts..."

$WshShell = New-Object -ComObject WScript.Shell

# Desktop shortcut
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$DesktopShortcut = $WshShell.CreateShortcut("$DesktopPath\Start BioInsight.lnk")
$DesktopShortcut.TargetPath = "$InstallPath\start.bat"
$DesktopShortcut.WorkingDirectory = $InstallPath
$DesktopShortcut.IconLocation = "%SystemRoot%\System32\shell32.dll,4"
$DesktopShortcut.Description = "Start BioInsight Server"
$DesktopShortcut.Save()
Write-ColorOutput Green "[✓] Created Desktop shortcut"

# Start Menu shortcut
$StartMenuPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\BioInsight"
if (-not (Test-Path $StartMenuPath)) {
    New-Item -ItemType Directory -Path $StartMenuPath -Force | Out-Null
}

$StartShortcut = $WshShell.CreateShortcut("$StartMenuPath\Start BioInsight.lnk")
$StartShortcut.TargetPath = "$InstallPath\start.bat"
$StartShortcut.WorkingDirectory = $InstallPath
$StartShortcut.IconLocation = "%SystemRoot%\System32\shell32.dll,4"
$StartShortcut.Description = "Start BioInsight Server"
$StartShortcut.Save()

$InstallShortcut = $WshShell.CreateShortcut("$StartMenuPath\Install Dependencies.lnk")
$InstallShortcut.TargetPath = "$InstallPath\install.bat"
$InstallShortcut.WorkingDirectory = $InstallPath
$InstallShortcut.IconLocation = "%SystemRoot%\System32\shell32.dll,39"
$InstallShortcut.Description = "Install BioInsight Dependencies"
$InstallShortcut.Save()

Write-ColorOutput Green "[✓] Created Start Menu shortcuts"

# Run install.bat
Write-Output ""
Write-ColorOutput Yellow "Running dependency installation..."
Write-Output "----------------------------------------"
& "$InstallPath\install.bat"
Write-Output "----------------------------------------"

# Create uninstaller
$UninstallScript = @"
@echo off
echo Uninstalling BioInsight...
rd /s /q "$InstallPath"
del "%USERPROFILE%\Desktop\Start BioInsight.lnk" 2>nul
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\BioInsight\*.lnk" 2>nul
rd "%APPDATA%\Microsoft\Windows\Start Menu\Programs\BioInsight" 2>nul
echo BioInsight uninstalled.
pause
"@

$UninstallScript | Out-File -FilePath "$InstallPath\uninstall.bat" -Encoding ASCII

# Installation complete
Write-Output ""
Write-ColorOutput Green "========================================"
Write-ColorOutput Green "    Installation Complete!"
Write-ColorOutput Green "========================================"
Write-Output ""
Write-Output "BioInsight has been installed to:"
Write-Output "  $InstallPath"
Write-Output ""
Write-Output "To start BioInsight:"
Write-Output "  1. Double-click 'Start BioInsight' on your desktop, or"
Write-Output "  2. Click Start > BioInsight > Start BioInsight"
Write-Output ""
Write-Output "To uninstall, run:"
Write-Output "  $InstallPath\uninstall.bat"
Write-Output ""
Write-ColorOutput Cyan "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
