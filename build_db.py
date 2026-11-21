import sqlite3
import pandas as pd
import qrcode
from pathlib import Path

DATA_DIR = Path("data")
DB_PATH = "ehr.db"

# 1. Load CSVs into SQLite tables
conn = sqlite3.connect(DB_PATH)
tables = ["patients", "conditions", "medications", "observations", "encounters"]

for table in tables:
    df = pd.read_csv(DATA_DIR / f"{table}.csv")
    df.to_sql(table, conn, if_exists="replace", index=False)
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_pid ON {table}(patient_id)")
    print(f"Loaded {len(df)} rows into '{table}'")

conn.close()
print(f"\nDatabase saved to {DB_PATH}")

# 2. Generate QR codes containing ONLY the patient_id
qr_dir = Path("qr_codes")
qr_dir.mkdir(exist_ok=True)

demo_patients = ["FHIR-00001", "FHIR-00004", "FHIR-00006", "FHIR-00010"]
for pid in demo_patients:
    img = qrcode.make(pid)
    img.save(qr_dir / f"{pid}.png")
    print(f"Saved QR code: qr_codes/{pid}.png")