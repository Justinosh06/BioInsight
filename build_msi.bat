@echo off
echo Building BioInsight MSI Installer...
echo.

REM Check if WiX Toolset is installed
where candle >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: WiX Toolset not found. Please install WiX Toolset first.
    echo Download from: https://wixtoolset.org/releases/
    pause
    exit /b 1
)

where light >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: WiX Toolset not found. Please install WiX Toolset first.
    echo Download from: https://wixtoolset.org/releases/
    pause
    exit /b 1
)

echo 1. Preparing build environment...
if not exist "build" mkdir build
if not exist "build\output" mkdir build\output

echo 2. Building backend...
cd backend
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt --target=..\build\dependencies
deactivate
cd ..

echo 3. Building central dashboard...
cd central-dashboard
call npm run build
xcopy /E /I dist "..\build\central-dashboard" 
cd ..

echo 4. Building PWA client...
cd pwa-client
call npm run build
xcopy /E /I dist "..\build\pwa-client"
cd ..

echo 5. Copying application files...
xcopy /E /I backend\app "..\build\backend\app"
xcopy /E /I backend\database "..\build\database"

echo 6. Compiling WiX source...
cd installer
candle Product.wxs -out "..\build\Product.wixobj"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to compile WiX source
    pause
    exit /b 1
)

echo 7. Linking MSI installer...
light Product.wixobj -out "..\build\output\BioInsight.msi"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to link MSI installer
    pause
    exit /b 1
)

echo.
echo SUCCESS! MSI installer created at: build\output\BioInsight.msi
echo.
echo To test the installer:
echo 1. Run build\output\BioInsight.msi
echo 2. Follow the installation wizard
echo 3. Check that all components are installed correctly
echo.
pause
