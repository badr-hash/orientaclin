"""
MCP Server — Clinical Tools
Provides ICD-10 hints and care pathway suggestions via HTTP.
This is a simplified MCP-compatible server for the academic project.
"""
import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Clinical MCP Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load ICD-10 data from local JSON
DATA_DIR = Path(__file__).parent / "data"


def load_icd10_data() -> dict:
    path = DATA_DIR / "icd10_hints.json"
    if path.exists():
        return json.loads(path.read_text())
    return {}


def load_care_pathways() -> dict:
    path = DATA_DIR / "care_pathways.json"
    if path.exists():
        return json.loads(path.read_text())
    return {}


# ── Schemas ───────────────────────────────────────────────────────────────────

class ICD10Request(BaseModel):
    symptom: str


class CarePathwayRequest(BaseModel):
    summary: str


# ── Tool endpoints ────────────────────────────────────────────────────────────

@app.post("/tools/get_icd10_hint")
def get_icd10_hint(req: ICD10Request):
    """Returns a plausible ICD-10 code hint for a given symptom keyword."""
    icd10_data = load_icd10_data()
    symptom_lower = req.symptom.lower()

    for keyword, code in icd10_data.items():
        if keyword in symptom_lower:
            return {"icd10_code": code, "symptom": req.symptom, "matched_keyword": keyword}

    return {"icd10_code": "Z00.0 — Examen médical général", "symptom": req.symptom, "matched_keyword": None}


@app.post("/tools/suggest_care_pathway")
def suggest_care_pathway(req: CarePathwayRequest):
    """Suggests a care pathway based on clinical summary keywords."""
    pathways = load_care_pathways()
    summary_lower = req.summary.lower()

    for keyword, pathway in pathways.items():
        if keyword in summary_lower:
            return {"pathway": pathway, "matched_keyword": keyword}

    return {
        "pathway": "Médecine générale — Consultation de premier recours recommandée",
        "matched_keyword": None
    }


@app.get("/tools")
def list_tools():
    """Lists available MCP tools."""
    return {
        "tools": [
            {
                "name": "get_icd10_hint",
                "description": "Returns a plausible ICD-10 code hint for a symptom",
                "input_schema": {"symptom": "string"}
            },
            {
                "name": "suggest_care_pathway",
                "description": "Suggests a care pathway based on clinical summary",
                "input_schema": {"summary": "string"}
            }
        ]
    }


@app.get("/health")
def health():
    return {"status": "ok", "service": "Clinical MCP Server"}


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8001, reload=True)
