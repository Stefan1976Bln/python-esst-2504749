# MatchQuest Backend (in der App enthalten)

Dieser `api/`-Ordner liegt **innerhalb** der Web-App. Dadurch genügt **ein einziger Ordner-Upload**
(`webapp/`) — die App findet das Backend automatisch unter `./api/api.php` (relativ) und teilt dann
Konten, Punkte, Ranglisten und Teams **über alle Geräte**.

## Zero-Config (empfohlen für den schnellen Start)
- **Standard = SQLite** → **kein Datenbank-Setup nötig.** Beim ersten Aufruf legt `db.php` die Datei
  `api/data/matchquest.sqlite` automatisch an (der `data/`-Ordner ist per `.htaccess` gegen Web-Zugriff geschützt).
- Voraussetzung: PHP mit `pdo_sqlite` (auf IONOS-Webhosting üblich aktiv).
- Läuft der Backend-Aufruf mal nicht, fällt die App automatisch in den **Lokal-Modus** zurück — niemand bleibt hängen.

## Optional: MySQL statt SQLite
`config.sample.php` → **`config.php`** kopieren, MySQL-Daten aus dem IONOS-Kundenmenü eintragen,
`allow_origin` auf die eigene Domain setzen. `config.php` wird nicht ins Git übernommen.

## Test (ohne IONOS, lokal)
```
php -S 127.0.0.1:8291 -t ..        # den webapp-Ordner servieren
curl 127.0.0.1:8291/api/api.php -d '{"action":"ping"}'   # -> {"ok":true}
```
Automatischer E2E-Test: `../../tests/backend_e2e.mjs` (2 Geräte → geteiltes Leaderboard & Team-Battle).

## Sicherheit
- Passwörter mit `password_hash()`, Login-Token zufällig. Prepared Statements (PDO).
- `submit` überträgt die aktuellen Punktestände (local-first) mit Deckelung gegen offensichtlichen Missbrauch.
- **HTTPS Pflicht.** Für Produktion `allow_origin` einschränken (nicht `*`) — am einfachsten via `config.php`.
