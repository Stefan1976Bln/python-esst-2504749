/* =========================================================
   Fabio Antunes Prime Coaching — Admin / Verwaltung
   Buchungskalender · Anfragen · Mitglieder · Nachrichten · Postausgang
   ========================================================= */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  // Zugriffsschutz: nur Admin (Fabio)
  var admin = FA.requireRole('admin');
  if (!admin) return;

  var MONTHS = ['Januar','Februar','März','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember'];
  var MONTHS_SHORT = ['JAN','FEB','MÄR','APR','MAI','JUN','JUL','AUG','SEP','OKT','NOV','DEZ'];
  var DOW = ['Mo','Di','Mi','Do','Fr','Sa','So'];

  $('#whoName').textContent = admin.name;

  /* ---------- Tabs ---------- */
  function showTab(name) {
    $$('#tabs button').forEach(function (b) { b.classList.toggle('active', b.getAttribute('data-tab') === name); });
    $$('.tab-panel').forEach(function (p) { p.classList.toggle('active', p.getAttribute('data-panel') === name); });
    window.scrollTo(0, 0);
  }
  $$('#tabs button').forEach(function (b) { b.addEventListener('click', function () { showTab(b.getAttribute('data-tab')); }); });

  function userName(id) { var u = FA.DB.all().users.find(function (x) { return x.id === id; }); return u ? u.name : id; }
  function fmtDateLong(ds) { var p = ds.split('-'); var d = new Date(+p[0], +p[1]-1, +p[2]); return DOW[(d.getDay()+6)%7] + ', ' + d.getDate() + '. ' + MONTHS[d.getMonth()]; }

  /* ---------- Kalender ---------- */
  var calDate = new Date(); calDate.setDate(1);
  var selDay = FA.util.toDateStr(new Date());

  function renderCalendar() {
    $('#calLabel').textContent = MONTHS[calDate.getMonth()] + ' ' + calDate.getFullYear();
    var grid = $('#calGrid');
    grid.innerHTML = DOW.map(function (d) { return '<div class="cal-dow">' + d + '</div>'; }).join('');
    var year = calDate.getFullYear(), month = calDate.getMonth();
    var firstDow = (new Date(year, month, 1).getDay() + 6) % 7;
    var days = new Date(year, month + 1, 0).getDate();
    var todayStr = FA.util.toDateStr(new Date());
    var busyDays = {};
    FA.DB.allAppointments().forEach(function (a) { if (a.status !== 'cancelled') busyDays[a.date] = true; });
    for (var i = 0; i < firstDow; i++) grid.innerHTML += '<div></div>';
    for (var day = 1; day <= days; day++) {
      var ds = year + '-' + FA.util.pad(month + 1) + '-' + FA.util.pad(day);
      var cls = 'cal-cell' + (ds === todayStr ? ' today' : '') + (ds === selDay ? ' selected' : '') + (busyDays[ds] ? ' has-event' : '');
      grid.innerHTML += '<button class="' + cls + '" data-day="' + ds + '">' + day + '</button>';
    }
    $$('[data-day]', grid).forEach(function (c) {
      c.addEventListener('click', function () { selDay = c.getAttribute('data-day'); renderCalendar(); renderDay(); });
    });
  }
  function renderDay() {
    $('#dayLabel').textContent = fmtDateLong(selDay);
    var appts = FA.DB.allAppointments().filter(function (a) { return a.date === selDay; });
    var box = $('#dayAppts');
    if (!appts.length) { box.innerHTML = '<div class="empty">Keine Termine an diesem Tag.</div>'; return; }
    box.innerHTML = appts.map(function (a) {
      var cancelled = a.status === 'cancelled';
      return '<div class="appt"><div class="appt-date"><div class="d">' + a.time.split(':')[0] + '</div><div class="m">' + a.time.split(':')[1] + '</div></div>'
        + '<div class="appt-body"><div class="t" style="' + (cancelled?'text-decoration:line-through;opacity:.5;':'') + '">' + userName(a.userId) + '</div>'
        + '<div class="s">' + a.type + ' · ' + (a.location||'') + '</div></div>'
        + (cancelled ? '<span class="pill pill-grey">storniert</span>'
          : '<button class="pill pill-grey" data-cancel="' + a.id + '" style="border:0;cursor:pointer;">absagen</button>') + '</div>';
    }).join('');
    $$('[data-cancel]', box).forEach(function (b) {
      b.addEventListener('click', function () {
        if (confirm('Termin absagen?')) { FA.DB.cancelAppointment(b.getAttribute('data-cancel')); renderCalendar(); renderDay(); }
      });
    });
  }
  $('#calPrev').addEventListener('click', function () { calDate.setMonth(calDate.getMonth() - 1); renderCalendar(); });
  $('#calNext').addEventListener('click', function () { calDate.setMonth(calDate.getMonth() + 1); renderCalendar(); });

  /* ---------- Termin manuell anlegen ---------- */
  function fillMemberSelect() {
    var sel = $('#newFor');
    sel.innerHTML = FA.DB.members().map(function (m) { return '<option value="' + m.id + '">' + m.name + '</option>'; }).join('');
    var d = new Date(); d.setDate(d.getDate() + 1);
    $('#newDate').value = FA.util.toDateStr(d);
  }
  $('#addAppt').addEventListener('click', function () {
    var uid = $('#newFor').value, date = $('#newDate').value, time = $('#newTime').value, type = $('#newType').value;
    if (!uid || !date || !time) { $('#addResult').innerHTML = '<div class="alert alert-error" style="margin-top:12px;">Bitte alle Felder ausfüllen.</div>'; return; }
    var loc = type.indexOf('Outdoor') !== -1 ? 'Outdoor · Region KW' : (type.indexOf('Online') !== -1 ? 'Online (Video)' : 'Studio Königs Wusterhausen');
    FA.DB.addAppointment({ userId: uid, date: date, time: time, type: type, status: 'confirmed', location: loc });
    var u = FA.DB.members().find(function (m) { return m.id === uid; });
    if (u) FA.DB.sendMail(u.email, 'Terminbestätigung: ' + type, 'Hallo ' + u.name.split(' ')[0] + ', Fabio hat einen Termin für dich eingetragen:\n' + fmtDateLong(date) + ' um ' + time + ' Uhr · ' + type);
    $('#addResult').innerHTML = '<div class="alert alert-success" style="margin-top:12px;">✓ Termin angelegt & Bestätigung versendet.</div>';
    calDate = new Date(date); calDate.setDate(1); selDay = date;
    renderCalendar(); renderDay();
  });

  /* ---------- Anfragen / Leads ---------- */
  function renderLeads() {
    var leads = FA.DB.leads();
    var cnt = $('#leadCount');
    if (leads.length) { cnt.style.display = 'inline-flex'; cnt.textContent = leads.length; } else { cnt.style.display = 'none'; }
    var box = $('#leadList');
    if (!leads.length) { box.innerHTML = '<div class="empty">Keine offenen Anfragen. Neue Erstgespräch-Anfragen von der Website erscheinen hier.</div>'; return; }
    box.innerHTML = leads.map(function (l) {
      return '<div class="member"><div class="avatar">' + initials(l.name) + '</div>'
        + '<div class="b"><div class="t">' + esc(l.name) + '</div><div class="s">' + esc(l.email) + (l.phone ? ' · ' + esc(l.phone) : '') + '</div>'
        + '<div class="s">Interesse: ' + esc(l.plan) + ' · ' + esc(l.format) + (l.date ? ' · Wunsch: ' + l.date : '') + '</div>'
        + (l.message ? '<div class="s" style="margin-top:4px;color:var(--text-2);">„' + esc(l.message) + '"</div>' : '') + '</div>'
        + '<span class="pill pill-gold">' + l.status + '</span></div>';
    }).join('');
  }

  /* ---------- Mitglieder ---------- */
  function renderMembers() {
    var members = FA.DB.members();
    $('#memberList').innerHTML = members.map(function (m) {
      var appts = FA.DB.appointmentsFor(m.id).filter(function (a) { return a.status !== 'cancelled'; }).length;
      return '<div class="member"><div class="avatar">' + initials(m.name) + '</div>'
        + '<div class="b"><div class="t">' + esc(m.name) + '</div><div class="s">' + esc(m.email) + '</div>'
        + '<div class="s">' + esc(m.plan) + ' · seit ' + (m.since || '—') + '</div></div>'
        + '<div class="meta">' + appts + ' Termine<br/><span class="pill pill-green" style="margin-top:4px;">Aktiv</span></div></div>';
    }).join('');
  }

  /* ---------- Nachrichten ---------- */
  var activeConv = null;
  function renderConvList() {
    var members = FA.DB.members();
    $('#convSelect').innerHTML = '<div class="app-h" style="margin:0 0 8px;">Unterhaltungen</div>' + members.map(function (m) {
      var msgs = FA.DB.messagesFor(m.id);
      var last = msgs.length ? msgs[msgs.length - 1].text : 'Noch keine Nachrichten';
      return '<div class="member" style="cursor:pointer;" data-conv="' + m.id + '"><div class="avatar">' + initials(m.name) + '</div>'
        + '<div class="b"><div class="t">' + esc(m.name) + '</div><div class="s" style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">' + esc(last) + '</div></div>'
        + '<svg viewBox="0 0 24 24" fill="none" stroke="var(--text-3)" stroke-width="2" style="width:18px;"><path d="m9 18 6-6-6-6"/></svg></div>';
    }).join('');
    $$('[data-conv]').forEach(function (el) { el.addEventListener('click', function () { activeConv = el.getAttribute('data-conv'); renderConv(); }); });
  }
  function renderConv() {
    if (!activeConv) return;
    $('#convBox').style.display = 'block';
    var msgs = FA.DB.messagesFor(activeConv);
    $('#adminChat').innerHTML = msgs.map(function (m) {
      var t = new Date(m.ts); var time = FA.util.pad(t.getHours()) + ':' + FA.util.pad(t.getMinutes());
      // Aus Admin-Sicht: 'admin' = ausgehend (rechts), 'member' = eingehend (links)
      return '<div class="msg ' + (m.from === 'admin' ? 'out' : 'in') + '">' + esc(m.text) + '<span class="meta">' + (m.from === 'admin' ? 'Du' : userName(activeConv)) + ' · ' + time + '</span></div>';
    }).join('');
    var box = $('#adminChat'); box.scrollTop = box.scrollHeight;
  }
  function adminSend() {
    if (!activeConv) return;
    var inp = $('#adminMsg'); var txt = inp.value.trim();
    if (!txt) return;
    FA.DB.addMessage(activeConv, 'admin', txt);
    inp.value = ''; renderConv(); renderConvList();
  }
  $('#adminSend').addEventListener('click', adminSend);
  $('#adminMsg').addEventListener('keydown', function (e) { if (e.key === 'Enter') adminSend(); });

  /* ---------- Postausgang ---------- */
  function renderMails() {
    var mails = FA.DB.outbox();
    var box = $('#mailList');
    if (!mails.length) { box.innerHTML = '<div class="empty">Noch keine Mails versendet.</div>'; return; }
    box.innerHTML = mails.map(function (m) {
      var t = new Date(m.ts);
      return '<div class="mail-preview" style="margin:0 0 10px;"><div class="mh">📧 ' + t.toLocaleString('de-DE') + '</div>'
        + '<div class="row"><b>An:</b> ' + esc(m.to) + '</div>'
        + '<div class="row"><b>Betreff:</b> ' + esc(m.subject) + '</div>'
        + '<div class="body">' + esc(m.body) + '</div></div>';
    }).join('');
  }

  /* ---------- Helfer ---------- */
  function initials(name) { return name.split(' ').map(function (w) { return w[0]; }).slice(0, 2).join('').toUpperCase(); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;' }[c]; }); }

  $('#logoutBtn').addEventListener('click', function () { FA.logout(); location.href = 'login.html'; });

  /* ---------- Init ---------- */
  fillMemberSelect();
  renderCalendar(); renderDay(); renderLeads(); renderMembers(); renderConvList(); renderMails();
})();
