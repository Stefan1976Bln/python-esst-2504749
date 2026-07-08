import pkg from '/opt/node22/lib/node_modules/playwright/index.js';
const { chromium } = pkg;
import { readFileSync, writeFileSync } from 'fs';
writeFileSync('/tmp/pro.html','<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>'+readFileSync('/home/user/python-esst-2504749/matchquest-app/matchquest-pro.html','utf8')+'</body></html>');
const URL='file:///tmp/pro.html';
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
let pass=0,fail=0; const fails=[];
function ok(name,cond){ if(cond){pass++;console.log('  ✅',name);} else {fail++;fails.push(name);console.log('  ❌',name);} }
async function newP(){ const ctx=await b.newContext({viewport:{width:430,height:920}}); const p=await ctx.newPage();
  p.__errs=[]; p.on('console',m=>{if(m.type()==='error'&&!m.text().includes('TUNNEL')&&!m.text().includes('ERR_'))p.__errs.push(m.text());}); p.on('pageerror',e=>p.__errs.push('PE:'+e.message));
  await p.addInitScript(()=>{window.open=(u)=>{window.__open=u;return null;};});
  await p.goto(URL); return p; }
async function consent(p){ await p.check('#c1');await p.check('#c2');await p.check('#c3');await p.click('#consent-accept');await p.waitForTimeout(150); }
async function deLevel(p){ try{ if(await p.locator('#levelup.show').count()){ await p.click('#lu-close'); await p.waitForTimeout(120);} }catch(e){} }

/* ---------- Persona 1: Neuling Nina ---------- */
console.log('\n👩 Neuling Nina — Registrierung & Einwilligung');
{ const p=await newP();
  ok('Landing zeigt "nicht-kommerziell"', (await p.locator('#page-landing').innerText()).toLowerCase().includes('nicht-kommerziell'));
  await p.locator('#page-landing .btn').first().click();
  await p.click('#tab-register');
  ok('Passwort-Feld ist Klartext', await p.getAttribute('#reg-pw','type')==='text');
  await p.fill('#reg-email','nina@test.de');await p.fill('#reg-pw','abcd');await p.fill('#reg-pw2','xxxx');
  await p.click('#form-register button[type=submit]'); await p.waitForTimeout(100);
  ok('Passwort-Mismatch Fehler', (await p.textContent('#reg-error')).includes('stimmen nicht'));
  await p.fill('#reg-pw2','abcd'); await p.click('#form-register button[type=submit]'); await p.waitForTimeout(150);
  ok('Einwilligung erscheint', await p.locator('#consent').evaluate(e=>e.classList.contains('show')));
  ok('Akzeptieren erst gesperrt', await p.locator('#consent-accept').isDisabled());
  await p.click('#consent .consent-line a[data-doc=privacy]'); await p.waitForTimeout(80);
  ok('Datenschutz-Text öffnet', (await p.textContent('#doc-content')).includes('Datenschutz'));
  await p.click('#doc-close');
  await consent(p);
  ok('App gestartet (Name aus E-Mail)', (await p.locator('#page-app').evaluate(e=>e.classList.contains('active'))) && (await p.textContent('#sb-name'))==='nina');
  ok('keine JS-Fehler', p.__errs.length===0);
  await p.context().close(); }

/* ---------- Persona 2: Bettor Ben ---------- */
console.log('\n🎯 Bettor Ben — Wetten, Mehrheit, Rang');
{ const p=await newP();
  await p.locator('#page-landing .btn').first().click();
  await p.fill('#login-email','jonas@matchquest.app');await p.fill('#login-pw','wm2026');await p.click('#form-login button[type=submit]');await p.waitForTimeout(120);
  await consent(p);
  // join real match (Final = last)
  await p.locator('#match-list .card').last().locator('button').first().click(); await p.waitForTimeout(300);
  ok('Live-Ansicht aktiv', await p.locator('#view-live').evaluate(e=>e.classList.contains('active')));
  const coins0=parseInt(await p.textContent('#sb-coins'),10);
  // get a bet
  let bet=false; for(let i=0;i<8;i++){ if(await p.locator('#bet-card').isVisible()){bet=true;break;} await p.waitForTimeout(600);}
  ok('Wett-Challenge erscheint', bet);
  if(bet){ await p.locator('#bet-opts .opt').first().click(); await p.waitForTimeout(120);
    ok('Bestätigungsphase (Mehrheit)', await p.locator('#bet-confirm').isVisible());
    await p.locator('#bet-confirm-opts .opt').first().click(); await p.waitForTimeout(200);
    ok('Ergebnis nennt Mehrheit', (await p.textContent('#bet-result')).includes('Mehrheit')); }
  // leaderboard
  await p.click('.tabbar button[data-view=rank]'); await p.waitForTimeout(150);
  const lbCols=await p.locator('#view-rank thead th').count().catch(()=>0);
  ok('Freunde-Leaderboard hat Zeilen', (await p.locator('#lb-card .lb-row').count())>0);
  await p.click('.tabbar button[data-view=profile]'); await p.waitForTimeout(120);
  ok('Statistik sichtbar', (await p.textContent('#pf-points')).length>0);
  ok('keine JS-Fehler', p.__errs.length===0);
  await p.context().close(); }

/* ---------- Persona 3: Party-Host Petra ---------- */
console.log('\n🎉 Party-Host Petra — Teams, Gruppen-Jury, Videocall');
{ const p=await newP();
  await p.locator('#page-landing .btn').first().click();
  await p.fill('#login-email','stefan@matchquest.app');await p.fill('#login-pw','wm2026');await p.click('#form-login button[type=submit]');await p.waitForTimeout(120);
  await consent(p);
  // join team green
  await p.click('.tabbar button[data-view=rank]');await p.click('#seg-teams');await p.waitForTimeout(150);
  ok('Team-Battle VS', (await p.locator('#lb-card').innerText()).includes('VS'));
  const before=(await p.evaluate(()=>window.MQ.DB.teamStandings()));
  await p.locator('#lb-card .btn').first().click(); await p.waitForTimeout(150);
  ok('Team beigetreten', !!(await p.evaluate(()=>window.MQ.Auth.current().teamId)));
  // freeplay + group jury
  await p.click('.tabbar button[data-view=matches]'); await p.click('#freeplay-btn'); await p.waitForTimeout(200);
  await p.click('#grp-start'); await p.waitForTimeout(200);
  ok('Gruppen-Grid 4 Kacheln', (await p.locator('#grp-grid .vtile').count())===4);
  ok('genau 1 dran (Performer)', (await p.locator('#grp-grid .vtile.player').count())===1);
  // do one round (juror or performer)
  let rounds=0;
  for(let i=0;i<5;i++){
    await deLevel(p);
    if(await p.locator('#grp-scorebtns .btn').count()){ await p.locator('#grp-scorebtns .btn').nth(7).click(); await p.waitForTimeout(150); rounds++; }
    else if(await p.locator('#grp-cam').count()){ await p.click('#grp-cam'); await p.waitForTimeout(250); if(await p.locator('#grp-done').count()){await p.click('#grp-done');await p.waitForTimeout(200);rounds++;} }
    await deLevel(p);
    if(await p.locator('#grp-again').count()) { await p.click('#grp-again'); await p.waitForTimeout(200); }
  }
  await deLevel(p);
  ok('Mind. 1 Jury-Runde gespielt', rounds>=1);
  // team-call room code contains team id
  await p.click('#mode-live'); await p.waitForTimeout(150);
  ok('Team-Raum-Code enthält Team', /-(green|blue)$/.test(await p.inputValue('#vc-room')));
  await p.click('#vc-join'); await p.waitForTimeout(1000);
  ok('Videocall-Fallback ohne Absturz', (await p.textContent('#vc-status')).length>0 && await p.locator('#page-app').evaluate(e=>e.classList.contains('active')));
  await p.click('#grp-close'); await p.waitForTimeout(120);
  ok('keine JS-Fehler', p.__errs.length===0);
  await p.context().close(); }

/* ---------- Persona 4: Skeptiker Sami ---------- */
console.log('\n🕵️ Skeptiker Sami — Datenschutz, Spende, nicht-kommerziell');
{ const p=await newP();
  await p.locator('#page-landing .btn').first().click();
  await p.fill('#login-email','mara@matchquest.app');await p.fill('#login-pw','wm2026');await p.click('#form-login button[type=submit]');await p.waitForTimeout(120);
  await consent(p);
  await p.click('.tabbar button[data-view=profile]'); await p.waitForTimeout(150);
  for(const d of ['imprint','privacy','rules']){ await p.locator('#view-profile [data-doc="'+d+'"]').click(); await p.waitForTimeout(80);
    const t=await p.textContent('#doc-content'); ok('Doc '+d+' hat Inhalt', t.length>40); await p.click('#doc-close'); }
  ok('Profil sagt nicht-kommerziell', (await p.locator('.donate-card').innerText()).toLowerCase().includes('nicht-kommerziell'));
  await p.locator('[data-donate="1"]').click(); await p.waitForTimeout(80);
  ok('Spende öffnet Berliner Tafel', (await p.evaluate(()=>window.__open)||'').includes('berliner-tafel'));
  await p.click('#donate-chip'); await p.waitForTimeout(60);
  ok('Chip sagt Berliner Tafel', (await p.textContent('#donate-chip')).includes('Berliner Tafel'));
  ok('keine JS-Fehler', p.__errs.length===0);
  await p.context().close(); }

/* ---------- Persona 5: KI-Fan Kim (Guardrails) ---------- */
console.log('\n🤖 KI-Fan Kim — KI-Modus & Guardrails (jugendfrei)');
{ const p=await newP();
  await p.locator('#page-landing .btn').first().click();
  await p.fill('#login-email','lena@matchquest.app');await p.fill('#login-pw','wm2026');await p.click('#form-login button[type=submit]');await p.waitForTimeout(120);
  await consent(p);
  const guard=await p.evaluate(()=>{ const bad=['schlag','nackt','gewalt','droge','waffe','sex']; let allOk=true,samples=[];
    for(let i=0;i<300;i++){ const t=window.MQC.kiTask(); samples.push(t); if(!window.MQC.ok(t))allOk=false; const low=t.toLowerCase(); if(bad.some(w=>low.includes(w)))allOk=false; }
    return {allOk,uniq:[...new Set(samples)].length}; });
  ok('300 KI-Aufgaben alle jugendfrei/guardrail-ok', guard.allOk);
  ok('KI erzeugt Variation', guard.uniq>5);
  // KI mode affects group tasks
  await p.click('#freeplay-btn'); await p.waitForTimeout(150); await p.check('#ki-toggle');
  await p.click('#grp-start'); await p.waitForTimeout(200);
  ok('Gruppen-Aufgabe vorhanden', (await p.textContent('#grp-task')).length>3);
  await p.click('#grp-close'); await p.waitForTimeout(100);
  ok('keine JS-Fehler', p.__errs.length===0);
  await p.context().close(); }

/* ---------- Persona 6: Rückkehrer Rudi (Persistenz) ---------- */
console.log('\n🔁 Rückkehrer Rudi — Session, Reload, Persistenz');
{ const p=await newP();
  await p.locator('#page-landing .btn').first().click();
  await p.click('#tab-register'); await p.fill('#reg-email','rudi@test.de');await p.fill('#reg-pw','abcd');await p.fill('#reg-pw2','abcd');
  await p.click('#form-register button[type=submit]'); await p.waitForTimeout(120); await consent(p);
  await p.evaluate(()=>window.MQ.DB.addResult(window.MQ.Auth.current().id,{points:50,xp:30,coins:10,correctBet:true}));
  await p.reload(); await p.waitForTimeout(300);
  ok('Nach Reload eingeloggt (Session)', await p.locator('#page-app').evaluate(e=>e.classList.contains('active')));
  ok('Einwilligung nicht erneut', !(await p.locator('#consent').evaluate(e=>e.classList.contains('show'))));
  ok('Punkte persistent', (await p.evaluate(()=>window.MQ.Auth.current().points))>=50);
  // logout -> landing -> wrong login
  await p.click('.tabbar button[data-view=profile]'); await p.click('#logout'); await p.waitForTimeout(150);
  ok('Logout -> Landing', await p.locator('#page-landing').evaluate(e=>e.classList.contains('active')));
  await p.locator('#page-landing .btn').first().click();
  await p.fill('#login-email','rudi@test.de');await p.fill('#login-pw','falsch');await p.click('#form-login button[type=submit]');await p.waitForTimeout(100);
  ok('Falsches Passwort -> Fehler', (await p.textContent('#login-error')).length>0);
  await p.fill('#login-pw','abcd');await p.click('#form-login button[type=submit]');await p.waitForTimeout(150);
  ok('Richtiges Login -> App (kein erneuter Consent)', await p.locator('#page-app').evaluate(e=>e.classList.contains('active')));
  ok('keine JS-Fehler', p.__errs.length===0);
  await p.context().close(); }

console.log('\n===== ERGEBNIS: '+pass+' PASS / '+fail+' FAIL =====');
if(fails.length) console.log('FEHLGESCHLAGEN:\n - '+fails.join('\n - '));
await b.close();
process.exit(fail?1:0);
