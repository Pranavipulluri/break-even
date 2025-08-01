@echo off
echo 🌐 Starting Break-even Frontend...
echo Note: React will automatically use next available port if 3001 is taken
echo.

cd /d "%~dp0"
set PORT=3001
npm start

echo.
echo 📱 Frontend started! Check the terminal output for the actual port.
echo 🔗 If running on port 3002, the URL will be: http://localhost:3002
pause
