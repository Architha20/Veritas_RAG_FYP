@echo off
setlocal
cd /d "%~dp0"

echo ===================================================
echo        Starting VeritasRAG UI Server
echo ===================================================

set VENV_PYTHON=..\.venv\Scripts\python.exe

if exist "%VENV_PYTHON%" (
    echo [INFO] Found project virtual environment at ..\.venv
    echo [INFO] Launching UI server at http://127.0.0.1:8001 ...
    start http://127.0.0.1:8001/
    "%VENV_PYTHON%" -m uvicorn rag_api:app --host 127.0.0.1 --port 8001
) else (
    echo [WARNING] ..\.venv\Scripts\python.exe not found.
    echo [INFO] Trying system python...
    python -m uvicorn rag_api:app --host 127.0.0.1 --port 8001
)

pause
