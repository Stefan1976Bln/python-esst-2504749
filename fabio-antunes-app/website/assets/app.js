/* =========================================================
   Fabio Antunes Prime Coaching — Kunden-WebApp
   Tabs · Termine + Buchungskalender · Plan · Erfolge · Chat · Profil
   Nutzt FA (auth.js) als Demo-Datenbank.
   ========================================================= */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  // Zugriffsschutz: nur eingeloggte Mitglieder
  var user = FA.requireRole('member');
  if (!user) return;

  var MONTHS = ['Januar','Februar','März','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember'];
  var MONTHS_SHORT = ['JAN','FEB','MÄR','APR','MAI','JUN','JUL','AUG','SEP','OKT','NOV','DEZ'];
  var DOW = ['Mo','Di','Mi','Do','Fr','Sa','So'];
  var SLOT_TIMES = ['08:00','09:30','11:00','16:00','17:30','19:00'];

  /* ---------- Kopfzeile ---------- */
  var first = user.name.split(' ')[0];
  $('#whoName').textContent = user.name;
  $('#whoPlan').textContent = user.plan;
  $('#welcomeName').textContent = 'Servus, ' + first + '!';

  /* ---------- Tab-Steuerung ---------- */
  function showTab(name) {
    $$('#tabs button').forEach(function (b) { b.classList.toggle('active', b.getAttribute('data-tab') === name); });
    $$('.tab-panel').forEach(function (p) { p.classList.toggle('active', p.getAttribute('data-panel') === name); });
    $$('#appNav a').forEach(function (a) { a.classList.toggle('active', a.getAttribute('data-goto') === name); });
    window.scrollTo(0, 0);
  }
  $$('#tabs button').forEach(function (b) { b.addEventListener('click', function () { showTab(b.getAttribute('data-tab')); }); });
  $$('[data-goto]').forEach(function (el) { el.addEventListener('click', function () { showTab(el.getAttribute('data-goto')); }); });

  /* ---------- Übersicht: nächster Termin + Stats ---------- */
  function fmtDateLong(ds) {
    var p = ds.split('-'); var d = new Date(+p[0], +p[1] - 1, +p[2]);
    return DOW[(d.getDay() + 6) % 7] + ', ' + d.getDate() + '. ' + MONTHS[d.getMonth()];
  }
  function renderNextAppt() {
    var appts = FA.DB.appointmentsFor(user.id).filter(function (a) { return a.status !== 'cancelled' && (a.date >= FA.util.toDateStr(new Date())); });
    var box = $('#nextAppt');
    if (!appts.length) { box.innerHTML = '<div class="empty">Kein Termin gebucht. Buche jetzt deinen nächsten Slot!</div>'; return; }
    var a = appts[0]; var p = a.date.split('-');
    box.innerHTML =
      '<div class="appt"><div class="appt-date"><div class="d">' + (+p[2]) + '</div><div class="m">' + MONTHS_SHORT[+p[1]-1] + '</div></div>'
      + '<div class="appt-body"><div class="t">' + a.type + '</div><div class="s">' + a.time + ' Uhr · ' + (a.location||'') + '</div></div>'
      + '<span class="pill pill-green">bestätigt</span></div>';
  }
  function renderStats() {
    var pr = user.progress || { workouts: 0, streak: 0, volume: '0', minutes: 0 };
    $('#statGrid').innerHTML =
      stat(pr.workouts, '', 'Workouts') + stat(pr.streak, '🔥', 'Streak (Tage)')
      + stat(pr.volume, 'kg', 'Volumen') + stat(pr.minutes, 'min', 'Ø Dauer');
  }
  function stat(v, unit, label) {
    return '<div class="stat"><div class="v">' + v + (unit ? '<span class="unit"> ' + unit + '</span>' : '') + '</div><div class="l">' + label + '</div></div>';
  }

  /* ---------- Termine: Liste ---------- */
  function renderMyAppts() {
    var appts = FA.DB.appointmentsFor(user.id);
    var box = $('#myAppts');
    if (!appts.length) { box.innerHTML = '<div class="empty">Noch keine Termine.</div>'; return; }
    box.innerHTML = appts.map(function (a) {
      var p = a.date.split('-');
      var cancelled = a.status === 'cancelled';
      return '<div class="appt"><div class="appt-date"><div class="d">' + (+p[2]) + '</div><div class="m">' + MONTHS_SHORT[+p[1]-1] + '</div></div>'
        + '<div class="appt-body"><div class="t" style="' + (cancelled?'text-decoration:line-through;opacity:.5;':'') + '">' + a.type + '</div>'
        + '<div class="s">' + a.time + ' Uhr · ' + (a.location||'') + '</div></div>'
        + (cancelled ? '<span class="pill pill-grey">storniert</span>'
          : '<button class="pill pill-grey" data-cancel="' + a.id + '" style="border:0;cursor:pointer;">stornieren</button>') + '</div>';
    }).join('');
    $$('[data-cancel]', box).forEach(function (b) {
      b.addEventListener('click', function () {
        if (confirm('Termin wirklich stornieren?')) {
          FA.DB.cancelAppointment(b.getAttribute('data-cancel'));
          FA.DB.sendMail(user.email, 'Termin storniert', 'Hallo ' + first + ', dein Termin wurde storniert. Buche gern einen neuen Slot.');
          renderMyAppts(); renderNextAppt();
        }
      });
    });
  }

  /* ---------- Buchungskalender ---------- */
  var calDate = new Date(); calDate.setDate(1);
  var selDateStr = null, selTime = null;

  function renderCalendar() {
    $('#calLabel').textContent = MONTHS[calDate.getMonth()] + ' ' + calDate.getFullYear();
    var grid = $('#calGrid');
    grid.innerHTML = DOW.map(function (d) { return '<div class="cal-dow">' + d + '</div>'; }).join('');
    var year = calDate.getFullYear(), month = calDate.getMonth();
    var firstDow = (new Date(year, month, 1).getDay() + 6) % 7; // Mo=0
    var days = new Date(year, month + 1, 0).getDate();
    var todayStr = FA.util.toDateStr(new Date());
    for (var i = 0; i < firstDow; i++) grid.innerHTML += '<div></div>';
    for (var day = 1; day <= days; day++) {
      var ds = year + '-' + FA.util.pad(month + 1) + '-' + FA.util.pad(day);
      var past = ds < todayStr;
      var cls = 'cal-cell' + (ds === todayStr ? ' today' : '') + (ds === selDateStr ? ' selected' : '');
      grid.innerHTML += '<button class="' + cls + '" ' + (past ? 'disabled' : 'data-day="' + ds + '"') + '>' + day + '</button>';
    }
    $$('[data-day]', grid).forEach(function (c) {
      c.addEventListener('click', function () { selDateStr = c.getAttribute('data-day'); selTime = null; renderCalendar(); renderSlots(); });
    });
  }
  function renderSlots() {
    if (!selDateStr) { $('#slotWrap').style.display = 'none'; return; }
    $('#slotWrap').style.display = 'block';
    $('#slotDate').textContent = fmtDateLong(selDateStr);
    // Belegte Slots (alle Kunden) an diesem Tag → blockieren
    var taken = FA.DB.allAppointments().filter(function (a) { return a.date === selDateStr && a.status !== 'cancelled'; }).map(function (a) { return a.time; });
    $('#slots').innerHTML = SLOT_TIMES.map(function (t) {
      var busy = taken.indexOf(t) !== -1;
      return '<button class="slot' + (t === selTime ? ' selected' : '') + '" ' + (busy ? 'disabled' : 'data-slot="' + t + '"') + '>' + t + '</button>';
    }).join('');
    $$('[data-slot]').forEach(function (s) {
      s.addEventListener('click', function () { selTime = s.getAttribute('data-slot'); renderSlots(); $('#confirmBook').disabled = false; });
    });
    $('#confirmBook').disabled = !selTime;
  }
  $('#calPrev').addEventListener('click', function () { calDate.setMonth(calDate.getMonth() - 1); renderCalendar(); });
  $('#calNext').addEventListener('click', function () { calDate.setMonth(calDate.getMonth() + 1); renderCalendar(); });

  $('#confirmBook').addEventListener('click', function () {
    if (!selDateStr || !selTime) return;
    var type = $('#bookType').value;
    var loc = type.indexOf('Outdoor') !== -1 ? 'Outdoor · Region KW' : (type.indexOf('Online') !== -1 ? 'Online (Video)' : 'Studio Königs Wusterhausen');
    FA.DB.addAppointment({ userId: user.id, date: selDateStr, time: selTime, type: type, status: 'confirmed', location: loc });
    // Bestätigungs-Mail (Demo) an Kunde + Coach
    FA.DB.sendMail(user.email, 'Terminbestätigung: ' + type,
      'Hallo ' + first + ',\n\ndein Termin ist bestätigt:\n' + fmtDateLong(selDateStr) + ' um ' + selTime + ' Uhr\n' + type + ' · ' + loc + '\n\nBis dann!\nFabio');
    FA.DB.sendMail('info@fabioantunes.de', 'Neue Buchung: ' + user.name,
      user.name + ' hat gebucht: ' + fmtDateLong(selDateStr) + ' ' + selTime + ' Uhr · ' + type);

    $('#bookResult').innerHTML =
      '<div class="alert alert-success" style="margin-top:16px;">✓ Termin gebucht! Bestätigung wurde versendet.</div>'
      + '<div class="mail-preview"><div class="mh">📧 Terminbestätigung (Vorschau)</div>'
      + '<div class="row"><b>An:</b> ' + user.email + '</div>'
      + '<div class="row"><b>Betreff:</b> Terminbestätigung: ' + type + '</div>'
      + '<div class="body">' + fmtDateLong(selDateStr) + ' um ' + selTime + ' Uhr · ' + loc + '</div></div>';
    selTime = null; $('#confirmBook').disabled = true;
    renderMyAppts(); renderNextAppt(); renderSlots();
  });

  /* ---------- Trainingsplan ---------- */
  function renderPlan() {
    var tp = user.trainingPlan;
    if (!tp) { $('#planTitle').textContent = 'Noch kein Plan hinterlegt'; return; }
    $('#planTitle').textContent = tp.title;
    $('#planList').innerHTML = tp.exercises.map(function (ex, i) {
      return '<div class="plan-ex"><div class="n">' + (i + 1) + '</div><div class="b"><div class="t">' + ex.name + '</div><div class="s">' + ex.scheme + '</div></div></div>';
    }).join('');
  }

  /* ---------- Erfolge ---------- */
  function renderErfolge() {
    var pr = user.progress || {};
    $('#erfolgeGrid').innerHTML =
      stat(pr.workouts || 0, '', 'Workouts gesamt') + stat(pr.streak || 0, '🔥', 'Aktuelle Streak')
      + stat(pr.volume || '0', 'kg', 'Letztes Volumen') + stat('+1,8', 'kg', 'Gewicht (8 Wo)');
    $('#prList').innerHTML =
      prRow('Bankdrücken', '82,5 kg × 8', 'NEU')
      + prRow('Schrägbankdrücken', '30 kg × 12', '+2,5kg')
      + prRow('Dips', '12 Wdh · KG', '+2 Wdh');
  }
  function prRow(name, val, badge) {
    var isNew = badge === 'NEU';
    return '<div class="appt"><div class="card-icon" style="margin:0;width:40px;height:40px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9V3h12v6M6 9c0 4 3 7 6 7s6-3 6-7M12 16v3M8 22h8"/></svg></div>'
      + '<div class="appt-body"><div class="t">' + name + '</div><div class="s">' + val + '</div></div>'
      + '<span class="pill ' + (isNew ? 'pill-gold' : 'pill-grey') + '">' + badge + '</span></div>';
  }

  /* ---------- Chat ---------- */
  function renderChat() {
    var msgs = FA.DB.messagesFor(user.id);
    var box = $('#chatBox');
    box.innerHTML = msgs.map(function (m) {
      var t = new Date(m.ts); var time = FA.util.pad(t.getHours()) + ':' + FA.util.pad(t.getMinutes());
      return '<div class="msg ' + (m.from === 'member' ? 'out' : 'in') + '">' + escapeHtml(m.text) + '<span class="meta">' + (m.from === 'member' ? 'Du' : 'Fabio') + ' · ' + time + '</span></div>';
    }).join('');
    box.scrollTop = box.scrollHeight;
  }
  function sendChat() {
    var inp = $('#chatInput'); var txt = inp.value.trim();
    if (!txt) return;
    FA.DB.addMessage(user.id, 'member', txt);
    inp.value = '';
    renderChat();
  }
  $('#chatSend').addEventListener('click', sendChat);
  $('#chatInput').addEventListener('keydown', function (e) { if (e.key === 'Enter') sendChat(); });

  /* ---------- Profil ---------- */
  function renderProfile() {
    $('#profileBox').innerHTML =
      row('Name', user.name) + row('E-Mail', user.email) + row('Mitgliedschaft', user.plan)
      + row('Mitglied seit', user.since || '—') + row('Status', 'Aktiv');
  }
  function row(k, v) { return '<div class="panel-row"><div style="flex:1;"><div class="muted" style="font-size:12px;">' + k + '</div><div style="font-weight:600;">' + v + '</div></div></div>'; }

  $('#savePw').addEventListener('click', function () {
    var pw = $('#newPw').value;
    if (pw.length < 6) { $('#pwResult').innerHTML = '<div class="alert alert-error" style="margin-top:12px;">Mindestens 6 Zeichen.</div>'; return; }
    FA.changePassword(user.id, pw);
    $('#pwResult').innerHTML = '<div class="alert alert-success" style="margin-top:12px;">✓ Passwort gespeichert.</div>';
    $('#newPw').value = '';
  });
  $('#logoutBtn').addEventListener('click', function () { FA.logout(); location.href = 'login.html'; });

  function escapeHtml(s) { return s.replace(/[&<>"]/g, function (c) { return { '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;' }[c]; }); }

  /* ---------- Init ---------- */
  renderNextAppt(); renderStats(); renderMyAppts(); renderCalendar(); renderPlan(); renderErfolge(); renderChat(); renderProfile();
})();
