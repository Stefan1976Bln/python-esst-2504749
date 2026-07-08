/* =========================================================
   MatchQuest — Challenge-Engine
   ---------------------------------------------------------
   Zwei Stufen (per Schalter in der App wählbar):

   • STUFE 1 – Kuratierter Pool:
       Fest vorgegebene, geprüfte Live-Challenges. Zuverlässig
       und immer passend. Ideal für den ersten Test.

   • STUFE 2 – Simulierte "KI"-Generierung:
       Baut aus Bausteinen (Situationen × Aktionen) überraschende
       Challenges zusammen. Simuliert die spätere echte KI, ohne
       API-Kosten und ohne Risiko unpassender Inhalte.

   GUARDRAILS:
       Jede erzeugte Challenge – egal welche Stufe – läuft durch
       passesGuardrails(). Alles mit Gewalt, sexuellen Inhalten,
       Gefahr, Alkohol-/Drogenzwang, Diskriminierung oder
       illegalem Bezug wird verworfen und neu erzeugt. Die
       Bausteine selbst sind bereits harmlos gehalten; der Filter
       ist die zusätzliche Sicherheitsschicht (wie bei echter KI).

   Challenge-Typen:
       'bet'    → Ja/Nein-Wette auf ein Spielereignis (auto/Orakel)
       'action' → Aktion durchführen + Beweis (Foto/Video) hochladen,
                  ein Freund im Raum bestätigt als ORAKEL
   ========================================================= */

(function (global) {
  'use strict';

  /* ---------------- GUARDRAILS ---------------- */
  // Verbotene Themen — als Wortstämme. Bewusst konservativ.
  var BLOCKLIST = [
    // Gewalt / Gefahr
    'gewalt', 'schlag', 'prügel', 'verletz', 'blut', 'waffe', 'messer',
    'feuer', 'brand', 'sprung', 'springen vom', 'dach', 'balkon', 'klettern auf',
    'auto fahren', 'straße rennen', 'gefähr', 'ersticken', 'würg',
    // Sexuelles
    'sex', 'nackt', 'entkleid', 'ausziehen', 'busen', 'intim', 'porno',
    // Substanzen (Zwang)
    'exen', 'shot trinken', 'komasaufen', 'droge', 'kiffen', 'zigarette rauch',
    // Diskriminierung / Illegales
    'beleidig', 'rassis', 'sexis', 'stehlen', 'klauen', 'einbruch', 'mobbing'
  ];

  function passesGuardrails(text) {
    if (!text) return false;
    var t = text.toLowerCase();
    for (var i = 0; i < BLOCKLIST.length; i++) {
      if (t.indexOf(BLOCKLIST[i]) !== -1) return false;
    }
    return true;
  }

  /* ---------------- Kleine Zufallshelfer ----------------
     Wichtig: keine echte Zeit-/Zufallsabhängigkeit im Datenmodell,
     nur zur UI-Auswahl der nächsten Challenge. */
  function pick(arr, seed) {
    var idx = Math.floor((seed % arr.length + arr.length) % arr.length);
    return arr[idx];
  }
  function rnd() { return Math.random(); }

  /* ---------------- STUFE 1: Kuratierter Pool ---------------- */
  var CURATED = [
    {
      type: 'bet',
      text: 'Fällt in den nächsten 10 Minuten ein Tor?',
      options: ['Ja', 'Nein'], points: 20
    },
    {
      type: 'bet',
      text: 'Gibt es in den nächsten 10 Minuten eine Gelbe Karte?',
      options: ['Ja', 'Nein'], points: 20
    },
    {
      type: 'bet',
      text: 'Wird der nächste Eckball von der linken oder rechten Seite ausgeführt?',
      options: ['Links', 'Rechts'], points: 15
    },
    {
      type: 'action',
      text: 'Mache deinen besten Torjubel und lass ihn von einem Freund (Orakel) filmen oder bestätigen.',
      points: 30
    },
    {
      type: 'action',
      text: 'Male dein Tipp-Ergebnis auf einen Zettel, halte ihn in die Kamera und lass es vom Orakel bestätigen.',
      points: 25
    },
    {
      type: 'action',
      text: 'Stimme mit allen im Raum die Vereinshymne oder einen Fangesang an — Beweisvideo hochladen.',
      points: 30
    }
  ];

  /* ---------------- STUFE 2: Simulierte "KI" ----------------
     Bausteine sind schon von sich aus harmlos & lustig. */
  var SITUATIONS = [
    'Beim nächsten Freistoß',
    'Wenn die Kamera auf die Trainerbank schwenkt',
    'Sobald der Kommentator laut wird',
    'Beim nächsten Einwurf',
    'Wenn dein Team in Ballbesitz kommt',
    'In der nächsten Werbepause'
  ];
  var ACTIONS = [
    'erfinde einen Jubel und führe ihn vor',
    'halte ein selbstgemaltes Fan-Schild hoch',
    'imitiere den Kommentator für 10 Sekunden',
    'mache mit allen im Raum eine La-Ola-Welle',
    'stimme einen kurzen Fangesang an',
    'balanciere einen Snack auf dem Kopf, ohne dass er runterfällt',
    'zeichne in 20 Sekunden das Wappen deines Teams'
  ];
  var BET_EVENTS = [
    { q: 'Fällt in den nächsten 10 Minuten ein Tor?', o: ['Ja', 'Nein'] },
    { q: 'Kommt als Nächstes ein Foul oder ein Eckball?', o: ['Foul', 'Eckball'] },
    { q: 'Wird der nächste Torschuss aufs Tor gehen oder daneben?', o: ['Aufs Tor', 'Daneben'] },
    { q: 'Wechselt der Trainer in den nächsten 10 Minuten einen Spieler?', o: ['Ja', 'Nein'] }
  ];

  function generateSimulated(match) {
    // Bis zu 8 Versuche, eine guardrail-konforme Challenge zu bauen.
    for (var attempt = 0; attempt < 8; attempt++) {
      var asBet = rnd() < 0.5;
      var challenge;
      if (asBet) {
        var ev = pick(BET_EVENTS, Math.floor(rnd() * 1000));
        challenge = { type: 'bet', text: ev.q, options: ev.o.slice(), points: 20, source: 'ki' };
      } else {
        var sit = pick(SITUATIONS, Math.floor(rnd() * 1000));
        var act = pick(ACTIONS, Math.floor(rnd() * 1000));
        var text = sit + ': ' + act + '. Ein Freund im Raum bestätigt als Orakel — Beweisfoto/-video hochladen.';
        challenge = { type: 'action', text: text, points: 30, source: 'ki' };
      }
      if (passesGuardrails(challenge.text)) return challenge;
    }
    // Fallback: garantiert harmlose Challenge
    return { type: 'action', text: 'Zeig ein Daumen-hoch in die Kamera und lass es vom Orakel bestätigen.', points: 15, source: 'ki' };
  }

  /* ---------------- Öffentliche Engine-API ---------------- */
  var idCounter = 0;
  function nextChallenge(opts) {
    opts = opts || {};
    var mode = opts.mode || 'curated'; // 'curated' | 'ki'
    var raw;
    if (mode === 'ki') {
      raw = generateSimulated(opts.match);
    } else {
      raw = pick(CURATED, Math.floor(rnd() * 1000));
      raw = JSON.parse(JSON.stringify(raw)); // Kopie
      raw.source = 'curated';
    }
    // Sicherheitsnetz: auch kuratierte laufen durch den Filter
    if (!passesGuardrails(raw.text)) {
      raw = { type: 'action', text: 'Zeig ein Daumen-hoch in die Kamera und lass es vom Orakel bestätigen.', points: 15, source: raw.source };
    }
    raw.id = 'c' + (++idCounter);
    raw.answerSeconds = raw.type === 'bet' ? 30 : 90; // Antwortzeit / Zeitlimit
    raw.createdLabel = 'Live-Challenge';
    return raw;
  }

  global.MQChallenges = {
    nextChallenge: nextChallenge,
    passesGuardrails: passesGuardrails,   // exportiert für Tests/Transparenz
    BLOCKLIST: BLOCKLIST
  };

})(window);
