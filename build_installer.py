#!/usr/bin/env python3
"""
BioInsight Self-Extracting Installer Builder
Creates a Windows installer (.exe) that extracts and sets up BioInsight.

Output:
    dist/BioInsight-Installer.exe - Self-extracting installer
"""
import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path
from datetime import datetime

VERSION = "1.0.0"
PRODUCT_NAME = "BioInsight"
MANUFACTURER = "Ong Syu Hen"

def log(msg): print(f"  {msg}")
def success(msg): print(f"  ✓ {msg}")
def error(msg): print(f"  ✗ {msg}")
def info(msg): print(f"  ℹ {msg}")

def create_installer_script(project_root, package_dir):
    """Create the main installer Python script"""
    
    installer_py = project_root / "dist" / "installer.py"
    
    script_content = '''#!/usr/bin/env python3
"""
BioInsight Installer
Self-extracting installer for BioInsight Agricultural Monitoring System
"""
import os
import sys
import shutil
import zipfile
import subprocess
import tempfile
from pathlib import Path

INSTALL_DIR = Path(r"C:\\Program Files\\BioInsight")
SHORTCUT_NAME = "BioInsight"

def extract_installer():
    """Extract embedded package"""
    print("=" * 60)
    print("  BioInsight Installer v1.0.0")
    print("=" * 60)
    
    # Get the directory containing this script
    script_dir = Path(__file__).parent.absolute()
    package_zip = script_dir / "package.zip"
    
    if not package_zip.exists():
        print("Error: package.zip not found!")
        print(f"Looking for: {package_zip}")
        input("Press Enter to exit...")
        return False
    
    # Create install directory
    print("\\n[1/4] Creating installation directory...")
    try:
        if INSTALL_DIR.exists():
            print(f"  Removing old installation at {INSTALL_DIR}")
            shutil.rmtree(INSTALL_DIR)
        INSTALL_DIR.mkdir(parents=True, exist_ok=True)
        success("Created installation directory")
    except Exception as e:
        error(f"Failed to create directory: {e}")
        print("Please run as Administrator")
        input("Press Enter to exit...")
        return False
    
    # Extract files
    print("\\n[2/4] Extracting files...")
    try:
        with zipfile.ZipFile(package_zip, 'r') as zf:
            zf.extractall(INSTALL_DIR)
        success(f"Extracted {len(list(INSTALL_DIR.rglob('*')))} files")
    except Exception as e:
        error(f"Extraction failed: {e}")
        input("Press Enter to exit...")
        return False
    
    # Install dependencies
    print("\\n[3/4] Installing dependencies...")
    print("  This may take several minutes...")
    
    # Install Python dependencies
    backend_dir = INSTALL_DIR / "backend"
    if (backend_dir / "requirements.txt").exists():
        print("  Installing Python packages...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(backend_dir / "requirements.txt")],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            success("Python dependencies installed")
        else:
            warning("Some Python packages may have failed to install")
    
    # Install Node.js dependencies
    dashboard_dir = INSTALL_DIR / "central-dashboard"
    if (dashboard_dir / "package.json").exists():
        print("  Installing Dashboard dependencies...")
        result = subprocess.run(
            ["npm", "install"],
            cwd=str(dashboard_dir),
            capture_output=True, text=True
        )
        if result.returncode == 0:
            success("Dashboard dependencies installed")
    
    pwa_dir = INSTALL_DIR / "pwa-client"
    if (pwa_dir / "package.json").exists():
        print("  Installing PWA dependencies...")
        result = subprocess.run(
            ["npm", "install"],
            cwd=str(pwa_dir),
            capture_output=True, text=True
        )
        if result.returncode == 0:
            success("PWA dependencies installed")
    
    # Create shortcuts
    print("\\n[4/4] Creating shortcuts...")
    try:
        # Start Menu shortcut
        start_menu = Path(os.environ.get('PROGRAMDATA', r'C:\\ProgramData')) / "Microsoft\\Windows\\Start Menu\\Programs"
        start_menu_shortcut = start_menu / f"{SHORTCUT_NAME}.lnk"
        
        # Desktop shortcut
        desktop = Path(os.environ.get('PUBLIC', r'C:\\Users\\Public')) / "Desktop"
        desktop_shortcut = desktop / f"{SHORTCUT_NAME}.lnk"
        
        # Create shortcuts using PowerShell
        start_bat = INSTALL_DIR / "start.bat"
        
        for shortcut_path in [start_menu_shortcut, desktop_shortcut]:
            ps_cmd_parts = [
                '$WshShell = New-Object -comObject WScript.Shell;',
                '$Shortcut = $WshShell.CreateShortcut("' + str(shortcut_path) + '");',
                '$Shortcut.TargetPath = "' + str(start_bat) + '");',
                '$Shortcut.WorkingDirectory = "' + str(INSTALL_DIR) + '");',
                '$Shortcut.Description = "Start BioInsight";',
                '$Shortcut.IconLocation = "shell32.dll,14";',
                '$Shortcut.Save()'
            ]
            ps_cmd = '\n'.join(ps_cmd_parts)
            subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)
        
        success("Shortcuts created")
    except Exception as e:
        warning(f"Could not create shortcuts: {e}")
    
    # Complete
    print("\\n" + "=" * 60)
    print("  INSTALLATION COMPLETE!")
    print("=" * 60)
    print(f"\\n  Installation folder: {INSTALL_DIR}")
    print(f"  Start Menu: {SHORTCUT_NAME}")
    print(f"  Desktop: {SHORTCUT_NAME}")
    print("\\n  To start BioInsight:")
    print(f"    Double-click the {SHORTCUT_NAME} shortcut")
    print("\\n" + "=" * 60)
    
    input("\\nPress Enter to exit...")
    return True

def success(msg): print(f"    ✓ {msg}")
def error(msg): print(f"    ✗ {msg}")
def warning(msg): print(f"    ⚠ {msg}")

if __name__ == "__main__":
    try:
        extract_installer()
    except Exception as e:
        print(f"\\nError: {e}")
        import traceback
        traceback.print_exc()
        input("\\nPress Enter to exit...")
'''

    installer_py.write_text(script_content, encoding='utf-8')
    success("Created installer.py")
    return installer_py

def create_sfx_stub(project_root):
    """Create a self-extracting stub that combines with the zip"""
    
    stub_py = project_root / "dist" / "sfx_stub.py"
    
    stub_content = '''#!/usr/bin/env python3
"""
BioInsight Self-Extracting Archive Stub
This script extracts the embedded zip and runs the installer
"""
import os
import sys
import zipfile
import tempfile
import subprocess
from pathlib import Path

def main():
    # Get the path to this executable/script
    exe_path = Path(sys.executable if getattr(sys, 'frozen', False) else __file__)
    script_dir = exe_path.parent.absolute()
    
    # Read the zip data appended to this file
    with open(exe_path, 'rb') as f:
        content = f.read()
    
    # Find the zip marker
    marker = b'PK\\x05\\x06'  # End of central directory signature
    marker_pos = content.rfind(marker)
    
    if marker_pos == -1:
        print("Error: Could not find embedded archive!")
        input("Press Enter to exit...")
        return 1
    
    # Extract the zip portion
    # Find start of central directory
    cd_start = content.rfind(b'PK\\x01\\x02', 0, marker_pos)
    if cd_start == -1:
        # Try to find from end of file record
        eocd_start = content.rfind(b'PK\\x05\\x06')
        if eocd_start != -1 and eocd_start >= 20:
            cd_offset = int.from_bytes(content[eocd_start+16:eocd_start+20], 'little')
            cd_start = cd_offset
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    zip_path = Path(temp_dir) / "package.zip"
    
    # Write the zip file
    with open(zip_path, 'wb') as f:
        f.write(content[cd_start:])
    
    # Extract the installer
    installer_dir = Path(temp_dir) / "installer"
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(installer_dir)
    
    # Run the installer
    installer_py = installer_dir / "installer.py"
    if installer_py.exists():
        # Copy package.zip to installer dir
        shutil.copy(zip_path, installer_dir / "package.zip")
        
        # Run installer
        result = subprocess.run([sys.executable, str(installer_py)])
        return result.returncode
    else:
        print("Error: installer.py not found!")
        input("Press Enter to exit...")
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
    
    stub_py.write_text(stub_content, encoding='utf-8')
    success("Created stub")
    return stub_py

def build_exe(project_root, package_dir, installer_py, stub_py):
    """Build the self-extracting executable using PyInstaller or similar"""
    
    # Create a simple batch file instead of EXE for now
    # This is more reliable than PyInstaller for this use case
    
    dist_dir = project_root / "dist"
    exe_path = dist_dir / f"{PRODUCT_NAME}-Installer-v{VERSION}.exe"
    
    # Create the package zip
    package_zip = dist_dir / "package.zip"
    
    log("\n[Build] Creating package archive...")
    with zipfile.ZipFile(package_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in package_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(package_dir)
                zf.write(file_path, arcname)
    
    zip_size = package_zip.stat().st_size / (1024 * 1024)
    success(f"Created package.zip ({zip_size:.1f} MB)")
    
    # Create a simple batch-based installer
    # This launches Python with the installer script
    
    installer_bat = dist_dir / f"{PRODUCT_NAME}-Installer-v{VERSION}.bat"
    
    bat_content = f'''@echo off
echo ==========================================
echo {PRODUCT_NAME} Installer v{VERSION}
echo ==========================================
echo.

REM Check if running as admin
net session >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Please run this installer as Administrator
    echo.
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

echo Extracting installer...
cd /d "%~dp0"

REM Create temp dir and extract
set TEMP_DIR=%TEMP%\\BioInsight_Install_%RANDOM%
mkdir "%TEMP_DIR%"

REM Extract package
powershell -Command "Expand-Archive -Path 'package.zip' -DestinationPath '%TEMP_DIR%' -Force"

REM Run installer
python "%TEMP_DIR%\\installer.py"

REM Cleanup
rmdir /S /Q "%TEMP_DIR%"

pause
'''
    
    installer_bat.write_text(bat_content, encoding='utf-8')
    
    # Also create a PowerShell version for better UX
    installer_ps1 = dist_dir / f"{PRODUCT_NAME}-Installer-v{VERSION}.ps1"
    
    ps1_content = f'''
# {PRODUCT_NAME} Installer v{VERSION}
# Requires Administrator privileges

# Check if running as admin
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {{{{
    Write-Host "[ERROR] Please run this installer as Administrator" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    pause
    exit 1
}}}}

# Check Python
try {{{{
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] $pythonVersion" -ForegroundColor Green
}}}} catch {{{{
    Write-Host "[ERROR] Python is not installed" -ForegroundColor Red
    Write-Host "Please install Python 3.11+ from https://python.org" -ForegroundColor Yellow
    pause
    exit 1
}}}}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  {PRODUCT_NAME} Installer v{VERSION}" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$tempDir = Join-Path $env:TEMP "BioInsight_Install_$([System.Guid]::NewGuid().ToString().Substring(0,8))"

Write-Host "[1/3] Extracting package..." -ForegroundColor Yellow
Expand-Archive -Path (Join-Path $scriptDir "package.zip") -DestinationPath $tempDir -Force
Write-Host "  ✓ Package extracted" -ForegroundColor Green

Write-Host ""
Write-Host "[2/3] Running installer..." -ForegroundColor Yellow
$installerPy = Join-Path $tempDir "installer.py"

# Copy package.zip to temp dir for installer to use
Copy-Item (Join-Path $scriptDir "package.zip") $tempDir

# Run installer
python $installerPy

Write-Host ""
Write-Host "[3/3] Cleaning up..." -ForegroundColor Yellow
Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "  ✓ Cleanup complete" -ForegroundColor Green

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  INSTALLER FINISHED" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
'''
    
    installer_ps1.write_text(ps1_content, encoding='utf-8')
    
    # Create a simple EXE launcher using built-in tools
    # We'll use a self-extracting CAB approach or just batch file
    
    success(f"Created installers:")
    success(f"  - {installer_bat.name} (Batch file)")
    success(f"  - {installer_ps1.name} (PowerShell)")
    success(f"  - package.zip ({zip_size:.1f} MB)")
    
    return dist_dir / f"{PRODUCT_NAME}-Installer-v{VERSION}.bat"

def main():
    print("=" * 70)
    print(f"  {PRODUCT_NAME} Self-Extracting Installer Builder v{VERSION}")
    print("=" * 70)
    
    project_root = Path(__file__).parent.absolute()
    dist_dir = project_root / "dist"
    package_dir = dist_dir / "BioInsight_Package"
    
    # Create package
    log("\n[Setup] Creating package...")
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy backend
    backend_src = project_root / "backend"
    if backend_src.exists():
        shutil.copytree(backend_src, package_dir / "backend",
                       ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.env', 'venv', '.git'))
        success("Copied backend")
    
    # Copy frontends
    for frontend in ['central-dashboard', 'pwa-client']:
        src = project_root / frontend
        if src.exists():
            shutil.copytree(src, package_dir / frontend,
                           ignore=shutil.ignore_patterns('node_modules', 'dist', '__pycache__', '.git'))
            success(f"Copied {frontend}")
    
    # Copy README
    readme = project_root / "README.md"
    if readme.exists():
        shutil.copy(readme, package_dir / "README.md")
    
    # Create scripts
    log("\n[Scripts] Creating installation scripts...")
    
    # install.bat
    (package_dir / "install.bat").write_text('''@echo off
echo ==========================================
echo Installing BioInsight Dependencies
echo ==========================================
echo.

REM Check requirements
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install from https://python.org
    pause
    exit /b 1
)

node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found. Install from https://nodejs.org
    pause
    exit /b 1
)

echo.
echo [1/3] Installing Python dependencies...
cd /d "%~dp0backend"
python -m pip install -r requirements.txt

echo.
echo [2/3] Installing Dashboard dependencies...
cd /d "%~dp0central-dashboard"
call npm install

echo.
echo [3/3] Installing PWA dependencies...
cd /d "%~dp0pwa-client"
call npm install

echo.
echo ==========================================
echo Installation Complete!
echo ==========================================
pause
''')
    
    # start.bat
    (package_dir / "start.bat").write_text('''@echo off
echo ==========================================
echo Starting BioInsight
echo ==========================================
echo.

cd /d "%~dp0"

echo [1/3] Starting Backend on port 8000...
start "BioInsight Backend" cmd /k "cd backend && python -m app.main"
timeout /t 5 /nobreak >nul

echo [2/3] Starting Dashboard on port 5173...
start "BioInsight Dashboard" cmd /k "cd central-dashboard && npm run dev -- --host"
timeout /t 3 /nobreak >nul

echo [3/3] Starting PWA on port 5174...
start "BioInsight PWA" cmd /k "cd pwa-client && npm run dev -- --host"
timeout /t 3 /nobreak >nul

echo.
echo ==========================================
echo BioInsight is running!
echo ==========================================
echo.
echo Dashboard: http://localhost:5173
echo PWA:       http://localhost:5174
echo Backend:   http://localhost:8000
echo.
pause
''')
    success("Created batch scripts")
    
    # Create installer script
    installer_py = create_installer_script(project_root, package_dir)
    stub_py = create_sfx_stub(project_root)
    
    # Build installer
    log("\n[Build] Building installer...")
    exe_path = build_exe(project_root, package_dir, installer_py, stub_py)
    
    print("\n" + "=" * 70)
    print("  BUILD SUCCESSFUL!")
    print("=" * 70)
    print(f"\n  Location: {dist_dir}")
    print(f"\n  Files created:")
    print(f"    - BioInsight-Installer-v{VERSION}.bat")
    print(f"    - BioInsight-Installer-v{VERSION}.ps1")
    print(f"    - package.zip")
    print(f"\n  To install:")
    print(f"    1. Right-click BioInsight-Installer-v{VERSION}.ps1")
    print(f"    2. Select 'Run with PowerShell'")
    print(f"    3. Follow the prompts")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
