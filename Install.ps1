# BioInsight Simple Installer
# Run this script to install BioInsight

param(
    [string]$InstallPath = "$env:LOCALAPPDATA\BioInsight"
)

Write-Host "BioInsight Installer" -ForegroundColor Green
Write-Host "====================" -ForegroundColor Green
Write-Host ""

# Source directory
$SourceDir = "$PSScriptRoot\dist\BioInsight_Deploy"

if (-not (Test-Path $SourceDir)) {
    Write-Error "Cannot find BioInsight_Deploy folder at $SourceDir!"
    exit 1
}

Write-Host "Installing to: $InstallPath"

# Create installation directory
if (-not (Test-Path $InstallPath)) {
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
    Write-Host "Created installation directory" -ForegroundColor Green
}

# Copy files
Write-Host "Copying files..." -NoNewline
Copy-Item -Path "$SourceDir\*" -Destination $InstallPath -Recurse -Force
Write-Host " Done!" -ForegroundColor Green

# Create shortcuts
$WshShell = New-Object -ComObject WScript.Shell

# Desktop shortcut
$DesktopShortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Start BioInsight.lnk")
$DesktopShortcut.TargetPath = "$InstallPath\start.bat"
$DesktopShortcut.WorkingDirectory = $InstallPath
$DesktopShortcut.IconLocation = "%SystemRoot%\System32\shell32.dll, 4"
$DesktopShortcut.Save()
Write-Host "Created desktop shortcut" -ForegroundColor Green

# Start Menu shortcut
$StartMenuPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\BioInsight"
if (-not (Test-Path $StartMenuPath)) {
    New-Item -ItemType Directory -Path $StartMenuPath -Force | Out-Null
}

$StartShortcut = $WshShell.CreateShortcut("$StartMenuPath\Start BioInsight.lnk")
$StartShortcut.TargetPath = "$InstallPath\start.bat"
$StartShortcut.WorkingDirectory = $InstallPath
$StartShortcut.IconLocation = "%SystemRoot%\System32\shell32.dll, 4"
$StartShortcut.Save()

$InstallShortcut = $WshShell.CreateShortcut("$StartMenuPath\Install BioInsight.lnk")
$InstallShortcut.TargetPath = "$InstallPath\install.bat"
$InstallShortcut.WorkingDirectory = $InstallPath
$InstallShortcut.IconLocation = "%SystemRoot%\System32\shell32.dll, 4"
$InstallShortcut.Save()
Write-Host "Created Start Menu shortcuts" -ForegroundColor Green

# Run install.bat
Write-Host ""
Write-Host "Running installation script..." -ForegroundColor Yellow
& "$InstallPath\install.bat"

Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To start BioInsight:" -ForegroundColor Cyan
Write-Host "  - Double-click 'Start BioInsight' on your desktop, or" -ForegroundColor White
Write-Host "  - Click Start > BioInsight > Start BioInsight" -ForegroundColor White
Write-Host ""
