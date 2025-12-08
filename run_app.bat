@echo off
echo ===================================================
echo   Dark Fantasy Book Generator - Startup Script
echo ===================================================

echo.
echo [1/2] Starting Backend Server (Port 8000)...
start "Backend Server" cmd /k "uvicorn backend.main:app --reload"

echo.
echo [2/2] Starting Frontend Server (Port 3000)...
cd frontend
start "Frontend Server" cmd /k "npm start"

echo.
echo ===================================================
echo   Servers are starting in separate windows.
echo   You can close this window now.
echo ===================================================
pause
