#!/bin/bash
# ============================================================
# AG City Prototyp - Lokales Start-Script
# Fuer DGX Spark oder jeden anderen lokalen Rechner
# Port: 8500 (konfigurierbar via PORT env var)
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

PORT="${PORT:-8500}"
HOST="${HOST:-0.0.0.0}"

echo "============================================"
echo "  AG City Verwaltungsplattform"
echo "  http://localhost:${PORT}"
echo "============================================"

# Create data directory
mkdir -p data/uploads/events

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo ""
    echo ">> Erstelle virtuelle Umgebung..."
    python3 -m venv .venv
fi

# Activate venv
source .venv/bin/activate

# Install dependencies
echo ">> Installiere Abhaengigkeiten..."
pip install -q -r requirements.txt

# Seed demo data if database doesn't exist
if [ ! -f "data/agcity.db" ]; then
    echo ">> Erstelle Datenbank mit Demo-Daten..."
    python scripts/seed_data.py
    echo ""
    echo ">> Demo-Login: admin / admin123"
fi

echo ""
echo ">> Starte Server auf Port ${PORT}..."
echo ">> Oeffne im Browser: http://localhost:${PORT}"
echo ">> Stoppen mit Ctrl+C"
echo ""

# Start the FastAPI server
uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
