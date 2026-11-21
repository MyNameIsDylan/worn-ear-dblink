import os
import json
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai

load_dotenv()
app = FastAPI(title="Worn Clinical EHR API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "ehr.db"
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY")) if os.getenv("GEMINI_API_KEY") else None


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def fetch_patient_record(patient_id: str) -> dict:
    conn = get_db()
    patient = conn.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,)).fetchone()
    if not patient:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")

    conditions = [
        dict(r) for r in conn.execute(
            "SELECT display, icd10_code, onset_date FROM conditions WHERE patient_id = ?", (patient_id,)
        ).fetchall()
    ]
    meds = [
        dict(r) for r in conn.execute(
            "SELECT medication, status, authored_on FROM medications WHERE patient_id = ? AND status = 'active'",
            (patient_id,),
        ).fetchall()
    ]
    # Latest value for each lab/vital measure
    obs_rows = conn.execute(
        """
        SELECT measure, value, unit, date
        FROM observations
        WHERE patient_id = ?
        ORDER BY date ASC
        """,
        (patient_id,),
    ).fetchall()
    conn.close()

    latest_obs = {}
    for r in obs_rows:
        latest_obs[r["measure"]] = {"value": r["value"], "unit": r["unit"], "date": r["date"]}

    # Build clinical alert flags for the glasses HUD
    alerts = []
    sys_bp = latest_obs.get("systolic_bp", {}).get("value")
    dia_bp = latest_obs.get("diastolic_bp", {}).get("value")
    a1c = latest_obs.get("hba1c_percent", {}).get("value")
    egfr = latest_obs.get("egfr", {}).get("value")

    if sys_bp and dia_bp and (sys_bp >= 140 or dia_bp >= 90):
        alerts.append(f"HIGH BP {int(sys_bp)}/{int(dia_bp)}")
    if a1c and a1c >= 8.0:
        alerts.append(f"HIGH A1c {a1c}%")
    if egfr and egfr < 60:
        alerts.append(f"LOW eGFR {int(egfr)}")

    p = dict(patient)
    return {
        "patient_id": patient_id,
        "glasses_hud": {
            "header": f"{patient_id} | {p['gender'][0].upper()}, {p['age_on_2026_06_30']}y",
            "alerts": alerts if alerts else ["Vitals Stable"],
            "bp": f"{int(sys_bp)}/{int(dia_bp)}" if (sys_bp and dia_bp) else "N/A",
            "a1c": f"{a1c}%" if a1c else "N/A",
            "conditions": [c["display"] for c in conditions[:3]],
            "meds": [m["medication"] for m in meds[:3]],
        },
        "phone_detail": {
            "demographics": p,
            "conditions": conditions,
            "active_medications": meds,
            "latest_observations": latest_obs,
        },
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/patients")
def list_demo_patients():
    """Returns first 10 patient IDs so teammates can see valid IDs."""
    conn = get_db()
    rows = conn.execute("SELECT patient_id, gender, age_on_2026_06_30 FROM patients LIMIT 10").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/patient/{patient_id}")
def get_patient(patient_id: str):
    return fetch_patient_record(patient_id)


class AskRequest(BaseModel):
    question: str


@app.post("/patient/{patient_id}/ask")
def ask_patient(patient_id: str, req: AskRequest):
    if not gemini_client:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not set")
    record = fetch_patient_record(patient_id)["phone_detail"]
    prompt = (
        "You are a hands-free clinical assistant on smart glasses. "
        "Answer in ONE short sentence (max 15 words) using ONLY this patient record:\n"
        f"{json.dumps(record)}\n\nQuestion: {req.question}"
    )
    resp = gemini_client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return {"patient_id": patient_id, "hud_answer": resp.text.strip()}