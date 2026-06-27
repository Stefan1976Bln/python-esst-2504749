/* =========================================================
   Fabio Antunes Prime Coaching — Landingpage Interaktivität
   Burger-Menü · FAQ-Accordion · Buchungs-Modal (Erstgespräch)
   Defensiv: alle Selektoren mit Null-Check.
   ========================================================= */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ---------- Mobile-Menü ---------- */
  var burger = $('#burger'), menu = $('#mobileMenu');
  if (burger && menu) {
    burger.addEventListener('click', function () { menu.classList.toggle('open'); });
    $$('#mobileMenu a').forEach(function (a) { a.addEventListener('click', function () { menu.classList.remove('open'); }); });
  }

  /* ---------- FAQ dynamisch aufbauen ---------- */
  var FAQ = [
    ['Brauche ich Vorerfahrung?', 'Nein. Das Training wird exakt auf deinen aktuellen Stand abgestimmt – egal ob Einsteiger oder Fortgeschritten.'],
    ['Trainierst du auch Anfänger?', 'Ja, sehr gerne. Gerade am Anfang ist eine saubere Technik und der richtige Aufbau entscheidend.'],
    ['Wo findet das Training statt?', 'Im Studio in Königs Wusterhausen, outdoor in der Region (Wildau, Zeuthen, Eichwalde, Berlin Süd) oder online als Hybrid Coaching.'],
    ['Gibt es Online Coaching?', 'Ja. Das Hybrid Coaching kombiniert Vor-Ort-Einheiten mit Online-Betreuung und ist deutschlandweit möglich.'],
    ['Wie oft trainieren wir?', 'Je nach Paket 4–12 Einheiten pro Monat, ergänzt durch eigenständige Einheiten nach Plan.'],
    ['Wie lange dauert ein Coaching?', 'Nachhaltige Veränderung braucht Zeit. Wir denken in Monaten, nicht in Wochen – die meisten Kunden bleiben langfristig.'],
    ['Was kostet das Coaching?', 'Die Pakete starten bei 499 €/Monat (PRIME START). Details findest du im Abschnitt „Pakete".'],
    ['Wie läuft das Erstgespräch ab?', '30–45 Minuten, kostenlos und unverbindlich – online oder vor Ort. Wir klären Ziele, Ausgangslage und ob es passt.'],
    ['Gibt es Ernährungsberatung?', 'Ja. Alltagstaugliche Ernährungsstrategien sind fester Bestandteil jedes Coachings (Ernährungsberater A-Lizenz).'],
    ['Was passiert, wenn ich wenig Zeit habe?', 'Genau dafür ist die Methode gemacht: Wir bauen Routinen, die in deinen Alltag passen – nicht umgekehrt.']
  ];
  var faqList = $('#faqList');
  if (faqList) {
    FAQ.forEach(function (item) {
      var el = document.createElement('div');
      el.className = 'faq-item';
      el.innerHTML =
        '<button class="faq-q">' + item[0] +
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg></button>' +
        '<div class="faq-a"><p>' + item[1] + '</p></div>';
      faqList.appendChild(el);
      var q = $('.faq-q', el), a = $('.faq-a', el);
      q.addEventListener('click', function () {
        var open = el.classList.toggle('open');
        a.style.maxHeight = open ? (a.scrollHeight + 'px') : '0';
      });
    });
  }

  /* ---------- Buchungs-Modal ---------- */
  var modal = $('#bookModal');
  function openModal(plan) {
    if (!modal) return;
    var sel = $('#bk-plan');
    if (plan && sel) {
      $$('option', sel).forEach(function (o) { if (o.value === plan || o.textContent === plan) sel.value = o.value; });
    }
    // Standard-Wunschtermin: in 3 Tagen
    var d = new Date(); d.setDate(d.getDate() + 3);
    var di = $('#bk-date'); if (di) di.value = (window.FA ? FA.util.toDateStr(d) : '');
    modal.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function closeModal() { if (modal) { modal.classList.remove('open'); document.body.style.overflow = ''; } }

  $$('[data-book]').forEach(function (b) {
    b.addEventListener('click', function (e) { e.preventDefault(); openModal(b.getAttribute('data-plan')); });
  });
  $$('[data-close]').forEach(function (b) { b.addEventListener('click', closeModal); });
  if (modal) modal.addEventListener('click', function (e) { if (e.target === modal) closeModal(); });

  /* ---------- Anfrage absenden (Lead + simulierte Mail) ---------- */
  var submit = $('#bk-submit');
  if (submit) {
    submit.addEventListener('click', function () {
      var name = ($('#bk-name') || {}).value || '';
      var email = ($('#bk-email') || {}).value || '';
      if (!name.trim() || !email.trim()) { alert('Bitte Name und E-Mail angeben.'); return; }

      var lead = {
        name: name.trim(), email: email.trim(),
        phone: ($('#bk-phone') || {}).value || '',
        plan: ($('#bk-plan') || {}).value || '',
        format: ($('#bk-format') || {}).value || '',
        date: ($('#bk-date') || {}).value || '',
        message: ($('#bk-msg') || {}).value || ''
      };

      // In Demo-DB speichern, damit Fabio die Anfrage im Admin-Bereich sieht
      if (window.FA) {
        FA.DB.addLead(lead);
        // Bestätigungs-Mail an den Interessenten (Demo)
        FA.DB.sendMail(lead.email, 'Deine Anfrage bei Fabio Antunes Prime Coaching',
          'Hallo ' + lead.name + ',\n\nvielen Dank für deine Anfrage zum kostenlosen Erstgespräch'
          + (lead.date ? ' (Wunschtermin: ' + lead.date + ')' : '') + '.\n'
          + 'Fabio meldet sich kurzfristig bei dir zur Terminabstimmung.\n\nPremium. Nachhaltigkeit. Lebensstilveränderung.\nFabio Antunes Prime Coaching');
        // Benachrichtigung an Fabio (Demo)
        FA.DB.sendMail('info@fabioantunes.de', 'Neue Erstgespräch-Anfrage: ' + lead.name,
          'Neue Anfrage über die Website:\n\nName: ' + lead.name + '\nE-Mail: ' + lead.email
          + '\nTelefon: ' + (lead.phone || '–') + '\nPaket-Interesse: ' + lead.plan
          + '\nFormat: ' + lead.format + '\nWunschtermin: ' + (lead.date || '–')
          + '\nNachricht: ' + (lead.message || '–'));
      }

      // Erfolgsansicht inkl. E-Mail-Vorschau
      var form = $('#bookForm'), done = $('#bookDone');
      if (form) form.style.display = 'none';
      if (done) {
        done.style.display = 'block';
        done.innerHTML =
          '<div class="alert alert-success">✓ Anfrage gesendet! Fabio meldet sich zeitnah bei dir.</div>'
          + '<div class="mail-preview"><div class="mh">📧 Bestätigungs-Mail (Vorschau)</div>'
          + '<div class="row"><b>An:</b> ' + lead.email + '</div>'
          + '<div class="row"><b>Betreff:</b> Deine Anfrage bei Fabio Antunes Prime Coaching</div>'
          + '<div class="body">Hallo ' + lead.name + ', vielen Dank für deine Anfrage'
          + (lead.date ? ' (Wunschtermin: ' + lead.date + ')' : '') + '. Fabio meldet sich kurzfristig zur Terminabstimmung.</div></div>'
          + '<p class="form-note" style="margin-top:14px;">Hinweis: Im Demo wird keine echte E-Mail verschickt. Auf der Live-Version (Ionos) übernimmt das PHPMailer über den Ionos-SMTP-Server.</p>'
          + '<button class="btn btn-ghost btn-block" data-close style="margin-top:14px;">Schließen</button>';
        $('[data-close]', done).addEventListener('click', function () {
          closeModal();
          if (form) form.style.display = 'block';
          done.style.display = 'none';
        });
      }
    });
  }
})();
