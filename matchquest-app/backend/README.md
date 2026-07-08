# MatchQuest Backend (IONOS PHP + MySQL)

Schlanke JSON-API für **echt geteilte** Konten, Punkte, Ranglisten und Teams — damit alle
geräteübergreifend gegeneinander spielen. Ohne dieses Backend läuft die App im reinen Lokal-/Demo-Modus.

## Dateien
| Datei | Zweck |
|-------|-------|
| `api.php` | Einzelne JSON-API (`POST {action, …}`): register, login, me, submit, joinTeam, leaderboard, teams |
| `db.php` | PDO-Verbindung + automatische Tabellen-Migration (MySQL **oder** SQLite) |
| `config.sample.php` | Vorlage — nach `config.php` kopieren und ausfüllen (Passwörter, DB) |

`config.php` und `*.sqlite` sind per `.gitignore` ausgeschlossen (keine Secrets ins Repo).

## Einrichten auf IONOS
1. Im IONOS-Kundenmenü eine **MySQL-Datenbank** anlegen → Host, DB-Name, Benutzer, Passwort notieren.
2. `config.sample.php` → **`config.php`** kopieren, `driver` auf `'mysql'` lassen und die MySQL-Daten eintragen.
   `allow_origin` auf die eigene Domain setzen, z. B. `https://www.altenau-harz.de`.
3. Den Ordner `backend/` per FTP in einen Unterordner laden, z. B. **`…/matchquest-api/`**
   (getrennt von der App unter `…/matchquest/`).
4. Testen: `https://www.altenau-harz.de/matchquest-api/api.php` mit einem POST-Tool aufrufen
   (`{"action":"teams"}` sollte JSON liefern). Die Tabellen werden beim ersten Aufruf automatisch angelegt.

## Backend in der App aktivieren
In `matchquest.html` / `webapp/index.html` die Konstante setzen:
```js
var BACKEND_URL='https://www.altenau-harz.de/matchquest-api/api.php';
```
(oder ohne Code-Änderung im Browser: `localStorage.setItem('mqpro_backend','https://…/api.php')`).
Leer = Lokal-Modus.

## Sicherheit / Hinweise
- Passwörter werden mit `password_hash()` gespeichert; Login vergibt ein Zufalls-Token.
- `submit` überträgt die aktuellen Punktestände des Clients (local-first) mit einfacher Deckelung
  gegen offensichtlichen Missbrauch. Für kompetitive Turniere später serverseitige Verifikation ergänzen.
- **HTTPS Pflicht.** `allow_origin` in Produktion einschränken (nicht `*`).
- Getestet: `tests/backend_e2e.mjs` (2 Geräte → geteiltes Leaderboard & Team-Battle: 7/7 PASS,
  lokal gegen PHP+SQLite verifiziert; auf IONOS läuft dieselbe PDO-Schicht mit MySQL).
