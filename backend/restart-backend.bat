@echo off
echo 🔄 Restarting Backend with updated CORS settings...
echo.

cd /d "%~dp0"

echo 🛑 Stopping any existing backend processes...
taskkill /f /im python.exe 2>nul

echo.
echo 🚀 Starting Backend with CORS for ports 3000-3003...
python run.py

pause
