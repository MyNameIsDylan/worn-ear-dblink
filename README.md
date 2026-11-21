# Clinical Smart Glasses FHIR Backend

Hands-free FHIR R4 clinical backend for smart glasses. Scans patient QR codes to surface critical alerts, cross-checks OTC/Rx medication barcodes via openFDA, and appends timestamped clinician voice notes.

## Live API (Render)
* **Interactive Docs:** https://worn-ear-dblink.onrender.com/docs
* **Sample Patient Record:** https://worn-ear-dblink.onrender.com/patient/FHIR-00001
* **OTC Barcode Check (Advil vs. CKD):** https://worn-ear-dblink.onrender.com/patient/FHIR-00001/check-med/305730164207

## Repo Contents
* `main.py` — FastAPI server (FHIR endpoints, openFDA barcode lookup, voice notes)
* `build_db.py` / `ehr.db` — Synthetic FHIR R4 ingestion script and SQLite database
* `make_qr.py` / `qr_codes/` — Patient QR code generator and scannable demo codes
  
