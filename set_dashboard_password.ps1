# ตั้งรหัสผ่านสำหรับเข้ารหัส Dashboard บน GitHub Pages
# รหัสถูกเก็บเป็นไฟล์ dashboard.pw ที่เข้ารหัสด้วยบัญชี Windows ของคุณ (DPAPI) เปิดอ่านได้เฉพาะบัญชีนี้บนเครื่องนี้
# ไฟล์นี้ไม่ถูก push ขึ้น GitHub (อยู่ใน .gitignore) และรหัสไม่ปรากฏบนหน้าจอ
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "ตั้งรหัสผ่านเปิดดู Dashboard (อย่างน้อย 12 ตัวอักษร แนะนำผสมตัวอักษร ตัวเลข และสัญลักษณ์)"
$p1 = Read-Host "รหัสผ่านใหม่" -AsSecureString
$p2 = Read-Host "พิมพ์ซ้ำอีกครั้ง" -AsSecureString
$a = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($p1))
$b = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($p2))
if ($a -ne $b) { Write-Host "รหัสทั้งสองครั้งไม่ตรงกัน ลองใหม่" -ForegroundColor Red; exit 1 }
if ($a.Length -lt 12) { Write-Host "สั้นเกินไป ต้องอย่างน้อย 12 ตัวอักษร" -ForegroundColor Red; exit 1 }
$p1 | ConvertFrom-SecureString | Set-Content -Path (Join-Path $here "dashboard.pw") -Encoding ascii
Write-Host "บันทึกรหัสผ่านแล้ว (dashboard.pw) จดรหัสไว้เอง เพราะดูย้อนหลังไม่ได้" -ForegroundColor Green
