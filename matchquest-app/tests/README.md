# MatchQuest — Persona-Testsuite (End-to-End)

Persona-getriebene Browser-Tests (Playwright) für die Web-App. Prüft Registrierung/Einwilligung,
Wetten mit Mehrheitsentscheid, Teams & Team-Battle, Gruppen-Jury (0–10) mit Rotation,
Videocall-Fallback, KI-Guardrails (jugendfrei), Spende und Persistenz.

Personas: Neuling Nina · Bettor Ben · Party-Host Petra · Skeptiker Sami · KI-Fan Kim · Rückkehrer Rudi.

## Ausführen
```
node tests/personas.mjs
```
Voraussetzung: Playwright + Chromium. Der echte Jitsi-Videocall wird bewusst nur über den
Fallback-Pfad geprüft (externer Dienst); das echte Mehrgeräte-Video auf der gehosteten HTTPS-Seite testen.

Letzter Lauf: **41 PASS / 0 FAIL**.
