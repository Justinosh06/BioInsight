#!/usr/bin/env python3
"""
BioInsight MSI Builder v5 - Direct file inclusion (no zip extraction issues)
"""
import os
import sys
import shutil
import subprocess
import uuid
from pathlib import Path

VERSION = "1.0.0"
MANUFACTURER = "Ong Syu Hen"
PRODUCT_NAME = "BioInsight"

def log(msg): print(f"  {msg}")
def success(msg): print(f"  ✓ {msg}")
def error(msg): print(f"  ✗ {msg}")
def info(msg): print(f"  ℹ {msg}")

def check_wix():
    paths = [
        r"C:\Program Files (x86)\WiX Toolset v3.14\bin",
        r"C:\Program Files (x86)\WiX Toolset v3.11\bin",
    ]
    for path in paths:
        if os.path.exists(os.path.join(path, "candle.exe")):
            os.environ['PATH'] = path + os.pathsep + os.environ['PATH']
            return path
    return None

def build_frontends(project_root):
    """Build frontends before packaging"""
    log("\n[Build] Building frontends...")
    
    # Build Central Dashboard
    dashboard_dir = project_root / "central-dashboard"
    if dashboard_dir.exists():
        log("  Building Central Dashboard...")
        result = subprocess.run(
            "npm install",
            cwd=dashboard_dir,
            capture_output=True,
            text=True,
            shell=True
        )
        if result.returncode != 0:
            error("npm install failed for dashboard")
        else:
            result = subprocess.run(
                "npm run build",
                cwd=dashboard_dir,
                capture_output=True,
                text=True,
                shell=True
            )
            if result.returncode == 0:
                success("Built Central Dashboard")
            else:
                error("Build failed for dashboard")
    
    # Build PWA Client
    pwa_dir = project_root / "pwa-client"
    if pwa_dir.exists():
        log("  Building PWA Client...")
        result = subprocess.run(
            "npm install",
            cwd=pwa_dir,
            capture_output=True,
            text=True,
            shell=True
        )
        if result.returncode != 0:
            error("npm install failed for PWA")
        else:
            result = subprocess.run(
                "npm run build",
                cwd=pwa_dir,
                capture_output=True,
                text=True,
                shell=True
            )
            if result.returncode == 0:
                success("Built PWA Client")
            else:
                error("Build failed for PWA")

def collect_files(source_dir, prefix="", exclude_patterns=None):
    """Collect all files from directory, excluding certain patterns"""
    if exclude_patterns is None:
        exclude_patterns = ['node_modules', '.git', '__pycache__', '.pyc', 
                           'smollm2-1.7b-instruct-q4', '.gguf', 'dist\dist']
    
    files = []
    for item in source_dir.rglob('*'):
        if item.is_file():
            # Check exclusions
            skip = False
            for pattern in exclude_patterns:
                if pattern in str(item):
                    skip = True
                    break
            if not skip:
                rel_path = item.relative_to(source_dir)
                files.append((item, f"{prefix}{rel_path}" if prefix else str(rel_path)))
    return files

def create_wix_components(files):
    """Generate WiX components for all files"""
    components = []
    component_refs = []
    directories = set()
    
    # Build directory structure
    for _, rel_path in files:
        parts = Path(rel_path).parts
        current = "INSTALLFOLDER"
        for part in parts[:-1]:  # All but filename
            dir_id = f"{current}_{part.replace('-', '_').replace('.', '_')}"
            directories.add((current, dir_id, part))
            current = dir_id
    
    # Create components
    for idx, (source_path, rel_path) in enumerate(files, 1):
        comp_id = f"FileComponent{idx}"
        file_id = f"File{idx}"
        comp_guid = str(uuid.uuid4())
        
        # Determine directory reference
        parts = Path(rel_path).parts
        if len(parts) == 1:
            dir_ref = "INSTALLFOLDER"
        else:
            dir_ref = f"INSTALLFOLDER_{'_'.join(parts[:-1]).replace('-', '_').replace('.', '_')}"
        
        # Escape source path for WiX
        source_wix = str(source_path).replace('\\', '\\\\')
        
        components.append(f'''      <Component Id="{comp_id}" Guid="{comp_guid}" Directory="{dir_ref}">
        <File Id="{file_id}" Source="{source_wix}" KeyPath="yes" />
      </Component>''')
        component_refs.append(f'      <ComponentRef Id="{comp_id}" />')
    
    return components, component_refs, directories

def create_wix_directory_structure(directories):
    """Create WiX Directory XML"""
    # Build tree
    tree = {}
    for parent, dir_id, name in directories:
        if parent not in tree:
            tree[parent] = []
        tree[parent].append((dir_id, name))
    
    def build_xml(parent_id, level=0):
        if parent_id not in tree:
            return ""
        
        indent = "  " * level
        xml_parts = []
        
        for dir_id, name in sorted(tree[parent_id]):
            child_xml = build_xml(dir_id, level + 1)
            if child_xml:
                xml_parts.append(f'''{indent}      <Directory Id="{dir_id}" Name="{name}">
{child_xml}{indent}      </Directory>''')
            else:
                xml_parts.append(f'''{indent}      <Directory Id="{dir_id}" Name="{name}" />''')
        
        return "\n".join(xml_parts)
    
    return build_xml("INSTALLFOLDER", 4)

def create_installer_files(build_dir):
    """Create the install.bat and start.bat files"""
    
    # install.bat
    install_bat = build_dir / "install.bat"
    install_bat.write_text(r'''@echo off
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

REM Create virtual environment if it doesn't exist
if not exist "%~dp0venv" (
    echo [1/4] Creating Python virtual environment...
    python -m venv "%~dp0venv"
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
)

REM Activate virtual environment
echo [2/4] Activating virtual environment...
call "%~dp0venv\Scripts\activate.bat"

REM Upgrade pip in virtual environment
echo [3/4] Upgrading pip...
python -m pip install --upgrade pip

REM Install Python dependencies in virtual environment
echo [4/4] Installing Python dependencies...
cd /d "%~dp0backend"
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install Python dependencies from requirements.txt
    pause
    exit /b 1
)

REM Verify critical packages are installed
echo.
echo [Verify] Checking critical packages...
python -c "import fastapi" && echo   [OK] fastapi || echo   [FAIL] fastapi
python -c "import uvicorn" && echo   [OK] uvicorn || echo   [FAIL] uvicorn  
python -c "import sqlalchemy" && echo   [OK] sqlalchemy || echo   [FAIL] sqlalchemy
python -c "import jose" && echo   [OK] jose || echo   [FAIL] jose
python -c "import llama_cpp" && echo   [OK] llama_cpp || echo   [FAIL] llama_cpp
python -c "import transformers" && echo   [OK] transformers || echo   [FAIL] transformers

REM Install serve package globally
echo.
echo Installing serve package...
npm install --location=global serve

echo.
echo ==========================================
echo Installation Complete!
echo ==========================================
echo Virtual environment: %~dp0venv
echo.
pause
''')

    # start.bat - checks for deps and auto-runs install.bat if needed
    start_bat = build_dir / "start.bat"
    start_bat.write_text(r'''@echo off
echo ==========================================
echo Starting BioInsight
echo ==========================================
echo.

REM Check if Python and Node are installed
python --version >nul 2>&1
set PYTHON_OK=%ERRORLEVEL%
node --version >nul 2>&1
set NODE_OK=%ERRORLEVEL%

REM Check if virtual environment exists
if not exist "%~dp0venv" (
    echo [First Run] Virtual environment not found. Running installer first...
    call "%~dp0install.bat"
    if errorlevel 1 exit /b 1
)

REM Activate virtual environment
echo [Startup] Activating virtual environment...
call "%~dp0venv\Scripts\activate.bat"

REM Check if Python dependencies are installed
set DEPS_OK=0
python -c "import fastapi, uvicorn, sqlalchemy, llama_cpp, transformers, jose" >nul 2>&1
if %ERRORLEVEL% EQU 0 set DEPS_OK=1

REM If Python is missing, run install
if %PYTHON_OK% NEQ 0 (
    echo [First Run] Python not found. Running installer first...
    call "%~dp0install.bat"
    if errorlevel 1 exit /b 1
) else if %NODE_OK% NEQ 0 (
    echo [First Run] Node.js not found. Running installer first...
    call "%~dp0install.bat"
    if errorlevel 1 exit /b 1
) else if %DEPS_OK% EQU 0 (
    echo [First Run] Python dependencies missing. Installing...
    call "%~dp0install.bat"
    if errorlevel 1 exit /b 1
)

REM Set database path to AppData (writable)
set "DATA_DIR=%LOCALAPPDATA%\BioInsight"
if not exist "%DATA_DIR%" mkdir "%DATA_DIR%"
set "DATABASE_URL=sqlite:///%DATA_DIR%/bioinsight.db"

REM Start backend (using virtual environment Python)
echo.
echo [Startup] Starting backend server...
cd /d "%~dp0backend"
set "PYTHONPATH=%~dp0backend"
start "BioInsight Backend" cmd /k "python app/main.py"

REM Wait for backend to start
echo [Startup] Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

REM Start frontend (central-dashboard)
echo [Startup] Starting central dashboard...
cd /d "%~dp0central-dashboard\dist"
start "BioInsight Dashboard" cmd /k "serve -s . -l 5173"

REM Wait for dashboard to start
echo [Startup] Waiting for dashboard to initialize...
timeout /t 3 /nobreak >nul

REM Start PWA client
echo [Startup] Starting PWA client...
cd /d "%~dp0pwa-client\dist"
start "BioInsight PWA" cmd /k "serve -s . -l 5174"

REM Wait for PWA to start
echo [Startup] Waiting for PWA to initialize...
timeout /t 3 /nobreak >nul

REM Open browser
echo [Startup] Opening browser...
start http://localhost:5173

echo.
echo ==========================================
echo BioInsight is running!
echo ==========================================
echo.
echo Backend: http://localhost:8000
echo Dashboard: http://localhost:5173
echo PWA: http://localhost:5174
echo.
echo Press any key to close this window...
pause >nul
''')

def create_msi(project_root, output_dir, files):
    """Create MSI with all files included directly"""
    
    # Generate components
    components, component_refs, directories = create_wix_components(files)
    dir_xml = create_wix_directory_structure(directories)
    
    # Add icon if exists
    icon_path = project_root / "assets" / "icon.ico"
    icon_xml = ""
    if icon_path.exists():
        icon_xml = f'    <Icon Id="MainIcon" SourceFile="{icon_path}" />\n'
        icon_xml += '    <Property Id="ARPPRODUCTICON" Value="MainIcon" />\n'
    
    # Create WiX XML
    wxs_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*" 
           Name="BioInsight"
           Language="1033"
           Version="1.0.0"
           Manufacturer="Ong Syu Hen"
           UpgradeCode="a1b2c3d4-e5f6-7890-abcd-ef1234567890">
    
    <Package InstallerVersion="200" 
             Compressed="yes" 
             InstallScope="perUser"
             Platform="x64" />

{icon_xml}
    <MediaTemplate EmbedCab="yes" CompressionLevel="high" />

    <Feature Id="ProductFeature" Title="BioInsight" Level="1">
{chr(10).join(component_refs)}
      <ComponentRef Id="MenuShortcuts" />
      <ComponentRef Id="DesktopShortcut" />
    </Feature>

    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="LocalAppDataFolder">
        <Directory Id="INSTALLFOLDER" Name="BioInsight">
{dir_xml}
        </Directory>
      </Directory>
      <Directory Id="ProgramMenuFolder">
        <Directory Id="ApplicationProgramsFolder" Name="BioInsight"/>
      </Directory>
      <Directory Id="DesktopFolder" Name="Desktop" />
    </Directory>

{chr(10).join(components)}

    <DirectoryRef Id="ApplicationProgramsFolder">
      <Component Id="MenuShortcuts" Guid="33333333-4444-5555-6666-777777777777">
        <Shortcut Id="StartMenuStart" 
                  Name="Start BioInsight"
                  Description="Start BioInsight Server"
                  Target="[INSTALLFOLDER]start.bat"
                  WorkingDirectory="INSTALLFOLDER"
                  Icon="MainIcon"
                  Show="normal" />
        <Shortcut Id="StartMenuInstall"
                  Name="Install Dependencies"
                  Description="Install BioInsight Dependencies"
                  Target="[INSTALLFOLDER]install.bat"
                  WorkingDirectory="INSTALLFOLDER"
                  Show="normal" />
        <RemoveFolder Id="ApplicationProgramsFolder" On="uninstall"/>
        <RegistryValue Root="HKCU" Key="Software\\Ong Syu Hen\\BioInsight" 
                      Name="installed" Type="integer" Value="1" KeyPath="yes"/>
      </Component>
    </DirectoryRef>

    <DirectoryRef Id="DesktopFolder">
      <Component Id="DesktopShortcut" Guid="44444444-5555-6666-7777-888888888888">
        <Condition>INSTALLDESKTOPSHORTCUT</Condition>
        <Shortcut Id="DesktopStart"
                  Name="BioInsight"
                  Description="Start BioInsight Agricultural Monitoring"
                  Target="[INSTALLFOLDER]start.bat"
                  WorkingDirectory="INSTALLFOLDER"
                  Icon="MainIcon"
                  Show="normal" />
        <RegistryValue Root="HKCU"
                      Key="Software\\Ong Syu Hen\\BioInsight"
                      Name="desktopshortcut"
                      Type="integer"
                      Value="1"
                      KeyPath="yes"/>
        <RemoveFile Id="RemoveDesktopLnk" Name="BioInsight.lnk" On="uninstall"/>
      </Component>
    </DirectoryRef>

    <Property Id="INSTALLDESKTOPSHORTCUT" Value="1" />

    <UIRef Id="WixUI_InstallDir" />
    <Property Id="WIXUI_INSTALLDIR" Value="INSTALLFOLDER" />
    
    <!-- Generic EULA -->
    <WixVariable Id="WixUILicenseRtf" Value="{project_root / 'assets' / 'license.rtf'}" />
    
  </Product>
</Wix>'''

    # Write WiX file
    wxs_path = output_dir / "Product.wxs"
    wxs_path.write_text(wxs_content, encoding='utf-8')
    
    # Compile
    log("[Build] Compiling WiX source...")
    result = subprocess.run(
        ['candle.exe', str(wxs_path), '-ext', 'WixUIExtension'],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        error("Failed to compile WiX source")
        print(result.stderr)
        return None
    success("Compiled Product.wxs")
    
    # Link
    msi_path = project_root / "dist" / f"BioInsight-v{VERSION}.msi"
    
    log("[Build] Linking MSI...")
    log("  (This may take a few minutes...)")
    result = subprocess.run(
        ['light.exe', str(output_dir / "Product.wixobj"),
         '-ext', 'WixUIExtension',
         '-out', str(msi_path),
         '-sval'],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        error("Failed to link MSI")
        print(result.stderr)
        return None
    
    size_mb = msi_path.stat().st_size / (1024 * 1024)
    success(f"Created MSI: {msi_path.name}")
    info(f"Size: {size_mb:.2f} MB")
    
    return str(msi_path)

def main():
    print("=" * 70)
    print("  BioInsight MSI Builder v5 (Direct File Inclusion)")
    print("=" * 70)
    
    project_root = Path(__file__).parent.absolute()
    dist_dir = project_root / "dist"
    output_dir = dist_dir / "msi_v5"
    staging_dir = dist_dir / "staging"
    
    # Check WiX
    log("\n[Check] WiX Toolset...")
    wix_path = check_wix()
    if not wix_path:
        error("WiX Toolset not found!")
        return False
    success(f"WiX found at: {wix_path}")
    
    # Build frontends
    build_frontends(project_root)
    
    # Clean staging
    if staging_dir.exists():
        shutil.rmtree(staging_dir, ignore_errors=True)
    staging_dir.mkdir(parents=True)
    
    # Copy files to staging
    log("\n[Build] Staging files...")
    
    # Backend (exclude SmolLM2 and database - will be auto-generated)
    backend_src = project_root / "backend"
    backend_dst = staging_dir / "backend"
    if backend_src.exists():
        def ignore_backend(dir, files):
            return [f for f in files if 'smollm2' in f.lower() or f.endswith('.gguf') 
                    or f == 'node_modules' or f == '__pycache__' or f == '.git'
                    or f.endswith('.db') or f == 'bioinsight.db']
        shutil.copytree(backend_src, backend_dst, ignore=ignore_backend)
        success("Staged backend (no SmolLM2)")
    
    # Central Dashboard (exclude node_modules)
    cd_src = project_root / "central-dashboard"
    cd_dst = staging_dir / "central-dashboard"
    if cd_src.exists():
        def ignore_cd(dir, files):
            return [f for f in files if f == 'node_modules' or f == '.git' or f == 'dist\dist']
        shutil.copytree(cd_src, cd_dst, ignore=ignore_cd)
        success("Staged central-dashboard")
    
    # PWA Client (exclude node_modules)
    pwa_src = project_root / "pwa-client"
    pwa_dst = staging_dir / "pwa-client"
    if pwa_src.exists():
        def ignore_pwa(dir, files):
            return [f for f in files if f == 'node_modules' or f == '.git' or f == 'dist\dist']
        shutil.copytree(pwa_src, pwa_dst, ignore=ignore_pwa)
        success("Staged pwa-client")
    
    # Copy README
    readme = project_root / "README.md"
    if readme.exists():
        shutil.copy(readme, staging_dir / "README.md")
    
    # Create installer files
    create_installer_files(staging_dir)
    
    # Collect all files
    log("\n[Build] Collecting all files...")
    all_files = []
    all_files.extend(collect_files(staging_dir / "backend", "backend\\"))
    all_files.extend(collect_files(staging_dir / "central-dashboard", "central-dashboard\\"))
    all_files.extend(collect_files(staging_dir / "pwa-client", "pwa-client\\"))
    all_files.append((staging_dir / "README.md", "README.md"))
    all_files.append((staging_dir / "install.bat", "install.bat"))
    all_files.append((staging_dir / "start.bat", "start.bat"))
    
    info(f"Total files: {len(all_files)}")
    
    # Setup build directory
    if output_dir.exists():
        shutil.rmtree(output_dir, ignore_errors=True)
    output_dir.mkdir(parents=True)
    
    # Change to output dir for WiX (so relative paths work)
    original_cwd = os.getcwd()
    os.chdir(staging_dir)
    
    try:
        # Create MSI
        msi_path = create_msi(project_root, output_dir, all_files)
    finally:
        os.chdir(original_cwd)
    
    if not msi_path:
        return False
    
    # Success
    print("\n" + "=" * 70)
    print("  BUILD SUCCESSFUL!")
    print("=" * 70)
    print(f"\n  Installer: {msi_path}")
    print(f"\n  Features:")
    print(f"    ✓ All files included directly (no extraction)")
    print(f"    ✓ Frontends pre-built")
    print(f"    ✓ Database in AppData")
    print(f"    ✓ SmolLM2 auto-downloads")
    print(f"    ✓ Python/Node auto-install")
    print(f"\n  To install:")
    print(f"    msiexec /i \"{msi_path}\"")
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
