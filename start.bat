@echo off
REM TikTok Live AI Avatar - Windows Startup Script

echo.
echo Starting TikTok Live AI Avatar Application...
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js is not installed. Please install Node.js first.
    pause
    exit /b 1
)

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed. Please install Python first.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo WARNING: .env file not found.
    if exist .env.example (
        copy .env.example .env
        echo Created .env file. Please edit it with your API keys.
    ) else (
        echo ERROR: .env.example not found. Please create .env manually.
    )
)

REM Install Node.js dependencies if needed
if not exist node_modules (
    echo Installing Node.js dependencies...
    call npm install
)

REM Install Python dependencies
echo Checking Python dependencies...
pip install -r requirements.txt -q

echo.
echo Starting servers...
echo.

REM Start Python server in new window
echo Starting Python AI Avatar Server...
start "Python AI Server" python3.11 avatar_server.py

REM Wait a bit for Python server to start
timeout /t 3 /nobreak >nul

REM Start Node.js server in new window
echo Starting Node.js Server...
start "Node.js Server" node server.js

echo.
echo Servers started successfully!
echo.
echo Open your browser and go to: http://localhost:3000
echo.
echo Close the server windows to stop the application.
echo.
pause

