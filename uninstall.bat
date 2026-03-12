@echo off
echo.
echo   Starting eesti.ai cleanup...
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0uninstall.ps1"
