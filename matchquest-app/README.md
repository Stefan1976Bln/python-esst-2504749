# MatchQuest — Interaktive Fußball-Challenges (Prototyp zur WM 2026)

> **Aktuelle Version:** die Premium-Web-App liegt in **`webapp/`** (installierbare PWA, für IONOS-Hosting) —
> Einzeldatei-Quelle: **`matchquest-pro.html`**. Konzept: **[../FACHKONZEPT.md](../FACHKONZEPT.md)** (lesbar auch als `fachkonzept.html`).
> Die frühere schlichte Version (`index.html`, `login.html`, `app.html`, `matchquest.html`) bleibt als Referenz erhalten.


MatchQuest verwandelt jedes Fußballspiel in ein interaktives Erlebnis: während des
Spiels erscheinen **Live-Challenges** (Wetten aufs nächste Ereignis oder Mitmach-Aktionen),
für die es **Punkte** gibt. Freunde vergleichen sich im **Leaderboard**.

Dies ist ein **statischer, voll durchklickbarer Entwurf** (HTML/CSS/JS). Registrierung,
Login, Punkte und die Spielliste laufen client-seitig über `localStorage` — **kein Server
nötig**. Ideal, um das Konzept zur WM sofort zu zeigen.

## Rollen

| Rolle | Beschreibung |
|-------|--------------|
| **Nutzer** | Fußballbegeisterte:r Zuschauer:in während einer Sportveranstaltung. |
| **Orakel** | Vertrauensvolle, akkreditierte Person **ohne eigenes wirtschaftliches Interesse**, die das Eintreten eines Ereignisses / die Erfüllung einer Aktion bestätigt (im Prototyp: ein Freund im Raum bestätigt per Button). |

## Inhalt

| Datei | Zweck |
|-------|-------|
| `index.html` | Marketing-/Landingpage (Konzept, Challenge-Arten, Sportarten) |
| `login.html` | Schnelle Registrierung **und** Login (Dummy, `localStorage`) |
| `app.html` | Die App: **Spiele/Lobby**, **Live-Challenge**, **Leaderboard** |
| `assets/auth.js` | Auth + Datenmodell + feste WM-Spielliste (`MQ.DB` / `MQ.Auth`) |
| `assets/challenges.js` | Challenge-Engine: kuratierter Pool (Stufe 1) + simulierte KI (Stufe 2) + **Guardrails** |
| `assets/app.js` | App-Logik (Views, Timer, Punkte) |
| `assets/styles.css` | Gemeinsames Stylesheet (mobile-first, Rasengrün/Gold) |
| `assets/landing.js` | Landingpage-Interaktivität |

## Umgesetzte User Storys

- **US1 — Registrieren, Einloggen, Lobby beitreten:** schnelle Anmeldung, Login-Bereich mit
  Rangliste, Spielliste mit Anstoß-Countdown und Live-Link, Beitritt zur Challenge-Lobby vor
  dem Anpfiff.
- **US2 — Live-Challenges:** im Takt (echte App: alle 10 Min.; im Demo beschleunigt auf 20 s)
  erscheint eine Challenge mit **Zeitlimit**. Zwei Typen:
  - **Wett-Challenge** — Ja/Nein bzw. Auswahl auf das nächste Ereignis, richtige Tipps geben Punkte.
  - **Mitmach-Challenge** — Aktion durchführen, **Beweisfoto/-video hochladen**, **Orakel** (Freund
    im Raum) bestätigt.
- **Leaderboard (Freunde):** über die Navigation → **„Leaderboard"**. Tabelle mit den Spalten
  **Platzierung · Name · Anzahl richtige Wetten**, nur Freunde, wird bei jedem Öffnen aktualisiert.
- **Statistik** nach Punkten, richtigen Wetten und gemeisterten Challenges.

## Challenge-Stufen & Guardrails

- **Stufe 1 (Standard):** kuratierter, geprüfter Challenge-Pool — zuverlässig und immer passend.
- **Stufe 2 (KI-Überraschungsmodus, in der App per Schalter):** simuliert eine KI, die aus
  Bausteinen überraschende Challenges kombiniert.
- **Guardrails:** jede Challenge — egal welche Stufe — läuft durch `passesGuardrails()`
  (`assets/challenges.js`). Inhalte mit **Gewalt, Sexuellem, Gefahr, Substanzzwang,
  Diskriminierung oder Illegalem** werden verworfen und neu erzeugt.

## Ausprobieren

Einfach `index.html` im Browser öffnen (Doppelklick genügt, kein Build).

**Demo-Zugang:** `stefan@matchquest.app` · Passwort `wm2026`
(auch `lena@…`, `jonas@…` — Passwort für alle: `wm2026`). Eigenes Konto jederzeit registrierbar.

Demo-Daten zurücksetzen: Fußzeile → „Demo zurücksetzen" oder in der Browser-Konsole `MQ.resetDemo()`.

## Veröffentlichung zur WM (GitHub Pages)

Der Ordner ist reines HTML/CSS/JS und kann auf jedem statischen Host laufen. Für GitHub Pages
den Deploy-Workflow auf diesen Ordner zeigen lassen (`path: matchquest-app`) bzw. Pages-Quelle
entsprechend setzen.

## Ausblick: echtes Backend (Phase 2)

Die Datenzugriffe sind in `MQ.DB` gekapselt und lassen sich später auf echte API-Aufrufe
umstellen: echte Accounts/Login, serverseitiges Echtzeit-Ranking, private Ligen, echte
Ereignis-Auflösung der Wetten (Live-Datenfeed) und **echte KI-Challenge-Generierung** mit
serverseitigen Guardrails (API-Key gehört nie ins öffentliche Frontend).
