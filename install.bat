@echo off
echo ==========================================
echo BioInsight Installation Script
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)

echo [1/5] Installing Python dependencies...
cd /d "%~dp0backend"
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install Python dependencies
    pause
    exit /b 1
)

echo [2/5] Installing Central Dashboard dependencies...
cd /d "%~dp0central-dashboard"
call npm install
if errorlevel 1 (
    echo [ERROR] Failed to install dashboard dependencies
    pause
    exit /b 1
)

echo [3/5] Installing PWA Client dependencies...
cd /d "%~dp0pwa-client"
call npm install
if errorlevel 1 (
    echo [ERROR] Failed to install PWA dependencies
    pause
    exit /b 1
)

echo [4/5] Creating startup shortcuts...
cd /d "%~dp0"
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('$env:USERPROFILE\Desktop\BioInsight.lnk'); $Shortcut.TargetPath = '%~dp0start_bioinsight.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Save()"

echo [5/5] Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('$env:USERPROFILE\Desktop\Start BioInsight.lnk'); $Shortcut.TargetPath = '%~dp0start_bioinsight.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Save()"

echo.
echo ==========================================
echo Installation Complete!
echo ==========================================
echo.
echo To start BioInsight:
echo   1. Double-click "Start BioInsight" on your desktop
echo   2. Or run: start_bioinsight.bat
echo.
echo Access the applications:
echo   - Central Dashboard: http://localhost:5173
echo   - PWA Client: http://localhost:5174/pwa/
echo.
pause
