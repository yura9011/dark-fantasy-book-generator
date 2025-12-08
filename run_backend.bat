@echo off
echo ===================================================
echo   Dark Fantasy Book Generator - Backend Server
echo ===================================================
echo.
echo Starting FastAPI Backend on Port 8000...
echo.
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause
