@echo off
echo 🔧 Fixing Break-even Backend Registration Issues...
echo.

cd /d "%~dp0"

echo 📝 Running User model test...
python test_user_model.py
echo.

echo 🛑 Stopping any existing backend processes...
taskkill /f /im python.exe 2>nul

echo.
echo 🚀 Starting Backend with fixes...
echo Press Ctrl+C to stop the server
python run.py

pause
