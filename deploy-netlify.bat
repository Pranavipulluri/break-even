@echo off
echo Starting Break-Even Application Deployment...
echo.

REM Check if Netlify CLI is installed
netlify --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Netlify CLI...
    npm install -g netlify-cli
)

REM Check if we're in the right directory
if not exist "netlify.toml" (
    echo Error: netlify.toml not found. Please run this script from the break-even directory.
    pause
    exit /b 1
)

echo Step 1: Installing frontend dependencies...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo Error: Failed to install frontend dependencies
    pause
    exit /b 1
)

echo Step 2: Building frontend...
call npm run build
if %errorlevel% neq 0 (
    echo Error: Failed to build frontend
    pause
    exit /b 1
)
cd ..

echo Step 3: Installing Netlify function dependencies...
cd netlify-functions
call npm install
if %errorlevel% neq 0 (
    echo Error: Failed to install function dependencies
    pause
    exit /b 1
)
cd ..

echo Step 4: Logging into Netlify (if not already logged in)...
netlify status
if %errorlevel% neq 0 (
    echo Please log into Netlify...
    netlify login
)

echo Step 5: Deploying to Netlify...
echo Choose deployment option:
echo [1] Deploy draft (for testing)
echo [2] Deploy to production
set /p choice="Enter choice (1 or 2): "

if "%choice%"=="1" (
    echo Deploying draft version...
    netlify deploy
) else if "%choice%"=="2" (
    echo Deploying to production...
    netlify deploy --prod
) else (
    echo Invalid choice. Deploying draft version...
    netlify deploy
)

echo.
echo Deployment complete!
echo.
echo IMPORTANT: Don't forget to set these environment variables in your Netlify dashboard:
echo - MONGODB_URI: Your MongoDB connection string
echo - JWT_SECRET: A secure secret key for JWT tokens
echo.
echo Access your Netlify dashboard at: https://app.netlify.com/
echo.
pause
