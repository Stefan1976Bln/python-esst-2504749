import pkg from '/opt/node22/lib/node_modules/playwright/index.js';
const { chromium } = pkg;
import { readFileSync, writeFileSync } from 'fs';
writeFileSync('/tmp/pro.html','<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>'+readFileSync('/home/user/python-esst-2504749/matchquest-app/matchquest-pro.html','utf8')+'</body></html>');
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args:['--use-fake-device-for-media-stream','--use-fake-ui-for-media-stream']});
let pass=0,fail=0;const F=[];const ok=(n,c)=>{if(c){pass++;console.log('  ✅',n);}else{fail++;F.push(n);console.log('  ❌',n);}};
async function fresh(email){const ctx=await b.newContext({viewport:{width:430,height:920},permissions:['camera','microphone']});
  const p=await ctx.newPage();p.__e=[];p.on('pageerror',e=>p.__e.push(e.message));p.on('console',m=>{if(m.type()==='error'&&!/TUNNEL|ERR_/.test(m.text()))p.__e.push(m.text());});
  await p.goto('file:///tmp/pro.html');await p.locator('#page-landing .btn').first().click();
  await p.click('#tab-register');await p.fill('#reg-email',email);await p.fill('#reg-pw','test12');await p.fill('#reg-pw2','test12');
  await p.click('#form-register button[type=submit]');await p.waitForTimeout(150);
  await p.check('#c1');await p.check('#c2');await p.check('#c3');await p.click('#consent-accept');await p.waitForTimeout(150);
  return p;}
async function dismiss(p){try{if(await p.locator('#levelup.show').count()){await p.click('#lu-close');await p.waitForTimeout(80);}}catch(e){}}

for(let run=1;run<=3;run++){
  console.log('\n===== DURCHLAUF '+run+' =====');
  const p=await fresh('cam'+run+'_'+Date.now()+'@t.de');
  await p.click('#freeplay-btn');await p.waitForTimeout(250);

  // --- SOLO Live-Video-Challenge: bis Video-Challenge, dann Kamera starten ---
  let vid=false;
  for(let i=0;i<20 && !vid;i++){ if(await p.locator('#vid-card').isVisible()){vid=true;break;}
    await p.click('.tabbar button[data-view=matches]');await p.waitForTimeout(60);await p.click('#freeplay-btn');await p.waitForTimeout(150);}
  ok('Video-Challenge erreichbar', vid);
  if(vid){
    await p.click('#vid-start');await p.waitForTimeout(1200);
    const v=await p.evaluate(()=>{const el=document.getElementById('stage-video');return el?{shown:el.style.display!=='none',w:el.videoWidth,playing:!el.paused}:{none:true};});
    ok('Kamera läuft (echtes Video, Breite>0)', v.shown && v.w>0);
    ok('REC-Badge sichtbar', await p.locator('#rec-badge').isVisible());
    // Reaktionen antippen (dürfen nicht crashen)
    await p.locator('#reacts .rbtn').first().click().catch(()=>{});
  }

  // --- GRUPPE: bis wir Performer sind, Kamera starten ---
  await p.click('#grp-start');await p.waitForTimeout(200);
  let didPerform=false;
  for(let i=0;i<8 && !didPerform;i++){ await dismiss(p);
    if(await p.locator('#grp-cam').count()){ await p.click('#grp-cam');await p.waitForTimeout(1000);
      const gv=await p.evaluate(()=>{const el=document.getElementById('grp-video');return el?{w:el.videoWidth}:{none:true};});
      ok('Gruppe: Kamera aktiv beim Performer (Breite>0)', gv.w>0);
      if(await p.locator('#grp-done').count()){await p.click('#grp-done');await p.waitForTimeout(300);}
      didPerform=true;
    } else if(await p.locator('#grp-scorebtns .btn').count()){ await p.locator('#grp-scorebtns .btn').nth(6).click(); await p.waitForTimeout(150); }
    await dismiss(p); if(await p.locator('#grp-again').count()){await p.click('#grp-again');await p.waitForTimeout(150);}
  }
  ok('Gruppe: Performer-Kamerarunde absolviert', didPerform);
  ok('keine JS-Fehler', p.__e.length===0);
  if(p.__e.length)console.log('   Fehler:',p.__e.join(' | '));
  await p.context().close();
}
console.log('\n########## KAMERA-TEST: '+pass+' PASS / '+fail+' FAIL ##########');
if(F.length)console.log(' - '+[...new Set(F)].join('\n - '));
await b.close();process.exit(fail?1:0);
