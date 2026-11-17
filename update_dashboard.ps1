param([string]$Mode = "")
# ปุ่มอัปเดตเอง: ดึงข้อมูลจาก SVMS portal -> อัปเดต dashboard.html -> เข้ารหัสและ push ขึ้น GitHub Pages
# ใช้ Mode "noopen" เพื่อไม่เปิดเบราว์เซอร์และไม่รอกดปุ่ม (สำหรับทดสอบ)
$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here
$env:PYTHONIOENCODING = "utf-8"
$env:GIT_TERMINAL_PROMPT = "0"
$py = "C:\Users\HAL-USER\AppData\Local\Python\pythoncore-3.15-64\python.exe"
if (-not (Test-Path $py)) { $py = "python" }

Write-Host "=================================================="
Write-Host " อัปเดตข้อมูล Dashboard ค่าตู้ขาเข้า HEUNG A"
Write-Host " ดึงข้อมูลจาก SVMS portal ใช้เวลาราว 1-2 นาที"
Write-Host " อย่าปิดหน้าต่างนี้จนกว่าจะขึ้นว่าเสร็จ"
Write-Host "=================================================="
Write-Host ""
& $py (Join-Path $here "refresh_portal_data.py")
$rc = $LASTEXITCODE
Write-Host ""
if ($rc -eq 0) {
    Write-Host "[เสร็จแล้ว] ข้อมูลบนเครื่องอัปเดตแล้ว" -ForegroundColor Green
    Write-Host 'ดูบรรทัด "push:" ด้านบน ถ้าขึ้นว่าสำเร็จ แปลว่าส่งขึ้นเว็บแล้ว เว็บจะอัปเดตตามใน 1-2 นาที'
    if ($Mode -ne "noopen") { Start-Process (Join-Path $here "dashboard.html") }
} else {
    Write-Host "[ล้มเหลว] ดึงข้อมูลไม่สำเร็จ ข้อมูลเดิมยังอยู่ ดูสาเหตุในข้อความด้านบน" -ForegroundColor Red
}
if ($Mode -ne "noopen") { Write-Host ""; Read-Host "กด Enter เพื่อปิดหน้าต่าง" | Out-Null }
exit $rc
