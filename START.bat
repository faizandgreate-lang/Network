@echo off
cd /d "%~dp0"
echo Installing first time only...
python --version >nul 2>&1
if errorlevel 1 (
  echo Install Python from https://www.python.org/downloads/
  pause
  exit /b 1
)
if not exist .venv python -m venv .venv
call .venv\Scripts\activate.bat
pip install -q -r requirements.txt
set BIND=0.0.0.0
set PORT=5080
set AUTO_SCAN_MINUTES=0
echo.
python server\main.py
pause
