@echo off
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

cd /d "%~dp0backend"
start "BioInsight Backend" python -m app.main

echo Starting services...
timeout /t 5 /nobreak >nul

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
echo Press any key to open the dashboard in your browser...
pause >nul
start http://localhost:5173
echo.
echo Press Ctrl+C in the backend window to stop the server.
pause
