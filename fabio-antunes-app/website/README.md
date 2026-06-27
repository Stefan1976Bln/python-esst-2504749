# Fabio Antunes Prime Coaching — Website & WebApp (Entwurf)

Premium-Website mit Kundenlogin, mobiler WebApp und Verwaltungsoberfläche für Fabio.
Gleiches Look & Feel wie der App-Prototyp (Gold `#CFAB47` / Schwarz `#000000`).

## Inhalt

| Datei | Zweck |
|-------|-------|
| `index.html` | Öffentliche Marketing-Website (Flyer-Inhalte: Hero, Methode, Pakete, Für wen, Ablauf, Über mich, FAQ, Kontakt) + Buchungs-Modal „Kostenloses Erstgespräch" |
| `login.html` | Login für Kunden **und** Fabio (rollenbasierte Weiterleitung) |
| `app.html` | **Kunden-WebApp** (mobil): Termine + Buchungskalender, Trainingsplan, Erfolge, Nachrichten an Fabio, Profil/Vertrag |
| `admin.html` | **Verwaltung für Fabio**: zentraler Buchungskalender, Neukunden-Anfragen, Mitglieder/Verträge, Nachrichten, E-Mail-Postausgang |
| `assets/site.css` | Gemeinsames Premium-Stylesheet (mobile-first) |
| `assets/auth.js` | Demo-Login + Datenmodell (localStorage) |
| `assets/site.js` | Landingpage-Interaktivität (Menü, FAQ, Buchungs-Modal) |
| `assets/app.js` | Kunden-WebApp-Logik |
| `assets/admin.js` | Verwaltungs-Logik |

## Test-Zugänge (Demo)

- **Coach / Admin:** Login `Fabio` · Passwort `Fabio123!` → `admin.html`
- **Testkunde:** `stefan-wittenberg@gmx.de` · Passwort `Fabio123!` → `app.html`

Passwörter sind im Profil änderbar. Demo-Daten zurücksetzen: in der Browser-Konsole `FA.resetDemo()` aufrufen.

## Wichtiger Hinweis: Demo vs. Live

Dies ist ein **statischer, voll durchklickbarer Entwurf**. Login, Buchungskalender,
Nachrichten und E-Mails laufen client-seitig über `localStorage` — d.h. die Daten
liegen nur im jeweiligen Browser und es wird **keine echte E-Mail** verschickt.
Stattdessen zeigt die App „E-Mail-Vorschauen" (im Admin-Bereich → *Postausgang*),
damit erkennbar ist, **was** live verschickt würde.

Das ist ideal, um das Konzept mit Fabio abzustimmen, **bevor** das echte Backend gebaut wird.

## Live-Schaltung auf Ionos (Phase 2)

Ionos Standard-Webhosting bietet **PHP + MySQL** (kein Node.js). Der Umbau ist bewusst
vorbereitet — die Datenzugriffe sind in `auth.js` (Objekt `FA.DB`) gekapselt und müssen
nur auf `fetch()`-Aufrufe an PHP-Endpunkte umgestellt werden.

**Geplante Struktur live:**

```
/                 → Website (index.html)
/login.php        → echtes Login (Session, gehashte Passwörter via password_hash)
/api/booking.php  → Termine lesen/anlegen/stornieren (MySQL)
/api/messages.php → Nachrichten
/api/leads.php    → Erstgespräch-Anfragen
/api/mail.php     → E-Mail-Versand (PHPMailer)
```

**MySQL-Tabellen (Minimalschema):** `users`, `appointments`, `messages`, `leads`, `mail_log`.

### E-Mail (Open-Source, empfohlen)

- **[PHPMailer](https://github.com/PHPMailer/PHPMailer)** (MIT-Lizenz) über den **Ionos-eigenen SMTP-Server**
  mit Absender `info@fabioantunes.de` / `fabioantunesprimecoaching@gmail.com`.
  Keine externen Dienstleister, DSGVO-freundlich, im Hosting-Tarif enthalten.
- Automatische Mails: Erstgespräch-Bestätigung an Interessent, Benachrichtigung an Fabio,
  Terminbestätigung/-stornierung an Kunden, optional Erinnerungen (per Cron-Job auf Ionos).
- Alternative bei hohem Volumen / besserer Zustellbarkeit: **Brevo** oder **Mailjet**
  (kostenlose Kontingente, dann aber AV-Vertrag mit dem Dienstleister nötig).

### Mobile WebApp (PWA)

Die WebApp (`app.html`) ist mobile-first. Für „Zum Homescreen hinzufügen" + Offline
genügt später eine `manifest.json` + Service Worker — keine App-Store-Veröffentlichung nötig.
Für echte Android/Apple-Apps kann dieselbe Codebasis später z.B. mit Capacitor verpackt werden.

## Domain & Deployment

- Zieldomain: **fabioantunes.de** (Ionos Webhosting).
- Diesen Entwurf live testen: per FTP/SFTP in das Ionos-Webroot laden — läuft sofort
  (reines HTML/CSS/JS, keine Build-Schritte, kein npm).
- Aktuell ist der Entwurf zusätzlich über GitHub Pages erreichbar (siehe Repo-Deployments).
