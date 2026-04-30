/* =========================================================
   Fabio Antunes — Prototype Interactivity
   Reines Vanilla-JS, läuft auf allen HTMLs (defensiv).
   ========================================================= */

(function () {
  'use strict';

  /* ---------------------------------------------------------
     Übungs-Definitionen (7 Stück)
     Index in der Liste = ?ex= Query-Parameter (1-basiert)
     --------------------------------------------------------- */
  const EXERCISES = [
    { id: 'bankdruecken',     name: 'Bankdrücken',         scheme: '4 × 8-10',  weight: 80, rest: 90, muscles: ['Brust', 'Schulter (front)', 'Trizeps'] },
    { id: 'schraegbank',      name: 'Schrägbankdrücken',   scheme: '3 × 10-12', weight: 26, rest: 75, muscles: ['Brust (oben)', 'Schulter'] },
    { id: 'butterfly',        name: 'Butterfly',           scheme: '3 × 12-15', weight: 30, rest: 60, muscles: ['Brust'] },
    { id: 'trizepsdruecken',  name: 'Trizepsdrücken',      scheme: '3 × 12',    weight: 35, rest: 60, muscles: ['Trizeps'] },
    { id: 'dips',             name: 'Dips',                scheme: '3 × 8-12',  weight: 0,  rest: 90, muscles: ['Brust', 'Trizeps'] },
    { id: 'franzoesisch',     name: 'Französisch Drücken', scheme: '3 × 12',    weight: 15, rest: 75, muscles: ['Trizeps'] },
    { id: 'stretching',       name: 'Stretching',          scheme: '5 Min',     weight: 0,  rest: 0,  muscles: ['Mobility'] }
  ];

  /* ---------------------------------------------------------
     Health-Demo-Daten
     TODO: später durch echte Health-API (Apple Health / Google Fit) ersetzen
     --------------------------------------------------------- */
  const HEALTH_DEMO = {
    ruhepuls: { value: 58, unit: 'bpm', trend: '−3 bpm · 30 Tage', dir: 'down' },
    schlaf:   { value: 7.2, unit: 'h',  trend: '+0,4 h · 7 Tage',  dir: 'up' },
    hrv:      { value: 68, unit: 'ms', trend: '+5 ms · 30 Tage',  dir: 'up' },
    schritte: { value: '9,4', unit: 'k', trend: '+820 · 7 Tage',  dir: 'up' }
  };

  /* ---------------------------------------------------------
     Hilfsfunktionen
     --------------------------------------------------------- */

  // Sicheres querySelector mit Null-Check
  const $  = (sel, root) => (root || document).querySelector(sel);
  const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));

  // Pfad-basierte Erkennung der aktuellen Seite
  const PAGE = (location.pathname.split('/').pop() || 'index.html').toLowerCase();

  // Query-Parameter lesen
  function qs(key, def) {
    const v = new URLSearchParams(location.search).get(key);
    return v == null ? def : v;
  }

  // localStorage mit JSON-Wrapping (defensiv – falls localStorage geblockt ist)
  function lsGet(key, fallback) {
    try {
      const raw = localStorage.getItem(key);
      return raw == null ? fallback : JSON.parse(raw);
    } catch (e) { return fallback; }
  }
  function lsSet(key, val) {
    try { localStorage.setItem(key, JSON.stringify(val)); } catch (e) {}
  }

  // mm:ss Format
  function fmtTime(sec) {
    sec = Math.max(0, Math.floor(sec));
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0');
  }

  // Heute als YYYY-MM-DD
  function todayKey() {
    const d = new Date();
    return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  }

  /* =========================================================
     1) PAUSE-TIMER  (exercise.html)
     ========================================================= */
  const Timer = (function () {
    const DEFAULT = 90;       // Sekunden Standardpause
    let remaining = DEFAULT;  // verbleibende Sekunden
    let intervalId = null;
    let containerEl = null;
    let timeEl = null;

    function paint() {
      if (timeEl) timeEl.textContent = fmtTime(remaining);
    }

    function tick() {
      if (remaining > 0) {
        remaining -= 1;
        paint();
        if (remaining === 0) onZero();
      }
    }

    function onZero() {
      // Vibration (sofern unterstützt)
      if (navigator.vibrate) {
        try { navigator.vibrate(200); } catch (e) {}
      }
      // 3× grün blinken
      if (containerEl) {
        let blinks = 0;
        const flashColor = '#22c55e';
        const orig = containerEl.style.background;
        const blinkStep = () => {
          containerEl.style.background = blinks % 2 === 0 ? flashColor : orig;
          blinks += 1;
          if (blinks <= 6) {
            setTimeout(blinkStep, 200);
          } else {
            containerEl.style.background = orig;
          }
        };
        blinkStep();
      }
    }

    function start() {
      stop();
      intervalId = setInterval(tick, 1000);
    }

    function stop() {
      if (intervalId) { clearInterval(intervalId); intervalId = null; }
    }

    function reset(toSeconds) {
      remaining = (typeof toSeconds === 'number') ? toSeconds : DEFAULT;
      paint();
      start();
    }

    function add(delta) {
      remaining = Math.max(0, remaining + delta);
      paint();
      if (remaining === 0) onZero();
    }

    function skip() {
      remaining = 0;
      paint();
      onZero();
    }

    function init() {
      containerEl = $('#restTimer');
      if (!containerEl) return; // Timer existiert nur auf exercise.html
      timeEl = $('.rest-timer-time', containerEl);
      if (!timeEl) return;

      // Buttons identifizieren – Reihenfolge in HTML: -15, Skip, +15
      const btns = $$('.timer-btn', containerEl);
      btns.forEach((btn) => {
        const label = (btn.getAttribute('aria-label') || btn.textContent || '').toLowerCase();
        if (label.indexOf('minus') !== -1 || label.indexOf('-15') !== -1) {
          btn.addEventListener('click', () => add(-15));
        } else if (label.indexOf('plus') !== -1 || label.indexOf('+15') !== -1) {
          btn.addEventListener('click', () => add(15));
        } else if (label.indexOf('skip') !== -1) {
          btn.addEventListener('click', skip);
        }
      });

      reset(DEFAULT);
    }

    return { init, reset, add, skip };
  })();

  /* =========================================================
     2) SATZ-TRACKING + 3) KG/WDH BEARBEITBAR + 4) PERSISTENZ (Teilweise)
     ========================================================= */
  function initSets() {
    const setsRoot = $('.sets');
    if (!setsRoot) return; // nur exercise.html

    const exId = currentExerciseId();
    const sets = $$('.set', setsRoot).filter((s) => !s.classList.contains('sets-header'));
    if (sets.length === 0) return;

    // 4) Persistenz – gespeicherte kg/wdh-Werte einlesen
    sets.forEach((row, idx) => {
      const setNum = idx + 1;
      const inputs = $$('.set-input', row);
      // Reihenfolge im DOM: [0] = kg, [1] = wdh
      if (inputs[0]) {
        const stored = lsGet('set_' + exId + '_' + setNum + '_kg', null);
        if (stored != null && stored !== '') inputs[0].value = stored;
        wireNumericInput(inputs[0], 'set_' + exId + '_' + setNum + '_kg');
      }
      if (inputs[1]) {
        const stored = lsGet('set_' + exId + '_' + setNum + '_reps', null);
        if (stored != null && stored !== '') inputs[1].value = stored;
        wireNumericInput(inputs[1], 'set_' + exId + '_' + setNum + '_reps');
      }

      // Häkchen-Button
      const check = $('.set-check', row);
      if (check) {
        check.addEventListener('click', (e) => {
          e.preventDefault();
          markDone(row, sets, exId);
        });
      }
    });
  }

  // Numerische Validierung: nur Zahlen + Komma/Punkt; Speichern bei Blur
  function wireNumericInput(el, storageKey) {
    el.addEventListener('input', () => {
      // Erlaube Ziffern, Punkt, Komma
      const cleaned = el.value.replace(/[^0-9.,]/g, '');
      if (cleaned !== el.value) el.value = cleaned;
    });
    el.addEventListener('blur', () => {
      const val = el.value.trim();
      if (val === '') {
        try { localStorage.removeItem(storageKey); } catch (e) {}
      } else {
        lsSet(storageKey, val);
      }
    });
  }

  function markDone(row, allSets, exId) {
    if (row.classList.contains('done')) return; // schon erledigt
    row.classList.add('done');
    row.classList.remove('active');

    // Häkchen visuell aktiv
    const check = $('.set-check', row);
    if (check) check.classList.add('checked');

    // Nächste, noch nicht erledigte Zeile aktivieren
    const next = allSets.find((s) => !s.classList.contains('done') && s !== row);
    if (next) {
      allSets.forEach((s) => s.classList.remove('active'));
      next.classList.add('active');
    }

    // Pause-Timer auf 90s zurücksetzen
    Timer.reset(90);

    // Wenn alle Sätze erledigt → in History schreiben
    const allDone = allSets.every((s) => s.classList.contains('done'));
    if (allDone) saveHistory(exId, allSets);
  }

  function saveHistory(exId, allSets) {
    const entries = lsGet('history_' + exId, []);
    const today = todayKey();

    // Heutige Werte aus den Inputs sammeln
    const values = allSets.map((row) => {
      const inputs = $$('.set-input', row);
      return {
        kg: parseFloat((inputs[0] && inputs[0].value || '0').replace(',', '.')) || 0,
        reps: parseInt((inputs[1] && inputs[1].value || '0'), 10) || 0
      };
    });
    const bestKg = values.reduce((max, v) => Math.max(max, v.kg), 0);

    // Falls bereits ein Eintrag von heute existiert → ersetzen
    const filtered = entries.filter((e) => e.date !== today);
    filtered.push({ date: today, sets: values, bestKg: bestKg });

    // Nur die letzten 7 Einträge behalten
    while (filtered.length > 7) filtered.shift();

    lsSet('history_' + exId, filtered);
  }

  /* =========================================================
     5) NAVIGATION + Übungs-Daten dynamisch (exercise.html)
     ========================================================= */
  function currentExerciseId() {
    // 1-basierter Query-Parameter, default 1
    let n = parseInt(qs('ex', '1'), 10);
    if (isNaN(n) || n < 1) n = 1;
    if (n > EXERCISES.length) n = EXERCISES.length;
    return EXERCISES[n - 1].id;
  }

  function initExercisePage() {
    if (PAGE !== 'exercise.html') return;

    let n = parseInt(qs('ex', '1'), 10);
    if (isNaN(n) || n < 1) n = 1;
    if (n > EXERCISES.length) n = EXERCISES.length;
    const ex = EXERCISES[n - 1];
    const isLast = (n === EXERCISES.length);

    // Titel + Eyebrow setzen
    const nameEl = $('.topbar-name');
    if (nameEl) nameEl.textContent = ex.name;
    const eyebrow = $('.topbar-eyebrow');
    if (eyebrow) eyebrow.textContent = 'Übung ' + n + ' von ' + EXERCISES.length;
    const titleTag = $('title');
    if (titleTag) titleTag.textContent = ex.name + ' — Fabio Antunes';

    // Progress-Bar prozentual
    const bar = $('.workout-progress-bar');
    if (bar) bar.style.width = Math.round((n / EXERCISES.length) * 100) + '%';

    // Letzte Leistung aus history_*
    renderLastPerf(ex.id);

    // Nächste-Übung-Button
    const cta = $('.sticky-cta a.btn-primary');
    if (cta) {
      if (isLast) {
        cta.textContent = 'Workout abschließen';
        cta.setAttribute('href', 'progress.html');
      } else {
        cta.setAttribute('href', 'exercise.html?ex=' + (n + 1));
        // Text + Pfeil-Icon erhalten – Text-Knoten ersetzen
        // Wir lassen das bestehende Markup (Text + SVG) und ersetzen nur den Text-Knoten
        const textNode = Array.from(cta.childNodes).find((c) => c.nodeType === 3);
        if (textNode) textNode.nodeValue = 'Nächste Übung ';
      }
    }
  }

  function renderLastPerf(exId) {
    const valEl = $('.lastperf-item:not(.target) .lastperf-value');
    const metaEl = $('.lastperf-item:not(.target) .lastperf-meta');
    if (!valEl) return;

    const history = lsGet('history_' + exId, []);
    if (!history.length) return; // Default-Werte aus HTML lassen

    // Best-Wert der letzten 7 Tage = höchstes bestKg
    const best = history.reduce((m, e) => (e.bestKg > m.bestKg ? e : m), history[0]);
    valEl.innerHTML = best.bestKg + '<span class="unit">kg</span>';
    if (metaEl && best.sets) {
      const reps = best.sets.map((s) => s.reps).join(', ');
      metaEl.textContent = '×' + reps;
    }
  }

  /* =========================================================
     6) HEUTE-SCREEN (index.html)
     ========================================================= */
  function initHeute() {
    if (PAGE !== 'index.html' && PAGE !== '' && PAGE !== 'heute.html') return;

    // Streak + Workout-Zeit aus localStorage (Default 0)
    const streak = lsGet('stat_streak', 0);
    const totalMin = lsGet('stat_minutes', 0);

    // Falls die Hero-Card spezielle Stat-Slots hat – defensiv setzen
    // Das Markup hat keine dedizierten Streak-Felder; wir aktualisieren
    // optionale Elemente mit data-stat="streak" / "minutes" wenn vorhanden.
    const streakEl = $('[data-stat="streak"]');
    if (streakEl) streakEl.textContent = streak;
    const minEl = $('[data-stat="minutes"]');
    if (minEl) minEl.textContent = totalMin;

    // 8) Health-Sync-Grid auf heute.html (sofern vorhanden)
    renderHealthGrid();
  }

  /* =========================================================
     8) HEALTH-SYNC-GRID
     ========================================================= */
  function renderHealthGrid() {
    const grid = $('.health-grid');
    if (!grid) return;
    const cards = $$('.health-card', grid);

    // Reihenfolge in HTML: Ruhepuls, Schlaf, HRV, Schritte
    const order = ['ruhepuls', 'schlaf', 'hrv', 'schritte'];
    cards.forEach((card, i) => {
      const key = order[i];
      const data = HEALTH_DEMO[key];
      if (!data) return;
      const valEl = $('.health-value', card);
      const trendEl = $('.health-trend', card);
      if (valEl) valEl.innerHTML = data.value + '<span class="unit">' + data.unit + '</span>';
      if (trendEl) {
        trendEl.textContent = data.trend;
        trendEl.classList.remove('up', 'down');
        trendEl.classList.add(data.dir);
      }
    });
  }

  /* =========================================================
     7) PROGRESS-SCREEN (progress.html)
     ========================================================= */
  function initProgress() {
    if (PAGE !== 'progress.html') return;

    // PR-Erkennung: gibt es in irgendeinem history_*-Eintrag einen neuen Höchstwert
    // (höchster bestKg = letzter Eintrag)?
    const prCards = $$('.pr-card');
    let hasNewPR = false;

    EXERCISES.forEach((ex) => {
      const history = lsGet('history_' + ex.id, []);
      if (history.length < 2) return;
      const last = history[history.length - 1];
      const prev = history.slice(0, -1);
      const prevMax = prev.reduce((m, e) => Math.max(m, e.bestKg), 0);
      if (last.bestKg > prevMax) hasNewPR = true;
    });

    // NEU-Badge entfernen, wenn keine echten PRs vorliegen
    if (!hasNewPR) {
      prCards.forEach((card) => {
        if (card.classList.contains('new')) {
          card.classList.remove('new');
          const badge = $('.pr-badge', card);
          if (badge) badge.remove();
        }
      });
    }

    // 8-Wochen-Chart aus history_*-Keys neu rendern, sofern Daten existieren
    renderHistoryChart();

    // Health-Grid auf progress.html ebenfalls rendern (falls vorhanden)
    renderHealthGrid();
  }

  function renderHistoryChart() {
    const chartSvg = $('.chart svg');
    if (!chartSvg) return;

    // Sammle Volumen pro Tag (alle Übungen) der letzten 8 Tage
    const allDates = new Set();
    const byDate = {};
    EXERCISES.forEach((ex) => {
      const hist = lsGet('history_' + ex.id, []);
      hist.forEach((e) => {
        allDates.add(e.date);
        const vol = (e.sets || []).reduce((sum, s) => sum + (s.kg * s.reps), 0);
        byDate[e.date] = (byDate[e.date] || 0) + vol;
      });
    });

    const dates = Array.from(allDates).sort();
    if (dates.length < 2) return; // zu wenig Daten – Demo-Chart belassen

    const lastN = dates.slice(-8);
    const values = lastN.map((d) => byDate[d] || 0);
    const max = Math.max.apply(null, values) || 1;

    // Punkte berechnen (320 × 140 viewBox, Padding oben 20, unten 20)
    const w = 320, h = 140, padTop = 20, padBot = 20;
    const step = (lastN.length > 1) ? w / (lastN.length - 1) : 0;
    const pts = values.map((v, i) => {
      const x = i * step;
      const y = padTop + (1 - v / max) * (h - padTop - padBot);
      return [x, y];
    });

    const linePath = pts.map((p, i) => (i === 0 ? 'M' : 'L') + p[0].toFixed(1) + ',' + p[1].toFixed(1)).join(' ');
    const areaPath = linePath + ' L' + w + ',' + h + ' L0,' + h + ' Z';

    // Pfade tauschen
    const paths = $$('path', chartSvg);
    if (paths[0]) paths[0].setAttribute('d', areaPath); // Area
    if (paths[1]) paths[1].setAttribute('d', linePath); // Line

    // Letzten Punkt-Marker setzen
    const lastPt = pts[pts.length - 1];
    const circles = $$('circle', chartSvg);
    if (circles[0] && lastPt) { circles[0].setAttribute('cx', lastPt[0].toFixed(1)); circles[0].setAttribute('cy', lastPt[1].toFixed(1)); }
    if (circles[1] && lastPt) { circles[1].setAttribute('cx', lastPt[0].toFixed(1)); circles[1].setAttribute('cy', lastPt[1].toFixed(1)); }
  }

  /* =========================================================
     Boot
     ========================================================= */
  function boot() {
    Timer.init();
    initExercisePage();
    initSets();
    initHeute();
    initProgress();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
