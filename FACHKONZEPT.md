# Fachkonzept — MatchQuest

**Interaktive Live-Fußball-Challenges für Zuschauer:innen**

| | |
|---|---|
| **Dokument** | Fachkonzept (funktional & technisch) |
| **Produkt** | MatchQuest — Web-App (PWA) |
| **Version** | 1.0 |
| **Stand** | 08.07.2026 |
| **Verantwortlich** | Stefan Wittenberg (HTW Berlin) |
| **Status** | Entwurf / Prototyp umgesetzt (Phase 1) |

---

## 1. Ausgangslage & Vision

Klassische Tipp-Apps verlieren nach dem Anpfiff ihren Reiz: Wer falsch getippt hat, schaut nur noch zu.
**MatchQuest** hält Zuschauer:innen über die **gesamte Spieldauer** aktiv — durch interaktive
**Live-Challenges**, **Video-Duelle mit Freunden**, Punkte, Level und Ranglisten. Das Prinzip funktioniert
für **jedes** Fußballspiel (WM, Champions League, Bundesliga, Amateurfußball) und ist auf andere Sportarten
übertragbar.

**Produktvision:** „Verwandle jedes Spiel — egal welche Liga — in ein gemeinsames, spannendes Erlebnis mit
Freunden, vom Anpfiff bis zum Abpfiff."

**Anlass:** Erstveröffentlichung zur **Fußball-WM 2026**.

---

## 2. Zielgruppe & Rollen

**Zielgruppe:** fußballbegeisterte Zuschauer:innen, die Spiele gemeinsam (vor Ort oder verteilt) verfolgen
und spielerisch interagieren möchten; mobil-affin.

| Rolle | Beschreibung | Rechte/Aufgaben |
|-------|--------------|-----------------|
| **Nutzer** | Zuschauer:in während einer Sportveranstaltung | Registrieren, Lobby beitreten, an Challenges teilnehmen, Punkte sammeln, Ranglisten sehen |
| **Orakel** | Vertrauensvolle, akkreditierte Person **ohne eigenes wirtschaftliches Interesse** | Bestätigt neutral das Eintreten eines Ereignisses bzw. die korrekte Ausführung einer Aktion |
| **Admin/Betreiber** (Phase 2) | Betreibt die App | Inhalte/Challenges kuratieren, Missbrauch moderieren, Ligen verwalten |

> Bei **Gruppen-Videocall-Challenges** wird das Orakel **pro Runde zufällig** aus den Teilnehmenden bestimmt
> (rotierendes Prinzip), sodass niemand dauerhaft Vor- oder Nachteile hat.

---

## 3. Produktüberblick & Scope

**In Scope (Phase 1 – Prototyp, umgesetzt):**
- Schnelle Registrierung & Login
- Spielliste (WM 2026) mit Anstoß-Countdown und Live-Link, Challenge-Lobbys
- Live-Challenges im Takt (Wett-Challenge, Live-Video-Challenge, Gruppen-Videocall-Challenge)
- Orakel-Verifikation (menschliche Bestätigung)
- Gamification: XP, Level, Streak, Coins, Erfolge/Badges
- Social: Freunde, private Ligen, Live-Aktivitäts-Feed, Reaktionen
- Freundes-Leaderboard, Profil & Statistik
- Sicherheits-Guardrails für Challenge-Inhalte
- **Auslieferung als installierbare Web-App (PWA)**, hostbar auf IONOS

**Out of Scope (Phase 1) → Phase 2:**
- Echtes serverseitiges Mehrspieler-Backend (gemeinsame Konten, Echtzeit-Ranking)
- Echter geräteübergreifender Video-Chat (WebRTC)
- Echte KI-Generierung der Challenges (serverseitig)
- Automatische Auflösung von Ereignis-Wetten über Live-Datenfeed
- Push-Benachrichtigungen, Zahlungen/Belohnungs-Shop

---

## 4. User Storys & Akzeptanzkriterien

### US1 — Registrieren, Einloggen, Lobby beitreten
> *Als fußballbegeisterte:r Zuschauer:in möchte ich mich schnell registrieren/einloggen und vor dem Spiel
> einer Challenge-Lobby beitreten.*

**Akzeptanzkriterien**
- Registrierung/Login in wenigen Schritten möglich.
- Login-Bereich mit Zugriff auf Ranglisten.
- Spielliste mit **Startzeitpunkt** je Spiel und **Link zur Live-Übertragung**.
- Nutzer kann vor jedem Spiel einer **Challenge-Lobby** beitreten.

### US2 — Live-Challenges während des Spiels
> *Ich möchte mich in Live-Challenges mit Freunden und anderen Fans messen.*

**Akzeptanzkriterien**
- **Alle 10 Minuten** erscheint automatisch eine Live-Challenge (im Prototyp beschleunigt zum Testen).
- Antwort/Teilnahme nur innerhalb eines **Zeitlimits**.
- Richtige Antworten → Punkte → Aufstieg im **Live-Ranking**.
- **Private Ligen** mit Freunden, Punktestände in Echtzeit vergleichbar.
- Nach Spielende: Statistiken, Ranglisten, Erfolge.
- Nutzbar für **jedes** Fußballspiel.

### US2a — Live-Video-Challenge (interaktiv)
> *Ich möchte Aktions-Challenges live vor der Kamera ausführen, nicht nur ein Video hochladen.*

**Akzeptanzkriterien**
- Live-Kamerabild in der App (Aufnahme-Indikator, Zeitlimit).
- Ein **Orakel** (Freund) verifiziert das Ergebnis **live in Echtzeit** (Bestätigen/Ablehnen).
- Live-**Reaktionen** (Emojis) während der Challenge.

### US2b — Gruppen-Videocall-Challenge
> *Wir sind alle per Videochat online; pro Runde bekommt zufällig eine Person die Challenge, eine andere ist
> das Orakel, der Rest schaut zu.*

**Akzeptanzkriterien**
- Alle Teilnehmenden sind im **integrierten Videocall** sichtbar (Kachel-Raster).
- Pro Runde wird **genau 1 Spieler** und **genau 1 Orakel** **zufällig** bestimmt.
- Nur der Spieler erhält die Challenge; das Orakel bewertet; die übrigen sind Zuschauer und können reagieren.
- Rollen **rotieren** über die Runden.

### US3 — Leaderboard (Freunde)
> *Als Nutzer möchte ich über die Navigation eine Rangliste öffnen.*

**Akzeptanzkriterien**
- Navigationspunkt **„Leaderboard/Rang"**.
- Tabellarische Übersicht mit Spalten **Platzierung · Name · Anzahl richtige Wetten**.
- Enthält **nur Freunde**.
- Beim Öffnen wird die Liste **aktualisiert** und dargestellt.

---

## 5. Funktionale Anforderungen (Features)

| # | Feature | Beschreibung | Phase |
|---|---------|--------------|-------|
| F1 | Registrierung/Login | E-Mail + Passwort, Session | 1 (Demo) / 2 (echt) |
| F2 | Spielliste & Lobby | Fixtures, Countdown, Live-Link, Lobby-Beitritt, Teilnehmer-Avatare | 1 |
| F3 | Wett-Challenge | Ja/Nein bzw. Auswahl auf Spielereignis, Zeitlimit, Punkte | 1 |
| F4 | Live-Video-Challenge | Kamera live, REC-Timer, Orakel bestätigt in Echtzeit, Reaktionen | 1 |
| F5 | Gruppen-Videocall-Challenge | Videocall-Raster, Zufallsauslosung Spieler/Orakel, Rollen-Ablauf | 1 |
| F6 | Orakel-Verifikation | Menschliche Bestätigung (Freund im Raum / im Call) | 1 |
| F7 | Gamification | XP, Level (+Level-Up), Streak 🔥, Coins 🪙, Erfolge/Badges, Konfetti | 1 |
| F8 | Social | Freunde, private Ligen, Live-Aktivitäts-Feed, Emoji-Reaktionen | 1 |
| F9 | Leaderboard | Freunde-Rangliste (Platz/Name/richtige Wetten) + Liga-Ansicht | 1 |
| F10 | Profil & Statistik | Level-Fortschritt, Punkte, Wetten, Challenges, Erfolge | 1 |
| F11 | Guardrails | Inhaltsfilter für Challenges (s. Kap. 11) | 1 |
| F12 | KI-Challenge-Generierung | Stufe 1 kuratiert, Stufe 2 (Prototyp) simuliert, (Phase 2) echt | 1/2 |
| F13 | PWA/Installierbarkeit | „Zum Home-Bildschirm", Offline-Shell | 1 |
| F14 | Echtzeit-Multiplayer | Gemeinsame Lobbys/Ranking serverseitig | 2 |
| F15 | Echter Video-Chat | WebRTC zwischen Geräten + Signalisierung | 2 |
| F16 | Auto-Auflösung Wetten | Live-Sportdatenfeed | 2 |

---

## 6. Nicht-funktionale Anforderungen

- **Usability:** Mobile-first, native-App-Gefühl (Bottom-Navigation, Vollbild-PWA), Bedienung mit einer Hand.
- **Performance:** Erststart < 2 s auf Mobilgerät; keine Build-Abhängigkeiten in Phase 1.
- **Barrierefreiheit:** ausreichende Kontraste, sichtbarer Fokus, `prefers-reduced-motion` respektiert.
- **Kompatibilität:** aktuelle mobile Browser (Safari iOS, Chrome Android); Kamera erfordert **HTTPS**.
- **Datenschutz:** DSGVO-konform (s. Kap. 14); Kamerabild wird **nicht gespeichert** (Phase 1 nur lokal).
- **Sicherheit:** kein API-Key im Frontend; Guardrails serverseitig in Phase 2.
- **Skalierbarkeit:** Datenzugriffe gekapselt (`MQ.DB`), Backend in Phase 2 ohne UI-Umbau anbindbar.
- **Wartbarkeit:** klar getrennte Module (Datenschicht, Challenge-Engine, UI-Controller).

---

## 7. UX/UI-Konzept

- **Design-System:** „Matchday unter Flutlicht" — dunkles Midnight-Blau, Akzent Electric-Lime `#c8ff4d`,
  Gold `#ffd15c` (Belohnungen), LIVE-Magenta `#ff3d71`, Cyan `#35e0ff` (Video). Glassmorphism, animierter
  Hintergrund, Konfetti/Reaktionen als Feedback.
- **Navigation:** Bottom-Tab-Bar mit **Spiele · Live · Rang · Profil**; Status-Leiste oben (Avatar, Level,
  XP-Balken, Streak, Coins).
- **Kern-Screens:** Landing → Login/Registrierung → App (Spiele/Lobby, Live-Challenge, Rang/Ligen, Profil).
- **Feedback:** Toasts, animierte Zähler, Level-Up-Moment, Konfetti bei Erfolg.

---

## 8. Systemarchitektur

### Phase 1 — Statische PWA (umgesetzt)
```
[ Browser / PWA ]
   index.html + CSS + JS   (UI, Challenge-Engine, Gamification)
   localStorage            (Konten, Punkte, Ligen — pro Gerät)
   getUserMedia            (lokale Kamera für Video-Challenges)
   Service Worker          (Offline-Shell, Installierbarkeit)
        │
   Hosting: IONOS Webhosting (statische Dateien via FTP, HTTPS)
```
Keine Serverlogik nötig — ideal für schnellen Start zur WM. „Gruppen-Videocalls" laufen als überzeugende
**Simulation** auf einem Gerät.

### Phase 2 — Backend & Echtzeit (Ausbau)
```
[ PWA Clients ]  ⇄  [ REST/WebSocket-API ]  ⇄  [ DB ]
                         │
   Auth (gehashte Passwörter, Sessions/JWT)
   Lobbys & Echtzeit-Ranking (WebSocket)
   Challenge-Service + KI-Generierung (+ serverseitige Guardrails)
   Ereignis-Auflösung via Sport-Datenfeed
   [ WebRTC ]  Peer-to-Peer-Video  +  Signalisierungs-Server (TURN/STUN)

   Hosting-Optionen: IONOS PHP + MySQL (wie Fabio-Antunes-Projekt)
                     oder Node/Managed-Dienst für WebSocket/WebRTC-Signalisierung
```

---

## 9. Datenmodell (vereinfacht)

- **User**: `id, name, email, passwort(hash), avatar, friends[], points, correctBets, challengesDone, xp, coins, streak, achievements[]`
- **Match**: `id, stage, home, away, kickoff, venue, liveUrl, lobby[]`
- **Challenge**: `id, matchId, type(bet|video|group), text, options[], points, xp, coins, answerSeconds, source(curated|ki)`
- **GroupRound**: `challengeId, participants[], playerId, oracleId, result`
- **League**: `id, name, members[]`
- **Result/Activity**: `userId, challengeId, correct, pointsDelta, timestamp`

---

## 10. Ablauf: Live- und Gruppen-Challenges

**Wett-Challenge:** Challenge erscheint → Zeitlimit läuft → Nutzer wählt Option → Ergebnis wird ermittelt
(Phase 2: Datenfeed) → Punkte/XP/Streak aktualisiert.

**Live-Video-Challenge:** Nutzer startet Kamera → führt Aktion vor (REC-Timer) → **Orakel** bestätigt/lehnt
live ab → Belohnung bzw. Streak-Reset.

**Gruppen-Videocall-Challenge (US2b):**
1. Alle Teilnehmenden der Lobby sind im **Videocall-Raster** sichtbar.
2. Pro Runde werden **zufällig** 1 **Spieler** und 1 **Orakel** ausgelost (verschiedene Personen).
3. Nur der Spieler erhält die Challenge und führt sie live vor; die anderen schauen zu und **reagieren**.
4. Das Orakel bewertet live (Bestätigen/Ablehnen).
5. Belohnung: Spieler (voll) bei Bestätigung; Orakel & Zuschauer erhalten Teilnahme-Boni (Fairness/Aktivität).
6. **Nächste Runde:** neue Zufallsauslosung → Rollen rotieren.

---

## 11. KI-Konzept & Sicherheit (Guardrails)

**Zweistufig:**
- **Stufe 1 (kuratiert):** geprüfter Challenge-Pool — zuverlässig, immer passend.
- **Stufe 2 (KI-Überraschungsmodus):** kombiniert Bausteine zu überraschenden Challenges
  (Prototyp: regelbasierte Simulation; Phase 2: echte KI serverseitig).

**Guardrails (Pflicht für alle Stufen):** Jede Challenge durchläuft einen Inhaltsfilter. **Verworfen** werden
Inhalte mit **Gewalt, sexuellen Bezügen, Gefahr, Substanz-/Alkoholzwang, Diskriminierung oder Illegalem**.
Zusätzlich gilt die Vorgabe: „verrückt, aber **ethisch vertretbar, ungefährlich, kontextspezifisch**".
Als menschliche Sicherheitsebene bestätigt das **Orakel** neutral das Ergebnis.

> In Phase 2 gehört der KI-API-Schlüssel **ausschließlich auf den Server**, nie ins öffentliche Frontend.

---

## 12. Betrieb & Verteilung (finale Entscheidung: Web-App)

**Entscheidung:** MatchQuest wird als **Web-App (PWA)** ausgeliefert — **kein** App-Store, **keine** APK.
Begründung: hohe iPhone-Verbreitung in der Zielgruppe und zu große Hürde/Aufwand für die Store-Einreichung.

**Hosting (wie Fabio-Antunes-Projekt): IONOS Webhosting**
1. Inhalt von `matchquest-app/webapp/` per **FTP/SFTP** in einen **neuen Unterordner** laden, z. B.
   `…/matchquest/` — die bestehende Website (z. B. `www.altenau-harz.de`) bleibt **unverändert**, es wird
   nur zusätzlicher Webspace genutzt. Die App nutzt relative Pfade und läuft daher im Unterordner.
2. **HTTPS/SSL** aktivieren (im Tarif enthalten) — nötig für Kamera-Zugriff.
3. Erreichbar unter z. B. `https://www.altenau-harz.de/matchquest/` — Link/QR-Code an Freunde zum Testen.

**Verteilung an alle — einfach & kostenlos:**
- **Link teilen** (WhatsApp/QR-Code): alle öffnen dieselbe URL auf jedem Gerät.
- **Installieren ohne Store:** iPhone (Safari → „Zum Home-Bildschirm"), Android (Chrome → „App installieren").
  Danach Vollbild-App-Erlebnis mit eigenem Icon.
- Kein Sideloading, keine Store-Gebühr, kein Freigabeprozess.

---

## 13. Recht & Datenschutz

- **DSGVO:** Datensparsamkeit; klare Einwilligung; Datenschutzerklärung & **Impressum** verpflichtend.
- **Kamera/Video:** ausdrückliche Einwilligung; in Phase 1 wird **nichts gespeichert/übertragen**
  (nur lokale Anzeige). In Phase 2 (Video-Chat) Einwilligung aller Teilnehmenden, keine dauerhafte Speicherung.
- **Bild-/Persönlichkeitsrechte:** Beweisvideos zeigen ggf. Dritte → nur mit Zustimmung, nicht öffentlich teilen.
- **Kein Glücksspiel:** Es wird **mit Punkten**, nicht um Geld gespielt (keine Geldeinsätze/-gewinne),
  um regulatorische Einordnung als Glücksspiel zu vermeiden.
- **Minderjährige:** Alterskennzeichnung/Elternhinweis; Guardrails schützen zusätzlich.
- **Marken/Ligarechte:** Team-/Wettbewerbsnamen nur beschreibend; keine offiziellen Logos ohne Lizenz;
  Live-Links verweisen auf berechtigte Anbieter.

---

## 14. Roadmap

| Phase | Inhalt | Status |
|-------|--------|--------|
| **1 — Prototyp / WM-Launch** | PWA, alle Challenge-Typen (simuliert), Gamification, IONOS-Hosting | ✅ umgesetzt |
| **2 — Multiplayer-Backend** | Echte Konten, Echtzeit-Lobbys & -Ranking, WebRTC-Video, echte KI + Guardrails, Auto-Auflösung der Wetten | geplant |
| **3 — Ausbau** | Push-Benachrichtigungen, Belohnungs-Shop, weitere Sportarten, Turniere/Events | Idee |

---

## 15. Risiken & Annahmen

- **Kamera-Rechte/Browser:** iOS/Android-Kamera nur über HTTPS; Fallback auf Simulation vorhanden.
- **Echtzeit-Video (Phase 2):** WebRTC + TURN kann Betriebskosten verursachen → Anbieter/Skalierung prüfen.
- **Ereignis-Auflösung:** verlässlicher Live-Datenfeed nötig (Lizenz/Kosten) — sonst Orakel-basiert.
- **Fairness/Missbrauch:** Orakel-Rotation + Moderation (Phase 2) gegen Manipulation.
- **Annahme:** Nutzer:innen schauen gemeinsam (Raum oder Video-Call) — Grundlage der Orakel-Mechanik.

---

## 16. Offene Punkte

- Zieldomain & IONOS-Tarif final festlegen.
- Phase-2-Backend-Stack entscheiden (IONOS PHP/MySQL vs. Node/Managed für WebSocket/WebRTC).
- Quelle für offiziellen Spielplan/Live-Daten klären (Lizenz).
- Belohnungssystem: rein virtuell (Coins/Badges) — später reale Prämien? (Recht prüfen)

---

## Anhang — Glossar

- **PWA:** Progressive Web App — Web-App, installierbar wie eine native App, offlinefähig.
- **Orakel:** neutrale Instanz, die ein Ergebnis bestätigt.
- **Guardrails:** Regeln/Filter, die unerwünschte Inhalte verhindern.
- **WebRTC:** Browser-Technik für Peer-to-Peer-Video/-Audio.
- **Streak:** Serie aufeinanderfolgender Erfolge.
