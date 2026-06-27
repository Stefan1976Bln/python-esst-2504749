/* =========================================================
   Fabio Antunes Prime Coaching — Auth & gemeinsame Daten
   ---------------------------------------------------------
   DEMO-MODUS: Login, Mitglieder, Termine und Nachrichten
   liegen im localStorage. So kann Fabio alles durchklicken,
   OHNE Server. Für die Live-Version auf Ionos wird dieser
   Teil durch echte PHP/MySQL-Endpunkte ersetzt (siehe README).

   Test-Zugänge:
     • Fabio (Admin):   Login "Fabio"             / Passwort "Fabio123!"
     • Testkunde:       stefan-wittenberg@gmx.de  / Passwort "Fabio123!"
   ========================================================= */

(function (global) {
  'use strict';

  var LS_KEY = 'fa_db_v1';      // gesamte Demo-Datenbank
  var SESSION_KEY = 'fa_session';

  /* ---------- Seed-Datenbank (Erstbefüllung) ---------- */
  function seed() {
    return {
      users: [
        {
          id: 'fabio',
          role: 'admin',
          login: 'Fabio',
          email: 'info@fabioantunes.de',
          password: 'Fabio123!',
          name: 'Fabio Antunes',
          plan: '—'
        },
        {
          id: 'stefan',
          role: 'member',
          login: 'stefan-wittenberg@gmx.de',
          email: 'stefan-wittenberg@gmx.de',
          password: 'Fabio123!',
          name: 'Stefan Wittenberg',
          plan: 'PRIME EVOLUTION',
          since: '2026-01-15',
          // Trainingsplan (Push Day A) – passt zum bestehenden App-Prototyp
          trainingPlan: {
            title: 'Push Day A · Brust/Schulter/Trizeps',
            exercises: [
              { name: 'Bankdrücken', scheme: '4 × 8-10 · 80 kg' },
              { name: 'Schrägbankdrücken', scheme: '3 × 10-12 · 26 kg' },
              { name: 'Butterfly', scheme: '3 × 12-15 · 30 kg' },
              { name: 'Trizepsdrücken', scheme: '3 × 12 · 35 kg' },
              { name: 'Dips', scheme: '3 × 8-12 · KG' }
            ]
          },
          progress: { workouts: 14, streak: 5, volume: '12.480', minutes: 58 }
        }
      ],
      // Termine: { id, userId, date 'YYYY-MM-DD', time 'HH:MM', type, status, location }
      appointments: [
        { id: 'a1', userId: 'stefan', date: nextDateStr(2), time: '18:00', type: 'Personal Training', status: 'confirmed', location: 'Studio Königs Wusterhausen' },
        { id: 'a2', userId: 'stefan', date: nextDateStr(5), time: '17:30', type: 'Personal Training', status: 'confirmed', location: 'Outdoor · Wildau' }
      ],
      // Nachrichten zwischen Kunde und Fabio: { id, userId, from('member'|'admin'), text, ts }
      messages: [
        { id: 'm1', userId: 'stefan', from: 'admin', text: 'Servus Stefan! Stark gestern – heute volle Power 💪', ts: Date.now() - 86400000 },
        { id: 'm2', userId: 'stefan', from: 'member', text: 'Danke Fabio! Bin bereit für Push Day A.', ts: Date.now() - 80000000 }
      ],
      // Neukunden-Anfragen (kostenloses Erstgespräch / Probetraining)
      leads: [],
      // Postausgang (simulierte E-Mails – Demo für spätere echte Mails)
      outbox: []
    };
  }

  /* ---------- Datums-Helfer ---------- */
  function pad(n) { return String(n).padStart(2, '0'); }
  function toDateStr(d) { return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); }
  function nextDateStr(plusDays) {
    var d = new Date(); d.setDate(d.getDate() + plusDays); return toDateStr(d);
  }

  /* ---------- DB laden/speichern ---------- */
  function load() {
    try {
      var raw = localStorage.getItem(LS_KEY);
      if (!raw) { var s = seed(); localStorage.setItem(LS_KEY, JSON.stringify(s)); return s; }
      return JSON.parse(raw);
    } catch (e) { return seed(); }
  }
  function save(db) {
    try { localStorage.setItem(LS_KEY, JSON.stringify(db)); } catch (e) {}
  }

  /* ---------- Session ---------- */
  function getSession() {
    try { return JSON.parse(sessionStorage.getItem(SESSION_KEY) || localStorage.getItem(SESSION_KEY) || 'null'); }
    catch (e) { return null; }
  }
  function setSession(userId, remember) {
    var val = JSON.stringify({ userId: userId, ts: Date.now() });
    sessionStorage.setItem(SESSION_KEY, val);
    if (remember) localStorage.setItem(SESSION_KEY, val); else localStorage.removeItem(SESSION_KEY);
  }
  function logout() {
    sessionStorage.removeItem(SESSION_KEY);
    localStorage.removeItem(SESSION_KEY);
  }

  /* ---------- Auth ---------- */
  function login(loginInput, password, remember) {
    var db = load();
    var id = (loginInput || '').trim().toLowerCase();
    var user = db.users.find(function (u) {
      return (u.login.toLowerCase() === id || u.email.toLowerCase() === id) && u.password === password;
    });
    if (!user) return { ok: false, error: 'Login oder Passwort ist nicht korrekt.' };
    setSession(user.id, remember);
    return { ok: true, user: user };
  }

  function currentUser() {
    var s = getSession();
    if (!s) return null;
    var db = load();
    return db.users.find(function (u) { return u.id === s.userId; }) || null;
  }

  // Schützt eine Seite: leitet bei fehlender/falscher Rolle auf Login um
  function requireRole(role) {
    var u = currentUser();
    if (!u || (role && u.role !== role)) {
      location.href = 'login.html';
      return null;
    }
    return u;
  }

  function changePassword(userId, newPw) {
    var db = load();
    var u = db.users.find(function (x) { return x.id === userId; });
    if (u) { u.password = newPw; save(db); return true; }
    return false;
  }

  /* ---------- Daten-Zugriffe (für app.js / admin.js) ---------- */
  var DB = {
    all: load,
    save: save,
    refresh: function () { return load(); },

    appointmentsFor: function (userId) {
      return load().appointments.filter(function (a) { return a.userId === userId; })
        .sort(function (a, b) { return (a.date + a.time).localeCompare(b.date + b.time); });
    },
    allAppointments: function () {
      return load().appointments.sort(function (a, b) { return (a.date + a.time).localeCompare(b.date + b.time); });
    },
    addAppointment: function (appt) {
      var db = load();
      appt.id = 'a' + Date.now();
      db.appointments.push(appt);
      save(db);
      return appt;
    },
    cancelAppointment: function (id) {
      var db = load();
      var a = db.appointments.find(function (x) { return x.id === id; });
      if (a) { a.status = 'cancelled'; save(db); }
    },

    messagesFor: function (userId) {
      return load().messages.filter(function (m) { return m.userId === userId; })
        .sort(function (a, b) { return a.ts - b.ts; });
    },
    addMessage: function (userId, from, text) {
      var db = load();
      db.messages.push({ id: 'm' + Date.now(), userId: userId, from: from, text: text, ts: Date.now() });
      save(db);
    },
    membersWithMessages: function () {
      var db = load();
      var ids = {};
      db.messages.forEach(function (m) { ids[m.userId] = true; });
      return db.users.filter(function (u) { return u.role === 'member'; });
    },

    members: function () { return load().users.filter(function (u) { return u.role === 'member'; }); },

    addLead: function (lead) {
      var db = load();
      lead.id = 'l' + Date.now();
      lead.ts = Date.now();
      lead.status = 'neu';
      db.leads.push(lead);
      save(db);
      return lead;
    },
    leads: function () { return load().leads.sort(function (a, b) { return b.ts - a.ts; }); },

    // Simulierter Mail-Versand – legt eine Mail in den Postausgang.
    // LIVE: hier würde ein fetch() an ein PHP-Skript (PHPMailer/SMTP) gehen.
    sendMail: function (to, subject, body) {
      var db = load();
      var mail = { id: 'mail' + Date.now(), to: to, subject: subject, body: body, ts: Date.now() };
      db.outbox.push(mail);
      save(db);
      return mail;
    },
    outbox: function () { return load().outbox.sort(function (a, b) { return b.ts - a.ts; }); }
  };

  /* ---------- Demo zurücksetzen ---------- */
  function resetDemo() {
    localStorage.removeItem(LS_KEY);
    load();
  }

  /* ---------- Export ---------- */
  global.FA = {
    login: login,
    logout: logout,
    currentUser: currentUser,
    requireRole: requireRole,
    changePassword: changePassword,
    resetDemo: resetDemo,
    DB: DB,
    util: { toDateStr: toDateStr, pad: pad }
  };

})(window);
