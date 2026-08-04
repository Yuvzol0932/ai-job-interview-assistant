@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found.
    echo Please create it first:
    echo   python -m venv .venv
    echo   .venv\Scripts\python -m pip install -r requirements.txt
    pause
    exit /b 1
)

echo Starting AI Job Interview Assistant...
echo If the browser does not open automatically, visit: http://localhost:8501
echo Close this black window to stop the app.
".venv\Scripts\python.exe" -m streamlit run app.py
pause
