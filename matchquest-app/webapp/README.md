# MatchQuest — Web-App (PWA) für IONOS

Dies ist die **installierbare Web-App**. Reines HTML/CSS/JS — **kein Build, kein Node, keine App-Store-Freigabe**.
Genau wie bei der Fabio-Antunes-Seite wird der Ordner per **FTP/SFTP ins IONOS-Webroot** geladen und läuft sofort.

## Inhalt

| Datei | Zweck |
|-------|-------|
| `index.html` | Die komplette App (Landing, Login, Spiele, Live-/Video-/Gruppen-Challenges, Rang, Profil) |
| `manifest.webmanifest` | Macht die App installierbar („Zum Home-Bildschirm") |
| `service-worker.js` | Offline-Fähigkeit + Installierbarkeit |
| `icons/` | App-Icons (Android, iOS, maskable, Favicon) |

## Auf IONOS veröffentlichen — als **Unterordner** (bestehende Website bleibt unverändert)

Ziel: die App unter **`www.altenau-harz.de/matchquest/`** betreiben, **ohne** die bestehende Seite anzufassen —
es wird nur zusätzlicher Webspace genutzt. Die App verwendet **relative Pfade**, läuft daher problemlos in
einem Unterordner.

1. Im IONOS-Kundenmenü **Webhosting → FTP-Zugang** öffnen (Host, Benutzer, Passwort).
2. Mit einem FTP-Programm (z. B. **FileZilla**) verbinden.
3. Im Webroot (dort, wo die bestehende `index.html` von altenau-harz.de liegt) einen **neuen Ordner**
   `matchquest` anlegen. **Nichts Bestehendes löschen oder überschreiben.**
4. Den **gesamten Inhalt dieses Ordners** — `index.html`, `manifest.webmanifest`, `service-worker.js`
   und den Ordner `icons/` — in `…/matchquest/` hochladen.
5. **HTTPS/SSL** muss aktiv sein (bei IONOS kostenlos im Tarif). ⚠️ Die **Kamera** (Live-/Video-Challenges)
   funktioniert nur über **https**, nicht über http.
6. Fertig — Aufruf unter **`https://www.altenau-harz.de/matchquest/`**. Link (oder QR-Code) an Freunde
   schicken, Feedback einsammeln.

> Die eigentliche Website (`www.altenau-harz.de`) wird dadurch **nicht** verändert — MatchQuest liegt
> vollständig separat im Unterordner.

## Auf dem Handy „installieren" (ohne App-Store)

- **iPhone (Safari):** Seite öffnen → Teilen-Symbol → **„Zum Home-Bildschirm"**. Danach startet MatchQuest
  wie eine echte App im Vollbild (eigenes Icon, ohne Browser-Leiste).
- **Android (Chrome):** Menü ⋮ → **„App installieren"** bzw. Banner „Installieren" antippen.

## Verteilung an Freunde

- **Link teilen** (WhatsApp/QR-Code) → alle öffnen dieselbe URL, kostenlos, auf jedem Gerät.
- Kein Sideloading, keine APK, keine 25 $-Store-Gebühr nötig.

## Neu in dieser Version

- **Einwilligung (rechtlich):** Beim ersten Start muss jede:r den Nutzungsregeln, dem Datenschutz
  (inkl. Jitsi-Drittanbieter) und der Altersangabe (16+) zustimmen. Impressum/Datenschutz/Verhaltenskodex
  sind im Profil hinterlegt — **Betreiberangaben in `matchquest.html`/`index.html` (Objekt `DOCS`) vor dem
  Live-Gang ausfüllen** (in DE gesetzlich Pflicht).
- **Spenden statt Gewinn:** ❤️-Button (Statusleiste & Profil) öffnet die **offizielle Seite der Berliner Tafel**.
  Wir wickeln **keine Zahlungen** ab und behalten nichts. Exakten Spenden-Deep-Link bei Bedarf in
  `SPENDE_URL` eintragen.
- **Teams:** Rang → **Teams** (Team-Battle). Man kann **während einer Challenge** einem Team beitreten;
  Punkte zählen fürs Team. **Jedes Team hat seinen eigenen Videocall** (Raum-Code enthält die Team-ID).
- **KI-Modus (simuliert):** erzeugt Überraschungs-Challenges **im Browser** (regelbasiert, mit Guardrails) —
  funktioniert ohne Server. **Echte** LLM-KI braucht einen kleinen Server-Proxy (Phase 2, z. B. `ki.php` auf
  IONOS, damit der API-Schlüssel nie ins Frontend gelangt).
- **Videocall-Räume:** werden **dynamisch** erzeugt (kein Reservieren): Der Raum-Name ist der „Schlüssel" —
  wer denselben Code nutzt, landet im selben, kurzlebigen Meeting. `meet.jit.si`-Server ist in
  `JITSI_DOMAIN` austauschbar (eigene Instanz für Produktion).

## Mit Freunden testen

**Registrieren (super einfach, kein E-Mail-Versand):**
- Reiter **Registrieren** → E-Mail + Passwort (2×, im **Klartext** sichtbar), Name optional → **Konto erstellen**.
- Es wird **keine** E-Mail verschickt/bestätigt — man ist sofort drin. Ideal für einen schnellen Freundes-Test.

**Live-Challenge ohne Spiel-Termin:** auf **Spiele → „Freies Spiel — sofort testen"** (oder Live-Tab) — startet
sofort Live-Challenges (Wette + Live-Video), unabhängig von einem WM-Spiel.

**Echter Mehrpersonen-Videocall (alle sehen sich live):**
- **Live-Tab → „👥 Gruppen-Challenge starten" → Reiter „📹 Echter Videocall"**.
- Alle Tester geben **denselben Raum-Code** ein (z. B. den vorausgefüllten) → **Beitreten** → Kamera/Mikro erlauben.
- Basiert auf **Jitsi Meet** (Open Source, Apache-Lizenz) über den kostenlosen Server `meet.jit.si` — **kein eigener
  Server nötig**. Mit **„🎲 Runde für alle auslosen"** werden Spieler & Orakel zufällig bestimmt und synchron
  bei allen angezeigt; das Orakel bewertet live.
- ⚠️ **Nur über HTTPS** (Kamera). Funktioniert **nicht** in der Artifact-Vorschau (dort ist der externe Dienst
  blockiert → automatischer Rückfall auf den 🤖 Simulations-Modus), sondern **auf der IONOS-gehosteten Version**.
- ℹ️ Hinweis zu `meet.jit.si`: Gelegentlich verlangt der öffentliche Server, dass **eine Person** den Raum als
  „Moderator" per Google/GitHub-Login startet (Meldung „Warten auf Moderator"). Für den Freundes-Test einmalig ok.
  Für den Dauerbetrieb später **eigene Jitsi-Instanz** oder anderen Open-Source-Dienst hosten (DSGVO-freundlicher).
  Der Server lässt sich im Code leicht austauschen (`meet.jit.si` → eigene Domain).

## Echt gemeinsam spielen (optionales Backend)

Für **geräteübergreifend geteilte** Konten, Punkte, Ranglisten und Team-Battle gibt es ein schlankes
PHP+MySQL-Backend unter [`../backend/`](../backend/README.md) (läuft auf eurem IONOS-Webspace).
Aktivieren: in `index.html` die Konstante `BACKEND_URL` auf die API-URL setzen
(z. B. `https://www.altenau-harz.de/matchquest-api/api.php`). Leer = Lokal-Modus.
Der **echte Videocall + die Gruppen-Jury** laufen bereits ohne Backend live über den Call.

## Hinweis: Demo vs. Live-Backend

Aktuell laufen Konten, Punkte und Ranglisten **client-seitig im Browser** (`localStorage`), d. h. pro Gerät
getrennt und die „Gruppen-Videocalls" sind noch simuliert. Für echten Mehrspieler-Betrieb (gemeinsame Konten,
Echtzeit-Ranking, echter Video-Chat zwischen Geräten) folgt in **Phase 2** ein Backend
(IONOS bietet PHP + MySQL; für Live-Video WebRTC + ein Signalisierungs-Dienst). Details im
[Fachkonzept](../../FACHKONZEPT.md).
