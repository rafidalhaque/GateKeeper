@echo off
REM Stop existing Celery worker and restart with new configuration

echo ========================================
echo  RESTART CELERY WORKER
echo ========================================
echo.

cd /d "%~dp0"

echo Step 1: Checking for running Celery processes...
tasklist /FI "IMAGENAME eq python.exe" | find /I "python.exe" >nul
if %ERRORLEVEL% EQU 0 (
    echo Found Python processes. Please manually stop the Celery worker:
    echo 1. Go to the terminal running Celery
    echo 2. Press Ctrl+C to stop it
    echo 3. Wait for it to fully stop
    echo 4. Then run this script again
    echo.
    pause
    exit /b 1
)

echo No running Celery detected.
echo.

echo Step 2: Clearing Redis cache...
redis-cli FLUSHALL
if %ERRORLEVEL% EQU 0 (
    echo Redis cache cleared!
) else (
    echo Warning: Could not clear Redis cache
)
echo.

echo Step 3: Activating virtual environment...
call .venv\Scripts\activate.bat

echo Step 4: Starting Celery worker with NEW configuration...
echo.
echo Watch for these lines:
echo   [tasks]
echo     . app.services.tasks.generate_tickets_task
echo     . app.services.tasks.import_csv_task
echo     . app.services.tasks.send_bulk_emails_task
echo.
echo If you see all 3 tasks, it's working!
echo.
echo Press Ctrl+C to stop when needed
echo.

celery -A celery_worker worker --loglevel=info --pool=solo

pause
