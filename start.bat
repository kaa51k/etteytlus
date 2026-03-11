@echo off
echo.
echo   ========================================
echo     eesti.ai - e-etteytlus LIVE
echo   ========================================
echo.

:: Activate venv
if not exist "%~dp0venv\Scripts\activate.bat" (
    echo   ERROR: Virtual environment not found.
    echo   Run install.bat first!
    echo.
    pause
    exit /b 1
)

call "%~dp0venv\Scripts\activate.bat"

:: Check config
if not exist "%~dp0config.env" (
    echo   ERROR: config.env not found.
    echo   Copy config.env.example to config.env and edit it.
    echo.
    pause
    exit /b 1
)

echo   Starting pipeline...
echo   Web display: http://localhost:8080
echo   Press Ctrl+C to stop.
echo.

python "%~dp0src\pipeline.py"
pause
