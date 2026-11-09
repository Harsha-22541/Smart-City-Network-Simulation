@echo off
REM ==============================================================================
REM Windows Execution Script
REM Project: Smart City Network Simulation and Congestion Analysis
REM ==============================================================================

echo ======================================================================
echo    Starting Smart City Network Simulation and Congestion Analysis
echo ======================================================================

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in PATH. Please install Python 3.8+.
    pause
    exit /b 1
)

python run_analysis.py

echo.
echo ======================================================================
echo    Execution Complete. Graphs are saved in results\graphs\
echo ======================================================================
pause
