/* MatchQuest — Landingpage: bereits eingeloggte Nutzer weiterleiten,
   sanftes Scrollen für Anker-Links. */
(function () {
  'use strict';
  // Wer schon eingeloggt ist, sieht auf der Startseite den Button "Zur App".
  var u = window.MQ && window.MQ.Auth.currentUser();
  if (u) {
    var cta = document.querySelector('.hero .cta');
    if (cta) {
      var a = document.createElement('a');
      a.className = 'btn green';
      a.href = 'app.html';
      a.textContent = '▶️ Weiter zur App, ' + u.name;
      cta.insertBefore(a, cta.firstChild);
    }
  }

  document.querySelectorAll('a[href^="#"]').forEach(function (link) {
    link.addEventListener('click', function (e) {
      var el = document.querySelector(link.getAttribute('href'));
      if (el) { e.preventDefault(); el.scrollIntoView({ behavior: 'smooth' }); }
    });
  });
})();
