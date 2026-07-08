import pkg from '/opt/node22/lib/node_modules/playwright/index.js';
const { chromium } = pkg;
import { readFileSync, writeFileSync } from 'fs';
writeFileSync('/tmp/pro.html','<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>'+readFileSync('/home/user/python-esst-2504749/matchquest-app/matchquest-pro.html','utf8')+'</body></html>');
const API='http://127.0.0.1:8288/api.php';
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
let pass=0,fail=0; const F=[];
const ok=(n,c)=>{ if(c){pass++;console.log('  ✅',n);} else {fail++;F.push(n);console.log('  ❌',n);} };
async function device(email,name){ const ctx=await b.newContext({viewport:{width:430,height:920}});
  const p=await ctx.newPage(); await p.addInitScript((api)=>{localStorage.setItem('mqpro_backend',api);},API);
  await p.goto('file:///tmp/pro.html'); await p.locator('#page-landing .btn').first().click();
  await p.click('#tab-register'); await p.fill('#reg-name',name); await p.fill('#reg-email',email); await p.fill('#reg-pw','pw1234'); await p.fill('#reg-pw2','pw1234');
  await p.click('#form-register button[type=submit]'); await p.waitForTimeout(400);
  await p.check('#c1');await p.check('#c2');await p.check('#c3');await p.click('#consent-accept'); await p.waitForTimeout(200);
  return p; }

console.log('\n📱 Gerät A (Anna) & Gerät B (Ben) — echtes geteiltes Backend');
const A=await device('anna@x.de','Anna');
ok('A: im App (Server-Register)', await A.locator('#page-app').evaluate(e=>e.classList.contains('active')));
ok('A: Backend aktiv', await A.evaluate(()=>window.MQ.Net.enabled()));
await A.evaluate(()=>window.MQ.Net.submit({name:'Anna',points:120,xp:240,coins:50,correctBets:6,challengesDone:4,streak:2,teamId:'green',ach:[]}));
const B=await device('ben@x.de','Ben');
await B.evaluate(()=>window.MQ.Net.submit({name:'Ben',points:80,xp:180,coins:50,correctBets:9,challengesDone:3,streak:1,teamId:'blue',ach:[]}));
await B.waitForTimeout(200);

// A opens leaderboard -> sees BOTH (shared!)
await A.click('.tabbar button[data-view=rank]'); await A.waitForTimeout(500);
const lbA=await A.locator('#lb-card').innerText();
ok('A sieht sich UND Ben (geteiltes Leaderboard)', lbA.includes('Anna') && lbA.includes('Ben'));
ok('A: Ben vor Anna (mehr richtige Wetten)', lbA.indexOf('Ben')<lbA.indexOf('Anna'));

// A team battle from server
await A.click('#seg-teams'); await A.waitForTimeout(500);
const tA=await A.locator('#lb-card').innerText();
ok('A: Team-Battle zeigt Grün & Blau mit Punkten', /Team Grün/.test(tA) && /Team Blau/.test(tA) && /120/.test(tA) && /80/.test(tA));

// B sees the same shared board
await B.click('.tabbar button[data-view=rank]'); await B.waitForTimeout(500);
const lbB=await B.locator('#lb-card').innerText();
ok('B sieht ebenfalls beide Spieler', lbB.includes('Anna') && lbB.includes('Ben'));

// A joins Team Blau via UI -> server updates -> reflected
await A.click('#seg-teams'); await A.waitForTimeout(300);
const blueBtn=A.locator('#lb-card button', {hasText:'Team Blau'});
await blueBtn.first().click(); await A.waitForTimeout(600);
ok('A: Teamwechsel wird serverseitig gespeichert', (await A.evaluate(async()=>{const r=await window.MQ.Net.teams();const blue=r.teams.find(t=>t.id==='blue');return blue.members;}))>=2);

console.log('\n===== BACKEND-E2E: '+pass+' PASS / '+fail+' FAIL =====');
if(F.length)console.log(' - '+F.join('\n - '));
await b.close(); process.exit(fail?1:0);
