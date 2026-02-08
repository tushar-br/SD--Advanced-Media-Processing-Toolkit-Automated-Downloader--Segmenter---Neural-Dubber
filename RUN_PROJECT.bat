@echo off
setlocal
title Media Toolkit (Localhost:5000)

REM ==========================================
REM PERFECT LOCAL RUNNER (REACT + PYTHON)
REM ==========================================

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

REM 1. PYTHON CHECK
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python.
    pause
    exit /b 1
)

REM 2. DEPENDENCIES CHECK
if not exist "backend\installed.flag" (
    echo [INFO] Installing Dependencies...
    cd backend
    pip install -r requirements.txt
    echo done > installed.flag
    cd /d "%PROJECT_ROOT%"
)

REM ALWAYS UPDATE YT-DLP (Important for YouTube fixes)
echo [INFO] Checking for yt-dlp updates...
pip install --upgrade yt-dlp --quiet

REM 3. OPEN BROWSER (Wait a bit for server)
echo [INFO] Opening http://localhost:5000...
start "" "http://localhost:5000"

REM 4. START SERVER (Main Loop)
echo.
echo ==========================================
echo    SERVER IS STARTING...
echo    DO NOT CLOSE THIS WINDOW.
echo    Go to browser: http://localhost:5000
echo ==========================================
echo.

cd backend
python app.py

REM 5. ERROR CATCH (If crashed)
if errorlevel 1 (
    echo.
    echo [CRITICAL ERROR] Server stopped or crashed.
    echo check the error message above.
    pause
)
pause
