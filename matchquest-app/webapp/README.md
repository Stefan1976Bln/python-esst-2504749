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

## Hinweis: Demo vs. Live-Backend

Aktuell laufen Konten, Punkte und Ranglisten **client-seitig im Browser** (`localStorage`), d. h. pro Gerät
getrennt und die „Gruppen-Videocalls" sind noch simuliert. Für echten Mehrspieler-Betrieb (gemeinsame Konten,
Echtzeit-Ranking, echter Video-Chat zwischen Geräten) folgt in **Phase 2** ein Backend
(IONOS bietet PHP + MySQL; für Live-Video WebRTC + ein Signalisierungs-Dienst). Details im
[Fachkonzept](../../FACHKONZEPT.md).
