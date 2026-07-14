/* Baut webapp/index.html aus matchquest-pro.html (Kopf + PWA-Meta + Auto-Backend + Service-Worker).
   Ausführen:  node build-webapp.js   */
const fs = require('fs');
const path = require('path');
const src = path.join(__dirname, 'matchquest-pro.html');
let body = fs.readFileSync(src, 'utf8').replace(/^<title>[\s\S]*?<\/title>\s*/, '');
const head = `<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>MatchQuest — Live-Fußball-Challenges</title>
<meta name="description" content="Interaktive Live-Challenges, Video-Duelle mit Freunden, XP und Ranglisten zu jedem Fußballspiel.">
<meta name="theme-color" content="#060913">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icons/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="MatchQuest">
<style>html,body{margin:0;padding:0;background:#060913;}</style>
</head>
<body>
<script>
/* Backend automatisch finden: gehostet (http/https, nicht claude.ai) -> ./api/api.php.
   So genügt EIN Ordner-Upload; ohne erreichbares Backend fällt die App automatisch auf Lokal-Modus zurück. */
(function(){try{
  if(location.protocol.indexOf('http')===0 && !/claude\\.ai/.test(location.host) && !localStorage.getItem('mqpro_backend')){
    localStorage.setItem('mqpro_backend', new URL('api/api.php', location.href).href);
  }
}catch(e){}})();
</script>
`;
const tail = `
<script>
if("serviceWorker" in navigator){window.addEventListener("load",function(){navigator.serviceWorker.register("service-worker.js").catch(function(){});});}
</script>
</body>
</html>
`;
fs.writeFileSync(path.join(__dirname, 'webapp', 'index.html'), head + body + tail);
console.log('webapp/index.html gebaut:', fs.statSync(path.join(__dirname, 'webapp', 'index.html')).size, 'bytes');
