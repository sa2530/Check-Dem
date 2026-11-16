// เข้ารหัส Dashboard ด้วยรหัสผ่าน (PBKDF2-SHA256 600,000 รอบ + AES-256-GCM) เพื่อเผยแพร่บน GitHub Pages
// ใช้: node encrypt_dashboard.js <dashboard.html> <index.html> [asof]    รหัสผ่านอ่านจาก env DASH_PW เท่านั้น
// ผลลัพธ์เป็นหน้ากรอกรหัสผ่าน ข้อมูลจริงอยู่ในรูปข้อความเข้ารหัส ถอดรหัสในเบราว์เซอร์ผู้เปิดเท่านั้น
const fs = require('fs'), crypto = require('crypto');
const [, , inp, out, asof] = process.argv;
const pw = process.env.DASH_PW || '';
if (!inp || !out) { console.error('usage: node encrypt_dashboard.js in.html out.html [asof]'); process.exit(2); }
if (pw.length < 12) { console.error('DASH_PW ต้องมีอย่างน้อย 12 ตัวอักษร'); process.exit(2); }

const ITER = 600000;
const salt = crypto.randomBytes(16), iv = crypto.randomBytes(12);
const key = crypto.pbkdf2Sync(pw, salt, ITER, 32, 'sha256');
const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
const enc = Buffer.concat([cipher.update(fs.readFileSync(inp)), cipher.final()]);
const data = Buffer.concat([enc, cipher.getAuthTag()]).toString('base64'); // WebCrypto: ciphertext || tag

const html = `<!DOCTYPE html>
<!--ENCRYPTED_DASHBOARD-->
<html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>Dashboard ค่าตู้ขาเข้า HEUNG A</title>
<style>
:root{color-scheme:light dark}
body{margin:0;min-height:100vh;display:grid;place-items:center;font:16px system-ui,'Noto Sans Thai','Segoe UI',sans-serif;background:linear-gradient(180deg,#e3f6fb,#a6dbe9);color:#13203a}
@media (prefers-color-scheme:dark){body{background:linear-gradient(180deg,#08222f,#0b3b52);color:#e8eefb}}
form{width:min(92vw,360px);background:rgba(255,255,255,.92);color:#13203a;border-radius:16px;padding:24px;box-shadow:0 8px 30px rgba(0,0,0,.18);display:grid;gap:12px}
h1{font-size:20px;margin:0}
p{margin:0;font-size:13px;color:#56657f}
input{font:inherit;padding:10px 12px;border:1.5px solid #c5d2e6;border-radius:10px;min-height:44px}
button{font:inherit;font-weight:600;padding:10px;border:0;border-radius:999px;background:#0f2547;color:#fff;min-height:44px;cursor:pointer}
button:disabled{opacity:.6}
#err{color:#d3263f;font-size:14px;min-height:1.2em}
</style></head><body>
<form id="f" autocomplete="off">
<h1>Dashboard ค่าตู้ขาเข้า HEUNG A</h1>
<p>ข้อมูลถูกเข้ารหัส ใส่รหัสผ่านเพื่อดูข้อมูล${asof ? ' · ข้อมูล ณ ' + asof : ''}</p>
<input id="pw" type="password" placeholder="รหัสผ่าน" required autofocus>
<button id="b" type="submit">เปิดดู</button>
<div id="err" role="alert"></div>
</form>
<script>
var S="${salt.toString('base64')}",I="${iv.toString('base64')}",N=${ITER},D="${data}";
var b64=function(s){return Uint8Array.from(atob(s),function(c){return c.charCodeAt(0)})};
document.getElementById('f').addEventListener('submit',async function(e){
  e.preventDefault();
  var btn=document.getElementById('b'),err=document.getElementById('err');
  err.textContent='';btn.disabled=true;btn.textContent='กำลังถอดรหัส…';
  try{
    if(!(window.crypto&&crypto.subtle)) throw new Error('nosubtle');
    var km=await crypto.subtle.importKey('raw',new TextEncoder().encode(document.getElementById('pw').value),'PBKDF2',false,['deriveKey']);
    var key=await crypto.subtle.deriveKey({name:'PBKDF2',salt:b64(S),iterations:N,hash:'SHA-256'},km,{name:'AES-GCM',length:256},false,['decrypt']);
    var buf=await crypto.subtle.decrypt({name:'AES-GCM',iv:b64(I)},key,b64(D));
    var page=new TextDecoder().decode(buf);
    document.open();document.write(page);document.close();
  }catch(x){
    err.textContent=(x&&x.message==='nosubtle')?'เบราว์เซอร์นี้ถอดรหัสไม่ได้ (ต้องเปิดผ่าน https)':'รหัสผ่านไม่ถูกต้อง';
    btn.disabled=false;btn.textContent='เปิดดู';
  }
});
</script></body></html>`;
fs.writeFileSync(out, html);
console.log('encrypted ->', out, (html.length / 1024).toFixed(0) + ' KB');
