@echo off
setlocal
cd /d "%~dp0\.."

echo ===================================================
echo        Starting VeritasRAG Terminal CLI
echo ===================================================

set VENV_PYTHON=.venv\Scripts\python.exe

if exist "%VENV_PYTHON%" (
    echo [INFO] Found project virtual environment at .venv
    "%VENV_PYTHON%" veritas_cli.py
) else (
    echo [WARNING] .venv\Scripts\python.exe not found. Trying system python...
    python veritas_cli.py
)

pause
