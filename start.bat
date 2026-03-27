@echo off
REM ============================================================
REM AG City Prototyp - Windows Start-Script
REM Port: 8500
REM ============================================================

echo ============================================
echo   AG City Verwaltungsplattform
echo   http://localhost:8500
echo ============================================

REM Create data directory
if not exist "data\uploads\events" mkdir data\uploads\events

REM Check if virtual environment exists
if not exist ".venv" (
    echo.
    echo ^>^> Erstelle virtuelle Umgebung...
    python -m venv .venv
)

REM Activate venv
call .venv\Scripts\activate.bat

REM Install dependencies
echo.
echo ^>^> Installiere Abhaengigkeiten...
pip install -q -r requirements.txt

REM Seed demo data if database doesn't exist
if not exist "data\agcity.db" (
    echo.
    echo ^>^> Erstelle Datenbank mit Demo-Daten...
    python scripts\seed_data.py
    echo.
    echo ^>^> Demo-Login: admin / admin123
)

echo.
echo ^>^> Starte Server auf Port 8500...
echo ^>^> Oeffne im Browser: http://localhost:8500
echo ^>^> Stoppen mit Ctrl+C
echo.

uvicorn app.main:app --host 0.0.0.0 --port 8500 --reload
