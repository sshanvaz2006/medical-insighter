@echo off
REM Setup script for Medical Insight Engine (Windows)
REM Run this script to set up the entire project

setlocal enabledelayedexpansion

echo ================================
echo Medical Insight Engine Setup
echo ================================
echo.

REM Check prerequisites
echo Checking prerequisites...

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed. Please install Python 3.9+
    exit /b 1
)

npm --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: npm is not installed. Please install Node.js 16+
    exit /b 1
)

echo Prerequisites check passed!
echo.

REM Backend Setup
echo Setting up Backend...
cd backend

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Download spacy model
echo Downloading spacy models...
python -m spacy download en_core_web_sm

REM Create .env if not exists
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo Please edit backend\.env and set your database credentials
)

REM Create directories
if not exist "logs" mkdir logs
if not exist "uploads" mkdir uploads

echo Backend setup complete!
echo.

REM Frontend Setup
echo Setting up Frontend...
cd ..\frontend

REM Install dependencies
echo Installing npm dependencies...
call npm install

REM Create .env if not exists
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
)

echo Frontend setup complete!
echo.

REM Final instructions
echo ================================
echo Setup Complete!
echo ================================
echo.
echo Next steps:
echo.
echo 1. Configure Backend:
echo    Edit backend\.env and set:
echo    - DATABASE_URL (PostgreSQL connection)
echo    - SECRET_KEY and ENCRYPTION_KEY
echo    - CORS_ORIGINS (your frontend URL)
echo.
echo 2. Start Backend:
echo    cd backend
echo    venv\Scripts\activate.bat
echo    python -m uvicorn app.main:app --reload --port 8000
echo.
echo 3. In another terminal, Start Frontend:
echo    cd frontend
echo    npm run dev
echo.
echo 4. Access the application:
echo    Frontend: http://localhost:5173
echo    Backend API Docs: http://localhost:8000/api/docs
echo.
echo Happy coding!
echo.

endlocal
