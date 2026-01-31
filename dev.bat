@echo off
REM Development script - Starts both backend and frontend (Windows)
REM Usage: dev.bat

echo Starting Medical Insight Engine in development mode...
echo.

echo Starting Backend on port 8000...
echo.
start cmd /k "cd backend && venv\Scripts\activate.bat && python -m uvicorn app.main:app --reload --port 8000"

timeout /t 3 /nobreak

echo Starting Frontend on port 5173...
echo.
start cmd /k "cd frontend && npm run dev"

echo.
echo ================================
echo Both services are running!
echo ================================
echo.
echo Frontend:  http://localhost:5173
echo Backend:   http://localhost:8000
echo API Docs:  http://localhost:8000/api/docs
echo.
echo Close the terminal windows to stop the services.
