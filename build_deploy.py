"""
BioInsight Deployment Package Builder
Creates a ZIP file with all necessary files and installation scripts
"""
import os
import sys
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def create_deployment_package():
    print("=" * 60)
    print("BioInsight Deployment Package Builder")
    print("=" * 60)
    
    project_root = Path(__file__).parent.absolute()
    dist_dir = project_root / "dist"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"BioInsight_Deploy_{timestamp}"
    package_dir = dist_dir / package_name
    zip_file = dist_dir / f"{package_name}.zip"
    
    # Clean and create directories
    print("\n[1/6] Setting up directories...")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True)
    package_dir.mkdir(parents=True)
    
    # Define what to include/exclude
    exclude_patterns = [
        '__pycache__', '*.pyc', '*.pyo', '.git', '.env', 
        'venv', '.venv', 'node_modules', '.npm',
        'dist', 'build', '*.log', '.cache'
    ]
    
    def should_exclude(path):
        path_str = str(path)
        for pattern in exclude_patterns:
            if pattern in path_str:
                return True
        return False
    
    # Copy backend
    print("\n[2/6] Copying backend...")
    backend_src = project_root / "backend"
    backend_dst = package_dir / "backend"
    if backend_src.exists():
        shutil.copytree(backend_src, backend_dst, 
                       ignore=lambda d, files: [f for f in files if should_exclude(Path(d) / f)],
                       dirs_exist_ok=True)
        print(f"  ✓ Backend copied")
    
    # Copy built frontend files only (dist folders)
    print("\n[3/6] Copying frontend builds...")
    
    # Central Dashboard dist
    dashboard_src = project_root / "central-dashboard" / "dist"
    dashboard_dst = package_dir / "central-dashboard" / "dist"
    if dashboard_src.exists():
        shutil.copytree(dashboard_src, dashboard_dst, dirs_exist_ok=True)
        print(f"  ✓ Dashboard build copied")
    else:
        print(f"  ⚠ Dashboard dist not found! Run 'npm run build' in central-dashboard")
        return False
    
    # Copy essential dashboard files (package.json for serve, public if exists)
    dashboard_pkg = project_root / "central-dashboard" / "package.json"
    if dashboard_pkg.exists():
        shutil.copy(dashboard_pkg, package_dir / "central-dashboard" / "package.json")
    
    # PWA dist
    pwa_src = project_root / "pwa-client" / "dist"
    pwa_dst = package_dir / "pwa-client" / "dist"
    if pwa_src.exists():
        shutil.copytree(pwa_src, pwa_dst, dirs_exist_ok=True)
        print(f"  ✓ PWA build copied")
    else:
        print(f"  ⚠ PWA dist not found! Run 'npm run build' in pwa-client")
        return False
    
    # Copy essential PWA files
    pwa_pkg = project_root / "pwa-client" / "package.json"
    if pwa_pkg.exists():
        shutil.copy(pwa_pkg, package_dir / "pwa-client" / "package.json")
    pwa_manifest = project_root / "pwa-client" / "manifest.json"
    if pwa_manifest.exists():
        shutil.copy(pwa_manifest, package_dir / "pwa-client" / "manifest.json")
    
    # Copy database
    print("\n[4/6] Copying database...")
    db_src = project_root / "database"
    if db_src.exists():
        db_dst = package_dir / "database"
        shutil.copytree(db_src, db_dst, dirs_exist_ok=True)
        print(f"  ✓ Database copied")
    else:
        # Create empty database directory
        (package_dir / "database").mkdir(exist_ok=True)
        print(f"  ✓ Database directory created")
    
    # Copy README and docs
    print("\n[5/6] Copying documentation...")
    readme = project_root / "README.md"
    if readme.exists():
        shutil.copy(readme, package_dir / "README.md")
        print(f"  ✓ README copied")
    
    # Create installation scripts
    print("\n[6/6] Creating installation scripts...")
    
    # install.bat
    install_bat = package_dir / "install.bat"
    install_bat.write_text('''@echo off
echo ==========================================
echo BioInsight Installation
echo ==========================================
echo.
echo This will install BioInsight and its dependencies.
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)
echo [OK] Python found

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)
echo [OK] Node.js found

echo.
echo [1/3] Installing Python dependencies...
cd /d "%~dp0backend"
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install Python dependencies
    pause
    exit /b 1
)

echo.
echo [2/3] Installing Central Dashboard dependencies...
cd /d "%~dp0central-dashboard"
call npm install --production
if errorlevel 1 (
    echo [ERROR] Failed to install dashboard dependencies
    pause
    exit /b 1
)

echo.
echo [3/3] Installing PWA Client dependencies...
cd /d "%~dp0pwa-client"
call npm install --production
if errorlevel 1 (
    echo [ERROR] Failed to install PWA dependencies
    pause
    exit /b 1
)

echo.
echo Creating desktop shortcut...
cd /d "%~dp0"
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('$env:USERPROFILE\\Desktop\\Start BioInsight.lnk'); $Shortcut.TargetPath = '%~dp0start.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.IconLocation = '%SystemRoot%\\System32\\SHELL32.dll,14'; $Shortcut.Save()"

echo.
echo ==========================================
echo Installation Complete!
echo ==========================================
echo.
echo To start BioInsight:
echo   - Double-click 'Start BioInsight' on your desktop
echo   - Or run start.bat from this folder
echo.
echo Access the applications:
echo   - Central Dashboard: http://localhost:5173
echo   - PWA Client: http://localhost:5174/pwa/
echo.
pause
''')
    print(f"  ✓ install.bat created")
    
    # start.bat
    start_bat = package_dir / "start.bat"
    start_bat.write_text('''@echo off
echo ==========================================
echo Starting BioInsight Server
echo ==========================================
echo.
echo This will start:
echo   - Backend API (Port 8000)
echo   - Central Dashboard (Port 5173)
echo   - PWA Client (Port 5174)
echo.
echo Press Ctrl+C to stop all services
echo ==========================================
echo.

cd /d "%~dp0"

REM Start Backend
echo [1/3] Starting Backend...
start "BioInsight Backend" cmd /k "cd backend && python -m app.main"

REM Wait for backend to initialize
timeout /t 5 /nobreak >nul

REM Start Dashboard
echo [2/3] Starting Central Dashboard...
start "BioInsight Dashboard" cmd /k "cd central-dashboard && npm run preview -- --host 0.0.0.0 --port 5173"

REM Wait for dashboard
timeout /t 3 /nobreak >nul

REM Start PWA
echo [3/3] Starting PWA Client...
start "BioInsight PWA" cmd /k "cd pwa-client && npm run preview -- --host 0.0.0.0 --port 5174"

timeout /t 3 /nobreak >nul

echo.
echo ==========================================
echo BioInsight is running!
echo ==========================================
echo.
echo Access your applications:
echo   Central Dashboard: http://localhost:5173
echo   PWA Client:        http://localhost:5174/pwa/
echo   Backend API:       http://localhost:8000
echo.
echo Press any key to open the dashboard...
pause >nul
start http://localhost:5173

echo.
echo Servers are running in separate windows.
echo Close those windows to stop the servers.
echo.
pause
''')
    print(f"  ✓ start.bat created")
    
    # Create README for deployment
    deploy_readme = package_dir / "DEPLOY_README.txt"
    deploy_readme.write_text(f'''BioInsight Deployment Package
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

INSTALLATION:
1. Extract this ZIP file to a folder
2. Double-click 'install.bat'
3. Wait for dependencies to install
4. Double-click 'start.bat' to run the server

REQUIREMENTS:
- Python 3.11 or higher
- Node.js 18 or higher
- Windows 10/11

ACCESS POINTS:
- Central Dashboard: http://localhost:5173
- PWA Client: http://localhost:5174/pwa/
- Backend API: http://localhost:8000

TROUBLESHOOTING:
- If ports are in use, check if BioInsight is already running
- Make sure Python and Node.js are in your PATH
- Check that Windows Firewall isn't blocking the ports

SUPPORT:
See the main README.md for detailed documentation.
''')
    print(f"  ✓ DEPLOY_README.txt created")
    
    # Create ZIP file
    print(f"\n[+] Creating ZIP archive...")
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in package_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(package_dir)
                zf.write(file_path, arcname)
    
    # Calculate size
    zip_size_mb = zip_file.stat().st_size / (1024 * 1024)
    
    # Clean up temp directory
    shutil.rmtree(package_dir)
    
    # Success message
    print(f"\n{'=' * 60}")
    print(f"Deployment Package Created Successfully!")
    print(f"{'=' * 60}")
    print(f"\nLocation: {zip_file}")
    print(f"Size: {zip_size_mb:.2f} MB")
    print(f"\nTo deploy:")
    print(f"  1. Copy {zip_file.name} to target machine")
    print(f"  2. Extract to a folder")
    print(f"  3. Run install.bat")
    print(f"  4. Run start.bat to start the server")
    print(f"\n{'=' * 60}")
    
    return True

if __name__ == "__main__":
    try:
        success = create_deployment_package()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
