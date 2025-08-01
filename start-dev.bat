@echo off
echo 🚀 Starting Break-even Development Environment
echo.

echo 📋 Configuration:
echo - Frontend: http://localhost:3001
echo - Backend: http://localhost:5000
echo - MongoDB: mongodb://localhost:27017/breakeven
echo.

echo 🔍 Checking logo files...
cd /d "%~dp0scripts"
python test_logos.py
if errorlevel 1 (
    echo.
    echo ⚠️  Logo issues detected. Regenerating...
    python generate_logo512.py
)

echo.
echo 🖥️  Starting Backend Server...
cd /d "%~dp0backend"
start "Break-even Backend" cmd /k "python run.py"

echo.
echo 🌐 Starting Frontend Server...
cd /d "%~dp0frontend"
start "Break-even Frontend" cmd /k "npm run start:3001"

echo.
echo ✅ Development servers starting...
echo 📱 Frontend will be available at: http://localhost:3001
echo 🔌 Backend API available at: http://localhost:5000
echo.
echo Press any key to exit this window...
pause >nul
