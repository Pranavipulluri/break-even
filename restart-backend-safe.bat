@echo off
echo Stopping any existing Flask processes...
taskkill /f /im python.exe /t >nul 2>&1

echo Waiting for socket cleanup...
timeout /t 3 /nobreak >nul

echo Starting Flask backend...
cd /d "d:\my projects\break even\break-even\backend"

set FLASK_APP=run.py
set FLASK_ENV=development
set FLASK_DEBUG=1

python run.py

pause