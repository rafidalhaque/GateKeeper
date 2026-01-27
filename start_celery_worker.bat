@echo off
REM Celery Worker Startup Script for GateKeeper
REM This script starts the Celery worker for background task processing

echo ========================================
echo  GateKeeper Celery Worker
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv .venv
    echo Then install requirements: .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Check if Redis is running
echo Checking Redis connection...
redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Redis is not responding!
    echo Please start Redis first:
    echo   - redis-server
    echo   - or: docker run -d -p 6379:6379 redis:alpine
    echo.
    pause
    exit /b 1
)
echo Redis is running!
echo.

REM Start Celery worker
echo Starting Celery worker...
echo Press Ctrl+C to stop
echo.
celery -A celery_worker worker --loglevel=info --pool=solo

pause
