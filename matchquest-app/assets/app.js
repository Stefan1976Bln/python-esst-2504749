/* =========================================================
   MatchQuest — App-Logik (Kunden-WebApp)
   Views: Spiele/Lobby · Live-Challenge · Leaderboard
   ========================================================= */
(function () {
  'use strict';

  var MQ = window.MQ;
  var Engine = window.MQChallenges;
  var user = MQ.Auth.requireLogin();
  if (!user) return;

  /* Demo-Taktung: echte App = alle 10 Min. Hier beschleunigt,
     damit man es sofort ausprobieren kann. */
  var NEXT_CHALLENGE_SECONDS = 20;

  var state = {
    matchId: null,        // Lobby, der beigetreten wurde
    mode: 'curated',      // 'curated' (Stufe 1) | 'ki' (Stufe 2)
    challenge: null,
    answered: false
  };
  var timers = { next: null, answer: null, matchList: null };

  /* ---------------- Helpers ---------------- */
  function $(id) { return document.getElementById(id); }
  function clear(t) { if (t) { clearInterval(t); } return null; }
  function fmt(sec) {
    sec = Math.max(0, Math.round(sec));
    var m = Math.floor(sec / 60), s = sec % 60;
    return m + ':' + (s < 10 ? '0' : '') + s;
  }
  function kickoffDiff(iso) { return (new Date(iso).getTime() - Date.now()) / 1000; }

  /* ---------------- Navigation ---------------- */
  function showView(name) {
    document.querySelectorAll('.view').forEach(function (v) { v.classList.remove('active'); });
    var v = $('view-' + name); if (v) v.classList.add('active');
    document.querySelectorAll('.nav-btn[data-view]').forEach(function (b) {
      b.classList.toggle('active', b.getAttribute('data-view') === name);
    });
    if (name === 'leaderboard') renderLeaderboard();
    if (name === 'live') renderLiveView();
  }

  document.querySelectorAll('.nav-btn[data-view]').forEach(function (b) {
    b.addEventListener('click', function () { showView(b.getAttribute('data-view')); });
  });
  document.addEventListener('click', function (e) {
    var g = e.target.getAttribute && e.target.getAttribute('data-goto');
    if (g) showView(g);
  });

  $('logout').addEventListener('click', function () { MQ.Auth.logout(); window.location.href = 'index.html'; });
  $('who').textContent = '👤 ' + user.name;
  $('reset-demo').addEventListener('click', function (e) {
    e.preventDefault();
    if (confirm('Alle Demo-Daten zurücksetzen und abmelden?')) { MQ.resetDemo(); window.location.href = 'index.html'; }
  });

  /* ---------------- Spiele / Lobby ---------------- */
  function renderMatches() {
    var matches = MQ.DB.getMatches();
    var host = $('match-list');
    host.innerHTML = '';
    matches.forEach(function (m) {
      var diff = kickoffDiff(m.kickoff);
      var live = diff <= 0;
      var joined = state.matchId === m.id;

      var card = document.createElement('div');
      card.className = 'card match';
      card.innerHTML =
        '<span class="pill ' + (live ? 'live' : 'soon') + '">' + (live ? '● LIVE' : 'Bald') + '</span>' +
        '<div>' +
          '<div class="teams"><span class="flag">' + m.homeFlag + '</span> ' + m.home +
          ' <span class="muted">vs</span> ' + m.away + ' <span class="flag">' + m.awayFlag + '</span></div>' +
          '<div class="meta">' + m.stage + ' · ' + m.venue + '</div>' +
        '</div>' +
        '<span class="spacer"></span>' +
        '<div style="text-align:right">' +
          '<div class="meta">' + (live ? 'läuft' : 'Anpfiff in') + '</div>' +
          '<div class="countdown" data-kickoff="' + m.kickoff + '">' + (live ? '⏱️' : fmt(diff)) + '</div>' +
        '</div>';

      var actions = document.createElement('div');
      actions.style.width = '100%';
      actions.style.display = 'flex';
      actions.style.gap = '10px';
      actions.style.flexWrap = 'wrap';
      actions.style.marginTop = '4px';

      var joinBtn = document.createElement('button');
      joinBtn.className = 'btn ' + (joined ? 'green' : 'primary');
      joinBtn.textContent = joined ? '✅ In Lobby — zur Live-Challenge' : '➕ Challenge-Lobby beitreten';
      joinBtn.addEventListener('click', function () {
        joinLobby(m.id);
      });

      var liveLink = document.createElement('a');
      liveLink.className = 'btn ghost';
      liveLink.href = m.liveUrl; liveLink.target = '_blank'; liveLink.rel = 'noopener';
      liveLink.textContent = '📺 Spiel live verfolgen';

      actions.appendChild(joinBtn);
      actions.appendChild(liveLink);
      card.appendChild(actions);
      host.appendChild(card);
    });
  }

  // Countdown-Ticker der Spielliste
  timers.matchList = setInterval(function () {
    document.querySelectorAll('#match-list .countdown[data-kickoff]').forEach(function (el) {
      var diff = kickoffDiff(el.getAttribute('data-kickoff'));
      el.textContent = diff <= 0 ? '⏱️' : fmt(diff);
    });
  }, 1000);

  function joinLobby(matchId) {
    state.matchId = matchId;
    renderMatches();
    showView('live');
    startLobby();
  }

  /* ---------------- Live-Challenge ---------------- */
  $('ki-toggle').addEventListener('change', function () {
    state.mode = this.checked ? 'ki' : 'curated';
  });

  function renderLiveView() {
    var hasLobby = !!state.matchId;
    $('live-empty').style.display = hasLobby ? 'none' : '';
    $('live-active').style.display = hasLobby ? '' : 'none';
    if (hasLobby) {
      var m = MQ.DB.getMatch(state.matchId);
      $('live-match').textContent = m ? (m.homeFlag + ' ' + m.home + ' vs ' + m.away + ' ' + m.awayFlag) : '';
    }
  }

  function startLobby() {
    renderLiveView();
    // Erste Challenge kommt sofort, danach im Takt.
    spawnChallenge();
    scheduleNext();
  }

  function scheduleNext() {
    timers.next = clear(timers.next);
    var remaining = NEXT_CHALLENGE_SECONDS;
    $('next-timer').textContent = '⏳ Nächste Live-Challenge in ' + fmt(remaining);
    timers.next = setInterval(function () {
      remaining -= 1;
      if (remaining <= 0) {
        $('next-timer').textContent = '';
        spawnChallenge();
        scheduleNext();
        return;
      }
      $('next-timer').textContent = '⏳ Nächste Live-Challenge in ' + fmt(remaining);
    }, 1000);
  }

  function spawnChallenge() {
    var m = MQ.DB.getMatch(state.matchId);
    var c = Engine.nextChallenge({ mode: state.mode, match: m });
    state.challenge = c;
    state.answered = false;

    var card = $('challenge-card');
    card.style.display = '';
    $('challenge-result').style.display = 'none';
    $('skip-challenge').style.display = '';

    // Quelle-Badge
    var src = $('challenge-source');
    if (c.source === 'ki') { src.className = 'pill ki'; src.textContent = '🤖 KI-Challenge · geprüft'; }
    else { src.className = 'pill curated'; src.textContent = '🎯 Live-Challenge'; }

    $('challenge-q').textContent = c.text;

    // Optionen (Wette) vs. Aktion
    var optsHost = $('challenge-opts');
    optsHost.innerHTML = '';
    if (c.type === 'bet') {
      $('challenge-action').style.display = 'none';
      c.options.forEach(function (opt) {
        var b = document.createElement('button');
        b.className = 'btn';
        b.textContent = opt;
        b.addEventListener('click', function () { answerBet(opt, b); });
        optsHost.appendChild(b);
      });
    } else {
      $('challenge-action').style.display = '';
      resetProof();
    }

    // Antwort-Countdown
    startAnswerTimer(c.answerSeconds);
  }

  function startAnswerTimer(seconds) {
    timers.answer = clear(timers.answer);
    var remaining = seconds;
    var el = $('challenge-timer');
    el.textContent = '⏱️ ' + fmt(remaining) + ' Zeit zum Antworten';
    timers.answer = setInterval(function () {
      remaining -= 1;
      if (remaining <= 0) {
        timers.answer = clear(timers.answer);
        if (!state.answered) timeout();
        return;
      }
      el.textContent = '⏱️ ' + fmt(remaining) + ' Zeit zum Antworten';
    }, 1000);
  }

  function lockChallenge() {
    state.answered = true;
    timers.answer = clear(timers.answer);
    $('challenge-timer').textContent = '';
    $('skip-challenge').style.display = 'none';
  }

  function banner(kind, text) {
    var b = $('challenge-result');
    b.className = 'result-banner ' + kind;
    b.textContent = text;
    b.style.display = '';
  }

  /* --- Wett-Challenge --- */
  function answerBet(choice, btnEl) {
    if (state.answered) return;
    lockChallenge();
    // "Live"-Ergebnis wird ermittelt (im Prototyp zufällig).
    var opts = state.challenge.options;
    var correct = opts[Math.floor(Math.random() * opts.length)];
    Array.prototype.forEach.call($('challenge-opts').children, function (b) {
      b.disabled = true;
      if (b.textContent === correct) b.classList.add('correct');
      if (b === btnEl && choice !== correct) b.classList.add('wrong');
    });
    if (choice === correct) {
      MQ.DB.addResult(user.id, { points: state.challenge.points, correctBet: true });
      banner('ok', '🎉 Richtig getippt! +' + state.challenge.points + ' Punkte');
    } else {
      banner('bad', '😅 Diesmal daneben — richtig war: ' + correct + '. Nächste Challenge kommt gleich!');
    }
    refreshUserAndStats();
  }

  /* --- Aktions-Challenge: Beweis + Orakel --- */
  function resetProof() {
    $('proof-input').value = '';
    $('proof-preview').innerHTML = '';
    $('oracle-confirm').disabled = true;
    $('oracle-reject').disabled = true;
  }

  $('proof-input').addEventListener('change', function () {
    var file = this.files && this.files[0];
    var host = $('proof-preview');
    host.innerHTML = '';
    if (!file) return;
    var url = URL.createObjectURL(file);
    var el = file.type.indexOf('video') === 0 ? document.createElement('video') : document.createElement('img');
    if (el.tagName === 'VIDEO') { el.controls = true; }
    el.src = url;
    host.appendChild(el);
    // Orakel darf jetzt bestätigen
    $('oracle-confirm').disabled = false;
    $('oracle-reject').disabled = false;
  });

  $('oracle-confirm').addEventListener('click', function () {
    if (state.answered) return;
    lockChallenge();
    MQ.DB.addResult(user.id, { points: state.challenge.points, challengeDone: true });
    banner('ok', '✅ Vom Orakel bestätigt! +' + state.challenge.points + ' Punkte');
    refreshUserAndStats();
  });
  $('oracle-reject').addEventListener('click', function () {
    if (state.answered) return;
    lockChallenge();
    banner('bad', '👁️ Orakel hat nicht bestätigt — keine Punkte. Weiter geht\'s!');
  });

  function timeout() {
    lockChallenge();
    if (state.challenge && state.challenge.type === 'bet') {
      Array.prototype.forEach.call($('challenge-opts').children, function (b) { b.disabled = true; });
    }
    banner('bad', '⏰ Zeit abgelaufen — keine Antwort. Die nächste Challenge kommt gleich!');
  }

  $('skip-challenge').addEventListener('click', function () {
    lockChallenge();
    banner('bad', '⏭️ Übersprungen. Nächste Challenge kommt gleich.');
  });

  /* ---------------- Leaderboard & Statistik ---------------- */
  function medal(rank) {
    return rank === 1 ? '🥇' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : '';
  }
  function renderLeaderboard() {
    var rows = MQ.DB.friendsLeaderboard(user.id);
    var body = $('lb-body');
    body.innerHTML = '';
    rows.forEach(function (r) {
      var tr = document.createElement('tr');
      if (r.me) tr.className = 'me';
      tr.innerHTML =
        '<td class="rank">' + (medal(r.rank) ? '<span class="medal">' + medal(r.rank) + '</span>' : '') + r.rank + '</td>' +
        '<td>' + (r.me ? '<b>' + r.name + ' (du)</b>' : r.name) + '</td>' +
        '<td>' + r.correctBets + '</td>';
      body.appendChild(tr);
    });
    // Statistik
    var me = MQ.DB.getUser(user.id);
    $('stat-points').textContent = me.points || 0;
    $('stat-bets').textContent = me.correctBets || 0;
    $('stat-challenges').textContent = me.challengesDone || 0;
  }

  function refreshUserAndStats() {
    user = MQ.DB.getUser(user.id);
  }

  /* ---------------- Start ---------------- */
  renderMatches();
  renderLiveView();

})();
