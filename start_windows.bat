@echo off
set VENV_DIR=venv

if not exist "%VENV_DIR%\Scripts\python.exe" (
    python -m venv "%VENV_DIR%"
)

"%VENV_DIR%\Scripts\python.exe" -c "import PySide6" >nul 2>&1
if errorlevel 1 (
    "%VENV_DIR%\Scripts\python.exe" -m pip install PySide6
)

"%VENV_DIR%\Scripts\python.exe" app.py