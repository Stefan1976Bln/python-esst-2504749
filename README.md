# AG City Berlin - Mitglieder- & Veranstaltungsverwaltung

Prototyp fuer die AG City Berlin e.V. zur Verwaltung von Mitgliedsunternehmen, Ansprechpartnern, Veranstaltungen (City-Talk, Stammtisch, KTS Fruehstueck), Anmeldungen mit Scoring und KI-gestuetzten Analysen.

## Quick Start (Windows)

```cmd
git clone https://github.com/Stefan1976Bln/python-esst-2504749.git
cd python-esst-2504749
git checkout claude/deploy-hetzner-prototype-HEeBo
start.bat
```

**Voraussetzung:** Python 3.10+ installiert und in PATH.

Dann im Browser: **http://localhost:8500**
Login: `admin` / `admin123`

## Quick Start (Linux/Mac)

```bash
git clone https://github.com/Stefan1976Bln/python-esst-2504749.git
cd python-esst-2504749
git checkout claude/deploy-hetzner-prototype-HEeBo
bash start.sh
```

## Erster Start / Daten laden

1. Server starten (start.bat / start.sh)
2. Einloggen als admin/admin123
3. **Unternehmen -> CSV Import**: CRM-Export (Semikolon-getrennt) hochladen
4. **Veranstaltungen**: City-Talk Events sind vorgeladen (54 echte Events 2022-2026)
5. **WP-Import**: Wordpress Teilnehmer-CSVs je Veranstaltung importieren

## Features

### Unternehmensverwaltung
- CRUD mit CRM-kompatiblen Feldern (Firma, Firma2, Firma3, Strasse, PLZ, Ort, Staat, Branche, Beitrag, CRM-ID, Eintrittsdatum, Austrittsdatum)
- Ansprechpartner mit Anrede, Titel, Position, Abteilung, Telefon, Durchwahl, Mobil, Geburtstag
- Dossiers / Notizen pro Unternehmen und Ansprechpartner
- CSV-Import fuer Bulk-Upload aus CRM-System (Semikolon-getrennt, Encoding-Auto-Detection)
- Loeschen direkt aus der Liste oder Detailansicht

### Veranstaltungsmanagement
- Veranstaltungstypen: City-Talk, Stammtisch, KTS Fruehstueck, Workshop, Networking, Seminar, Gala, Konferenz, Messe
- Bilderupload mit automatischer Groessenanpassung
- Wordpress-Anmeldelink (extern) statt internem Anmeldeformular
- 54 echte City-Talk Events der AG City Berlin (2022-2026)

### Anmelde-Workflow (Wordpress Integration)
- Anmeldungen laufen ueber Wordpress (agcity.de)
- **WP CSV-Import** (`/events/{id}/wp-import`): Wordpress-Export hochladen
  - Fuzzy-Matching gegen CRM-Datenbank (difflib, Schwelle 0.75)
  - Automatische Zuordnung bei >75% Uebereinstimmung
  - Manuelle Zuordnung bei Tippfehlern/Abweichungen
  - Unterstuetzt Komma- und Semikolon-Trennung, sep=-Zeile wird entfernt
  - Begleitpersonen werden automatisch erfasst
- Status-Workflow: Angemeldet -> Zugelassen/Abgelehnt/Warteliste -> Attended/No-Show

### Check-In Maske (`/events/{id}/checkin`)
- Tablet-optimiert fuer den Empfang
- Grosse Touch-Buttons zum Einchecken
- Suchfeld zum schnellen Finden
- Walk-In Erfassung neuer Teilnehmer
- Veranstaltung abschliessen -> alle nicht eingecheckten als No-Show

### Scoring & Zulassung (`/events/{id}/scoring`)
- Priority-Score (0-100) mit 5 Kriterien:
  - Zuverlaessigkeit (30 Punkte): No-Show-Quote
  - Mitgliedsstatus (25 Punkte): Aktives Mitglied + Beitrag bezahlt
  - Engagement (20 Punkte): Anzahl besuchter Events
  - Fairness (15 Punkte): Wer laenger nicht dran war, wird bevorzugt
  - Branchen-Diversitaet (10 Punkte): Branchenmix foerdern
- Score-Erklaerung pro Anmeldung
- "Top N zulassen" Bulk-Aktion

### Teilnahme nachpflegen (`/events/{id}/attendance`)
- Fuer vergangene Events nachtraeglich markieren (Anwesend/No-Show)
- "Alle Zugelassenen als No-Show markieren" fuer Abschluss

### Veranstaltungs-Analyse (`/events/{id}/analysis`)
- Teilnahmequote, No-Show-Quote
- Branchenverteilung der Teilnehmer
- Mitglieder vs. Nicht-Mitglieder
- No-Show Unternehmen Liste

### Mitgliedsbeitraege (`/fees`)
- Jahresweise Uebersicht
- Zahlungen erfassen
- Status: Offen, Teilweise, Bezahlt, Ueberfaellig

### KI-Analysen (`/ai/insights`)
- Zuverlaessigkeits-Score pro Person (No-Show-Verhalten)
- Passungs-Score (Teilnehmer <-> Veranstaltung)
- Engagement-Score pro Unternehmen
- Churn-Risiko-Prognose
- Automatische Veranstaltungs-Zusammenfassungen
- **Hinweis:** Benoetigt Claude API Key (CLAUDE_API_KEY in .env). Funktioniert auch ohne mit Fallback-Berechnung.

## Seiten-Uebersicht

| URL | Funktion |
|-----|----------|
| `/dashboard` | KPI-Dashboard mit Statistiken |
| `/companies` | Unternehmensliste |
| `/companies/new` | Neues Unternehmen anlegen |
| `/companies/{id}` | Unternehmensdetail (Kontakte, Dossiers, Beitraege) |
| `/import` | CRM CSV-Import fuer Unternehmen/Ansprechpartner |
| `/events` | Veranstaltungsliste |
| `/events/new` | Neue Veranstaltung anlegen |
| `/events/{id}` | Veranstaltungsdetail mit Anmeldungen |
| `/events/{id}/wp-import` | Wordpress CSV-Import mit Fuzzy-Matching |
| `/events/{id}/checkin` | Tablet Check-In Maske |
| `/events/{id}/scoring` | Score-Berechnung + Rangfolge + Zulassen |
| `/events/{id}/attendance` | Teilnahme nachpflegen |
| `/events/{id}/analysis` | Veranstaltungs-Auswertung |
| `/fees` | Mitgliedsbeitraege Uebersicht |
| `/ai/insights` | KI-Analysen Dashboard |

## Tech-Stack

- **Backend**: Python 3.10+, FastAPI 0.115, SQLAlchemy 2.0, SQLite (WAL mode)
- **Frontend**: Jinja2 Templates, Bootstrap 5.3, HTMX 2.0, Bootstrap Icons
- **KI**: Claude API (Anthropic) - optional
- **Deployment**: Docker + Nginx oder lokal via uvicorn mit --reload

## Projektstruktur

```
app/
  main.py              # FastAPI App, Router-Registrierung
  config.py            # Konfiguration (.env)
  database.py          # SQLAlchemy Engine, Session
  models/
    company.py         # Company, ContactPerson, Dossier
    event.py           # Event, EventImage
    registration.py    # EventRegistration (Status, Scoring, Attendance)
    membership.py      # MembershipFee, PaymentRecord
    user.py            # AdminUser
    ai.py              # AIScore, EmailLog
  routers/
    admin_auth.py      # Login/Logout
    dashboard.py       # Dashboard KPIs
    companies.py       # Unternehmen CRUD + Kontakte + Dossiers
    events.py          # Veranstaltungen CRUD + Bilder
    event_checkin.py   # WP-Import, Check-In, Walk-In, Teilnehmer-Verwaltung
    event_analysis.py  # Scoring, Attendance, Analyse
    fees.py            # Mitgliedsbeitraege
    ai_api.py          # KI-Analyse Endpoints
    csv_import.py      # CRM CSV-Import
    public.py          # Oeffentliche Seiten
  services/
    email.py           # SMTP E-Mail-Versand
    ai_analysis.py     # Claude API Integration
    scoring.py         # Priority-Score Berechnung
  templates/           # Jinja2 HTML (Bootstrap 5)
  static/
    css/custom.css     # AG City Branding (Rot #c0392b)
    js/app.js          # Minimales JS (HTMX uebernimmt Interaktionen)
    img/               # Logo, Favicon
scripts/
  seed_data.py         # Erstellt DB mit echten City-Talk Events
nginx/
  default.conf         # Nginx Reverse Proxy Config
Dockerfile             # Python 3.12-slim Container
docker-compose.yml     # App + Nginx
start.bat              # Windows Startscript
start.sh               # Linux/Mac Startscript
```

## Konfiguration (.env)

```
DATABASE_URL=sqlite:///data/agcity.db    # oder PostgreSQL fuer Produktion
SECRET_KEY=change-me-to-random-string
PORT=8500
CLAUDE_API_KEY=sk-ant-...                # Optional fuer KI-Features
SMTP_HOST=smtp.example.com               # Optional fuer E-Mail
SMTP_PORT=587
SMTP_USER=...
SMTP_PASSWORD=...
SMTP_FROM=noreply@agcity.de
BASE_URL=http://localhost:8500
ADMIN_DEFAULT_PASSWORD=admin123
```

## Datenbank zuruecksetzen

```cmd
del data\agcity.db
start.bat
```

Die Datenbank wird automatisch neu erstellt mit Admin-User und City-Talk Events.

## Docker Deployment (Hetzner/Produktion)

```bash
cp .env.example .env  # Werte anpassen
docker compose up -d --build
```

## Weiterentwicklung

- **Neue Veranstaltungstypen**: In `app/routers/events.py` die `EVENT_TYPES` Liste erweitern
- **Scoring anpassen**: In `app/services/scoring.py` die Gewichte und Kriterien aendern
- **Neue Felder**: In `app/models/*.py` ergaenzen, `data/agcity.db` loeschen (oder Alembic fuer Migration)
- **PostgreSQL**: In `.env` die `DATABASE_URL` auf PostgreSQL aendern, Rest bleibt gleich
