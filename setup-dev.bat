@echo off
echo Setting up Break-Even Application for Development...
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Node.js is not installed. Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "netlify.toml" (
    echo Error: netlify.toml not found. Please run this script from the break-even directory.
    pause
    exit /b 1
)

echo Step 1: Installing Netlify CLI globally...
npm install -g netlify-cli

echo Step 2: Installing frontend dependencies...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo Error: Failed to install frontend dependencies
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

echo Step 4: Creating .env file template...
if not exist ".env" (
    echo Creating .env file template...
    echo # MongoDB Configuration > .env
    echo MONGODB_URI=mongodb://localhost:27017 >> .env
    echo. >> .env
    echo # JWT Configuration >> .env
    echo JWT_SECRET=your-super-secret-jwt-key-change-this-in-production >> .env
    echo. >> .env
    echo # Application Configuration >> .env
    echo NODE_ENV=development >> .env
    echo. >> .env
    echo .env file created! Please update the values as needed.
)

echo.
echo Development setup complete!
echo.
echo Next steps:
echo 1. Update the .env file with your MongoDB connection string
echo 2. Run 'netlify dev' to start the development server
echo 3. Access the application at http://localhost:8888
echo.
echo To deploy to Netlify, run: deploy-netlify.bat
echo.
pause
