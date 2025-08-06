@echo off
REM Windows batch script for running OTel Collector diagnostics

echo ======================================================================
echo DYNATRACE OPENTELEMETRY COLLECTOR DIAGNOSTICS (WINDOWS)
echo ======================================================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

REM Change to script directory
cd /d "%~dp0"

REM Check if diagnostics script exists
if not exist "diagnostics.py" (
    echo ERROR: diagnostics.py not found in current directory
    echo Please ensure you're running this from the scripts/ directory
    pause
    exit /b 1
)

echo Running diagnostics...
echo.

REM Run diagnostics with error handling
python diagnostics.py %*
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Diagnostics failed to run
    echo Common solutions:
    echo - Ensure collector container is running: docker-compose up -d
    echo - Check if ports 13133 and 8888 are accessible
    echo - Verify network connectivity to localhost
)

echo.
echo ======================================================================
echo Diagnostics complete. Press any key to exit...
pause >nul