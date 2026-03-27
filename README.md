# AG City - Mitglieder- & Veranstaltungsverwaltung

Prototyp fuer die Verwaltung von Mitgliedsunternehmen, Ansprechpartnern, Veranstaltungen und KI-gestuetzte Analysen.

## Quick Start (Lokal / DGX Spark)

```bash
git clone <repo-url>
cd python-esst-2504749

# Einzeiler-Start (Port 8500):
bash start.sh

# Oder mit anderem Port:
PORT=9000 bash start.sh
```

Dann im Browser: **http://localhost:8500**
Login: `admin` / `admin123`

## Features

- **Unternehmensverwaltung**: CRUD mit Kontaktdaten, Ansprechpartnern, Dossiers
- **Mitgliedsbeitraege**: Jahresbeitraege, Zahlungen, Status-Tracking
- **Veranstaltungsmanagement**: Anlage, Bilder, Typen, oeffentlicher Anmeldelink
- **Oeffentliche Anmeldung**: Per Link (ohne Login), automatische Eingangsbestaetigung
- **Genehmigungs-Workflow**: Manuelles Bestaetigen/Ablehnen von Anmeldungen
- **Teilnahme-Tracking**: Anwesenheit / No-Show Historie
- **KI-Analysen** (Claude API):
  - Zuverlaessigkeits-Score (No-Show-Verhalten)
  - Passungs-Score (Teilnehmer <-> Veranstaltung)
  - Engagement-Score pro Unternehmen
  - Churn-Risiko-Prognose
  - Automatische Veranstaltungs-Zusammenfassungen
  - Personalisierte Veranstaltungsempfehlungen

## Tech-Stack

- **Backend**: Python, FastAPI, SQLAlchemy, SQLite
- **Frontend**: Jinja2, Bootstrap 5, HTMX
- **KI**: Claude API (Anthropic)
- **Deployment**: Docker + Nginx oder lokal via uvicorn

## Konfiguration

Kopiere `.env.example` nach `.env` und passe die Werte an:

```bash
cp .env.example .env
```

Wichtige Variablen:
- `PORT` - Server-Port (Standard: 8500)
- `CLAUDE_API_KEY` - Fuer KI-Features (optional, funktioniert auch ohne)
- `SMTP_*` - Fuer E-Mail-Versand (optional, wird geloggt wenn nicht konfiguriert)

## Docker Deployment (Hetzner Server)

```bash
cp .env.example .env
# .env anpassen
docker compose up -d --build
```

## Projektstruktur

```
app/
  main.py            # FastAPI App
  config.py          # Konfiguration
  database.py        # SQLAlchemy Setup
  models/            # Datenbank-Modelle
  routers/           # API Routes (admin + public)
  services/          # Email, KI-Analyse
  templates/         # Jinja2 HTML Templates
  static/            # CSS, JS
scripts/
  seed_data.py       # Demo-Daten
```
