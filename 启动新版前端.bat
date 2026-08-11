@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================
echo  AI Job Interview Assistant - React Frontend
echo  Backend API : http://127.0.0.1:8000
echo  Frontend    : http://localhost:5173
echo ============================================

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found.
    echo Please run:
    echo   python -m venv .venv
    echo   .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

if not exist "web\node_modules" (
    echo [1/3] Installing frontend dependencies, please wait...
    pushd web
    call npm install
    popd
)

echo [1/3] Starting backend API...
start "AIJobAssistant-API" cmd /k ".venv\Scripts\python.exe -m uvicorn api.app:app --host 127.0.0.1 --port 8000"

echo [2/3] Starting frontend dev server...
start "AIJobAssistant-Web" cmd /k "cd /d web && npm run dev"

echo [3/3] Done. Open http://localhost:5173 in your browser.
echo Tip: close the two black windows to stop the app.
pause
endlocal
