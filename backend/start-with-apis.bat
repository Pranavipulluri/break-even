@echo off
echo 🚀 Starting Break-even Backend with AI APIs...
echo.

cd /d "%~dp0"

echo 🧪 Testing backend configuration...
python test_backend.py
echo.

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Backend test failed. Please check the errors above.
    pause
    exit /b 1
)

echo 🔧 Installing required packages...
pip install requests

echo.
echo 🚀 Starting server on http://localhost:5000...
echo.
echo APIs Available:
echo - POST /api/ai-tools/gemini/generate-content
echo - POST /api/ai-tools/gemini/business-description
echo - POST /api/ai-tools/gemini/website-content
echo - POST /api/ai-tools/netlify/deploy-website
echo - POST /api/ai-tools/github/create-website
echo.
echo Press Ctrl+C to stop the server
echo.

python run.py

pause
