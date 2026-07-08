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

## Auf IONOS veröffentlichen (Phase 1)

1. Im IONOS-Kundenmenü **Webhosting → FTP-Zugang** öffnen (Host, Benutzer, Passwort).
2. Mit einem FTP-Programm (z. B. **FileZilla**) verbinden.
3. Den **gesamten Inhalt dieses Ordners** (`index.html`, `manifest.webmanifest`, `service-worker.js`, `icons/`)
   ins gewünschte Verzeichnis laden:
   - eigene Domain, z. B. `matchquest.de` → ins Webroot,
   - oder Unterordner, z. B. `deinedomain.de/matchquest/`.
4. **HTTPS aktivieren** (IONOS SSL/„SSL-Zertifikat" – kostenlos im Tarif enthalten).
   ⚠️ Wichtig: Die **Kamera** (Live-Video-Challenges) funktioniert nur über **https**, nicht über http.
5. Fertig – die App ist unter deiner Domain erreichbar und teilbar (einfach Link verschicken).

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
