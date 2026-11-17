# ดึงข้อมูลตู้ขาเข้าจาก SVMS portal API แล้วใส่ลงใน index.html (ระหว่าง PORTAL_DATA)
# ใช้: python refresh_portal_data.py   (ต้องมีชุด API ที่ C:\Users\HAL-USER\SinokorAPI\Thailand_HEUNG-A)
import sys, json, re, datetime, pathlib
sys.path.insert(0, r"C:\Users\HAL-USER\SinokorAPI\Thailand_HEUNG-A")
from ovs_more import client

PORTS = ["THLCH", "THBKK"]
HERE = pathlib.Path(__file__).parent
HTML = HERE / "dashboard.html"      # หน้าจริงบนเครื่อง (มีข้อมูล ไม่ถูก push)
PUBLIC_HTML = HERE / "index.html"   # หน้าเข้ารหัสสำหรับ GitHub Pages (push ได้)
PW_FILE = HERE / "dashboard.pw"     # รหัสผ่านที่เข้ารหัสด้วยบัญชี Windows (ไม่ถูก push)


def d(s):
    s = (s or "").strip()
    return f"{s[:4]}-{s[4:6]}-{s[6:8]}" if len(s) == 8 and s.isdigit() else ""


def n(v):
    try:
        return round(float(str(v).replace(",", "")))
    except (TypeError, ValueError):
        return None


def main():
    api = client()
    rows = []
    for port in PORTS:
        for r in api.call("import not pickup", {"P_NA_CD": "TH", "P_PORT_CD": port}):
            rows.append({
                "k": "P", "bl": r["BLNO"], "c": r["CNTRNO"], "t": r["TPSZ"], "pod": r["POD"],
                "v": f'{r.get("VSLCD") or ""} {r.get("VYG") or ""}'.strip(),
                "cn": r.get("CONSIGNEE") or "", "loc": r.get("LOCNM") or "",
                "mv": r.get("MVCD") or "", "arr": d(r.get("EQ_DATE")), "out": "",
                "free": n(r.get("FREE DAY")), "over": n(r.get("OVER DAY")), "stay": n(r.get("STAYING")),
                "amt": n(r.get("DEMAMT")), "cur": r.get("CUR") or "THB",
                "inv": n(r.get("INVAMT")), "stl": n(r.get("STLAMT")), "rcv": n(r.get("RCVAMT")),
                "tar": r.get("TARIFF_REF") or "", "msg": (r.get("MESSAGE") or "").strip(),
            })
        for r in api.call("import not return", {"P_NA_CD": "TH", "P_PORT_CD": port}):
            rows.append({
                "k": "R", "bl": r["BLNO"], "c": r["CNTRNO"], "t": r["TPSZ"], "pod": r["POD"],
                "v": f'{r.get("VSLCD") or ""} {r.get("VYG") or ""}'.strip(),
                "cn": r.get("CONSIGNEE") or "", "loc": r.get("LOCNM") or "",
                "mv": r.get("LASTMV") or "", "arr": d(r.get("BFRDT")), "out": d(r.get("LASTDT")),
                "free": n(r.get("FREEDAY")), "over": n(r.get("OVER")), "stay": n(r.get("STAYING")),
                "amt": n(r.get("DETENTION")), "cur": r.get("CUR") or "THB",
                "tar": r.get("TARIFF_REF") or "", "msg": (r.get("MESSAGE") or "").strip(),
            })
    # รายตู้ครบทุกตู้ของแต่ละ B/L จาก bl info (ตู้ที่รับ/คืนแล้วไม่อยู่ในรายงาน not pickup / not return)
    bls = {}
    failed = []
    all_bl = sorted({r["bl"] for r in rows})
    for i, bl in enumerate(all_bl, 1):
        try:
            data = api.call("bl info", {"P_BL_NO": bl}, raw=True)["data"]
        except Exception as e:  # ไม่มีสิทธิ์ / ล้มเหลว -> ใช้เฉพาะตู้ในรายงาน
            failed.append(bl)
            continue
        hdr = (data.get("R_HEADER") or [{}])[0]
        conts = {}
        for r in data.get("R_DEMDETTOS") or []:
            if r.get("LD") == "D" and r.get("CNTRNO") and r["CNTRNO"] != "Total":
                conts[r["CNTRNO"]] = {
                    "c": r["CNTRNO"], "t": r.get("TPSZ") or "", "pt": r.get("PORT") or "",
                    "fd": r.get("FREEDAY") or "",
                    "m1": d(r.get("MV1_DATE")), "m2": d(r.get("MV2_DATE")), "m3": d(r.get("MV3_DATE")),
                    "da": n(r.get("DEMAMT")), "ta": n(r.get("DETAMT")),
                }
        for r in data.get("R_CONTAINER") or []:
            c = r.get("HCCNTNO")
            if c and c not in conts:
                conts[c] = {"c": c, "t": r.get("HCTYPE") or "", "pt": "", "fd": "", "m1": "", "m2": "", "m3": "", "da": None, "ta": None}
            elif c and not conts[c]["t"]:
                conts[c]["t"] = r.get("HCTYPE") or ""
        one = lambda v: " ".join(str(v or "").split())  # ตัดบรรทัดใหม่/ช่องว่างซ้ำ
        bls[bl] = {"do": d(hdr.get("HHDODT")), "eta": d(hdr.get("HHETA")), "ata": d(hdr.get("HHAAD")),
                   "cnee": one(hdr.get("HHC1")), "vn": one(hdr.get("HHVSLNM")), "vc": one(hdr.get("HHVSLCD")),
                   "vy": one(hdr.get("HHVYG")), "pol": one(hdr.get("HHLODCD")), "poln": one(hdr.get("HHLODNM")),
                   "pod": one(hdr.get("HHDISCCD")), "podn": one(hdr.get("HHDISCNM")),
                   "k": list(conts.values())}
        if i % 50 == 0:
            print(f"bl info {i}/{len(all_bl)}", flush=True)
    if failed:
        print("bl info ไม่สำเร็จ", len(failed), "B/L:", ", ".join(failed[:10]))
    payload = {"asof": datetime.date.today().isoformat(), "ports": PORTS, "rows": rows, "bls": bls}
    js = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = HTML.read_text(encoding="utf-8")
    html, k = re.subn(r"/\*PORTAL_DATA\*/.*?/\*END_PORTAL_DATA\*/",
                      lambda m: "/*PORTAL_DATA*/" + js + "/*END_PORTAL_DATA*/", html, flags=re.S)
    if k != 1:
        sys.exit("ไม่พบตำแหน่ง PORTAL_DATA ใน index.html")
    HTML.write_text(html, encoding="utf-8")
    print(f"{len(rows)} ตู้ ({sum(r['k']=='P' for r in rows)} ยังไม่รับ, {sum(r['k']=='R' for r in rows)} ยังไม่คืน)"
          f" จาก {len({r['bl'] for r in rows})} B/L ณ {payload['asof']}")


REPO_URL = "https://github.com/sa2530/Check-Dem"


def repo_is_private():
    """เช็กแบบไม่ล็อกอิน: repo Private จะตอบ 404 ถ้าเปิดได้ (200) แปลว่าสาธารณะ -> ห้าม push ข้อมูลลูกค้า"""
    import urllib.request, urllib.error
    try:
        urllib.request.urlopen(urllib.request.Request(REPO_URL, headers={"User-Agent": "heunga-dashboard"}), timeout=20)
        return False
    except urllib.error.HTTPError as e:
        return e.code == 404
    except Exception:
        return None  # เช็กไม่ได้ (ไม่มีเน็ต ฯลฯ)


def encrypt_public():
    """สร้าง index.html (เข้ารหัส) จาก dashboard.html ด้วยรหัสผ่านใน dashboard.pw คืน True ถ้าสำเร็จ"""
    import subprocess, os, shutil
    if not PW_FILE.exists():
        print("ข้ามเข้ารหัส: ยังไม่ได้ตั้งรหัสผ่าน (รัน set_dashboard_password.ps1)"); return False
    node = shutil.which("node") or r"C:\Program Files\nodejs\node.exe"
    ps_cmd = ("$s = (Get-Content -Raw -LiteralPath '" + str(PW_FILE) + "').Trim() | ConvertTo-SecureString; "
              "[Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($s))")
    ps = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=60)
    pw = ps.stdout.strip()
    if ps.returncode != 0 or len(pw) < 12:
        print("ข้ามเข้ารหัส: อ่านรหัสผ่านจาก dashboard.pw ไม่ได้"); return False
    r = subprocess.run([node, str(HERE / "encrypt_dashboard.js"), str(HTML), str(PUBLIC_HTML), datetime.date.today().isoformat()],
                       env=dict(os.environ, DASH_PW=pw), capture_output=True, text=True, timeout=120)
    print("เข้ารหัส:", (r.stdout or r.stderr).strip()[-200:], flush=True)
    return r.returncode == 0


def push_to_github():
    import subprocess, os
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    def git(*a):
        return subprocess.run(["git", *a], cwd=HERE, env=env, capture_output=True, text=True, timeout=120)
    if not (HERE / ".git").exists():
        print("ข้าม push: ไม่ใช่โฟลเดอร์ git"); return
    # ห้าม push หน้าที่ไม่ได้เข้ารหัสเด็ดขาด (มีชื่อลูกค้าและยอดเงินจริง)
    if not encrypt_public():
        print("ข้าม push: ยังไม่ได้เข้ารหัสหน้า index.html"); return
    txt = PUBLIC_HTML.read_text(encoding="utf-8")
    if "ENCRYPTED_DASHBOARD" not in txt or "PORTAL_DATA" in txt or '"rows":' in txt or '"bls":' in txt:
        print("ข้าม push: index.html ดูเหมือนไม่ได้เข้ารหัส"); return
    try:
        git("add", "index.html")
        if git("diff", "--cached", "--quiet").returncode == 0:
            print("push: ไม่มีข้อมูลเปลี่ยน"); return
        c = git("commit", "-q", "-m", "Daily data refresh " + datetime.date.today().isoformat())
        p = git("push", "origin", "main")
        print("push:", "สำเร็จ" if p.returncode == 0 else "ล้มเหลว " + (p.stderr or c.stderr).strip()[-300:], flush=True)
    except Exception as e:
        print("push ล้มเหลว:", e, flush=True)


if __name__ == "__main__":
    if sys.stdout is None or sys.stderr is None:  # pythonw (Task Scheduler): เขียน log แทนหน้าจอ
        log = open(HERE / "refresh.log", "a", encoding="utf-8", buffering=1)
        sys.stdout = sys.stderr = log
    print("=== เริ่ม", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    try:
        main()
        print("=== สำเร็จ", datetime.datetime.now().strftime("%H:%M:%S"), flush=True)
        push_to_github()  # ไม่ทำให้งานล้มเหลวถ้า push ไม่ผ่าน (ข้อมูลบนเครื่องอัปเดตแล้ว)
    except SystemExit:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("=== ล้มเหลว (ข้อมูลเดิมยังอยู่ ไม่ถูกเขียนทับ):", e, flush=True)
        sys.exit(1)
