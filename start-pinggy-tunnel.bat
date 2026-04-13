@echo off
echo ============================================
echo BioInsight Pinggy SSH Tunnel
echo ============================================
echo.
echo This script creates a public HTTPS tunnel
echo to your local BioInsight backend (port 8000)
echo.
echo Requirements:
echo - OpenSSH installed (Windows 10/11 has it built-in)
echo - Backend running on localhost:8000
echo.
echo ============================================
echo.

REM Check if SSH is available
where ssh >nul 2>nul
if errorlevel 1 (
    echo ERROR: SSH command not found.
    echo Please install OpenSSH or use Git Bash.
    pause
    exit /b 1
)

echo Starting Pinggy tunnel with static URL...
echo Static URL: https://bioinsight.free.pinggy.io
echo Command: ssh -p 443 -R 80:localhost:5174 bioinsight@free.pinggy.io
echo.
echo The tunnel will be available at: https://bioinsight.free.pinggy.io/
echo ============================================
echo.

REM Start the SSH tunnel with static port 80
ssh -p 443 -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -o ExitOnForwardFailure=yes -R 80:localhost:5174 bioinsight@free.pinggy.io

echo.
echo ============================================
echo Tunnel closed.
pause
