/* =========================================================
   MatchQuest — Auth, Datenmodell & WM-Spieldaten
   ---------------------------------------------------------
   DEMO-MODUS: Registrierung, Login, Freunde, Punkte und
   die Spielliste liegen im localStorage. So lässt sich die
   App OHNE Server komplett durchklicken und zur WM sofort
   über einen statischen Host (z.B. GitHub Pages) zeigen.

   Für eine Live-Version werden die Zugriffe in MQ.DB später
   durch echte Backend-Aufrufe (fetch) ersetzt — die App-Logik
   bleibt gleich.

   Dummy-Zugänge (Passwort für alle: "wm2026"):
     • stefan@matchquest.app   (Stefan)
     • lena@matchquest.app     (Lena)
     • jonas@matchquest.app    (Jonas)
   Neue Konten lassen sich jederzeit selbst registrieren.
   ========================================================= */

(function (global) {
  'use strict';

  var LS_KEY = 'mq_db_v1';
  var SESSION_KEY = 'mq_session';

  /* ---------- Feste WM-2026-Demo-Spielliste ----------
     Zeiten relativ zu "jetzt", damit im Demo immer ein Spiel
     kurz vor Anpfiff bzw. "LIVE" ist. (kicker.de bietet keine
     offene API — für den Prototyp ist eine feste Liste robuster.) */
  function minutesFromNow(min) {
    var d = new Date(Date.now() + min * 60000);
    return d.toISOString();
  }

  function seedMatches() {
    return [
      {
        id: 'm1', stage: 'Gruppe A · 1. Spieltag',
        home: 'Deutschland', homeFlag: '🇩🇪',
        away: 'Brasilien', awayFlag: '🇧🇷',
        kickoff: minutesFromNow(-8),      // läuft bereits → LIVE
        venue: 'MetLife Stadium, New York',
        liveUrl: 'https://www.kicker.de/fussball-international/wettbewerbe'
      },
      {
        id: 'm2', stage: 'Gruppe C · 1. Spieltag',
        home: 'Argentinien', homeFlag: '🇦🇷',
        away: 'Frankreich', awayFlag: '🇫🇷',
        kickoff: minutesFromNow(20),      // startet bald
        venue: 'Estadio Azteca, Mexiko-Stadt',
        liveUrl: 'https://www.kicker.de/fussball-international/wettbewerbe'
      },
      {
        id: 'm3', stage: 'Gruppe E · 1. Spieltag',
        home: 'Spanien', homeFlag: '🇪🇸',
        away: 'England', awayFlag: '🏴',
        kickoff: minutesFromNow(75),
        venue: 'SoFi Stadium, Los Angeles',
        liveUrl: 'https://www.kicker.de/fussball-international/wettbewerbe'
      },
      {
        id: 'm4', stage: 'Gruppe G · 1. Spieltag',
        home: 'Portugal', homeFlag: '🇵🇹',
        away: 'Niederlande', awayFlag: '🇳🇱',
        kickoff: minutesFromNow(150),
        venue: 'BC Place, Vancouver',
        liveUrl: 'https://www.kicker.de/fussball-international/wettbewerbe'
      }
    ];
  }

  /* ---------- Seed-Datenbank (Erstbefüllung) ---------- */
  function seed() {
    return {
      users: [
        {
          id: 'stefan', name: 'Stefan', email: 'stefan@matchquest.app',
          password: 'wm2026',
          friends: ['lena', 'jonas', 'mara'],
          points: 120, correctBets: 6, challengesDone: 4
        },
        {
          id: 'lena', name: 'Lena', email: 'lena@matchquest.app',
          password: 'wm2026',
          friends: ['stefan', 'jonas'],
          points: 210, correctBets: 11, challengesDone: 7
        },
        {
          id: 'jonas', name: 'Jonas', email: 'jonas@matchquest.app',
          password: 'wm2026',
          friends: ['stefan', 'lena'],
          points: 90, correctBets: 4, challengesDone: 3
        },
        {
          id: 'mara', name: 'Mara', email: 'mara@matchquest.app',
          password: 'wm2026',
          friends: ['stefan'],
          points: 165, correctBets: 8, challengesDone: 6
        }
      ],
      matches: seedMatches(),
      version: 1
    };
  }

  /* ---------- Low-Level Storage ---------- */
  function load() {
    try {
      var raw = global.localStorage.getItem(LS_KEY);
      if (!raw) {
        var fresh = seed();
        save(fresh);
        return fresh;
      }
      return JSON.parse(raw);
    } catch (e) {
      var s = seed();
      save(s);
      return s;
    }
  }

  function save(db) {
    global.localStorage.setItem(LS_KEY, JSON.stringify(db));
  }

  /* ---------- Öffentliche Daten-API (später gegen Backend tauschbar) ---------- */
  var DB = {
    getUsers: function () { return load().users; },

    getUser: function (id) {
      return load().users.filter(function (u) { return u.id === id; })[0] || null;
    },

    findByEmail: function (email) {
      email = (email || '').trim().toLowerCase();
      return load().users.filter(function (u) {
        return u.email.toLowerCase() === email;
      })[0] || null;
    },

    getMatches: function () {
      // Spielliste bei jedem Laden zeitlich frisch halten
      var db = load();
      db.matches = seedMatches();
      save(db);
      return db.matches;
    },

    getMatch: function (id) {
      return DB.getMatches().filter(function (m) { return m.id === id; })[0] || null;
    },

    /* Punkte / Statistik eines Nutzers aktualisieren */
    addResult: function (userId, opts) {
      opts = opts || {};
      var db = load();
      var u = db.users.filter(function (x) { return x.id === userId; })[0];
      if (!u) return null;
      u.points = (u.points || 0) + (opts.points || 0);
      if (opts.correctBet) u.correctBets = (u.correctBets || 0) + 1;
      if (opts.challengeDone) u.challengesDone = (u.challengesDone || 0) + 1;
      save(db);
      return u;
    },

    /* Freundes-Leaderboard: Nutzer selbst + seine Freunde,
       sortiert nach richtigen Wetten (dann Punkte). */
    friendsLeaderboard: function (userId) {
      var db = load();
      var me = db.users.filter(function (u) { return u.id === userId; })[0];
      if (!me) return [];
      var ids = {};
      ids[userId] = true;
      (me.friends || []).forEach(function (f) { ids[f] = true; });
      var rows = db.users.filter(function (u) { return ids[u.id]; });
      rows.sort(function (a, b) {
        if (b.correctBets !== a.correctBets) return b.correctBets - a.correctBets;
        return (b.points || 0) - (a.points || 0);
      });
      return rows.map(function (u, i) {
        return {
          rank: i + 1,
          id: u.id,
          name: u.name,
          correctBets: u.correctBets || 0,
          points: u.points || 0,
          me: u.id === userId
        };
      });
    }
  };

  /* ---------- Registrierung & Login ---------- */
  var Auth = {
    register: function (name, email, password) {
      name = (name || '').trim();
      email = (email || '').trim().toLowerCase();
      if (!name || !email || !password) {
        return { ok: false, error: 'Bitte Name, E-Mail und Passwort ausfüllen.' };
      }
      if (DB.findByEmail(email)) {
        return { ok: false, error: 'Diese E-Mail ist bereits registriert.' };
      }
      var db = load();
      var id = 'u_' + email.replace(/[^a-z0-9]/g, '').slice(0, 12) + '_' + db.users.length;
      var user = {
        id: id, name: name, email: email, password: password,
        // Neue Nutzer sind automatisch mit den Demo-Freunden verbunden,
        // damit das Leaderboard sofort etwas anzeigt.
        friends: ['stefan', 'lena', 'jonas', 'mara'],
        points: 0, correctBets: 0, challengesDone: 0
      };
      db.users.push(user);
      // Rückseite der Freundschaft eintragen
      db.users.forEach(function (u) {
        if (user.friends.indexOf(u.id) !== -1 && u.friends.indexOf(id) === -1) {
          u.friends.push(id);
        }
      });
      save(db);
      Auth.setSession(id);
      return { ok: true, user: user };
    },

    login: function (email, password) {
      var u = DB.findByEmail(email);
      if (!u || u.password !== password) {
        return { ok: false, error: 'E-Mail oder Passwort ist falsch.' };
      }
      Auth.setSession(u.id);
      return { ok: true, user: u };
    },

    setSession: function (id) {
      global.localStorage.setItem(SESSION_KEY, id);
    },

    currentUser: function () {
      var id = global.localStorage.getItem(SESSION_KEY);
      return id ? DB.getUser(id) : null;
    },

    logout: function () {
      global.localStorage.removeItem(SESSION_KEY);
    },

    /* Session erforderlich — sonst zurück zum Login */
    requireLogin: function () {
      var u = Auth.currentUser();
      if (!u) { global.location.href = 'login.html'; }
      return u;
    }
  };

  /* Demo-Daten zurücksetzen (Browser-Konsole: MQ.resetDemo()) */
  function resetDemo() {
    global.localStorage.removeItem(LS_KEY);
    global.localStorage.removeItem(SESSION_KEY);
    load();
    return 'MatchQuest Demo-Daten zurückgesetzt.';
  }

  global.MQ = {
    DB: DB,
    Auth: Auth,
    resetDemo: resetDemo
  };

})(window);
