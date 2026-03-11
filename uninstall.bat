@echo off
echo.
echo   Starting eesti.ai cleanup...
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0uninstall.ps1"
