import qrcode
from pathlib import Path

# Paste your VS Code forwarded URL here (NO trailing slash at the end)
BASE_URL = "https://worn-ear-dblink.onrender.com"

qr_dir = Path("qr_codes")
qr_dir.mkdir(exist_ok=True)

demo_patients = ["FHIR-00001", "FHIR-00004", "FHIR-00006", "FHIR-00010"]

for pid in demo_patients:
    url = f"{BASE_URL}/patient/{pid}"
    img = qrcode.make(url)
    img.save(qr_dir / f"{pid}.png")
    print(f"Created QR for: {url}")