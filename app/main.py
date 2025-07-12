"""
FastAPI Intake Service (Phase-1)
────────────────────────────────
POST /intake
Headers: Content-Type: application/json
Query params:
  • source_ehr   – "Epic" (default)
  • content_type – "FHIR" (default)
Body:
  • Raw message (FHIR Bundle for Epic phase-1)
Response 200: { "gcim": { … } }
Response 422: { "errors": [ … ] }
"""

from fastapi import FastAPI, Query, Body, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any

from models.gcim import GCIM
from parser_registry import get_parser
from validator import validate_gcim
from classifier import detect_intent

app = FastAPI(
    title="Gooclaim Intake Agent — Phase 1",
    version="0.1.0",
    description="Parses Epic FHIR -> GCIM, validates, classifies."
)

# ────────────────────────────────────────────────────────────────────────────
# Routes
# ────────────────────────────────────────────────────────────────────────────

@app.post("/intake")
async def intake_endpoint(
    body: Dict[str, Any] = Body(..., description="Raw EHR payload (FHIR bundle for Epic)"),
    source_ehr: str = Query("Epic", description="EHR source, e.g., Epic"),
    content_type: str = Query("FHIR", description="Payload format, e.g., FHIR / HL7 / JSON"),
):
    """
    Main intake endpoint:
    1. Parse raw payload → GCIM
    2. Validate GCIM
    3. Classify intent
    4. Return GCIM JSON (or errors)
    """
    # 1️⃣   Parse
    try:
        parser = get_parser(source_ehr, content_type)
    except KeyError:
        raise HTTPException(status_code=400, detail=f"No parser for ({source_ehr}, {content_type})")

    try:
        gcim: GCIM = parser(body)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Parser error: {exc}")

    # 2️⃣   Validate
    is_valid, errors = validate_gcim(gcim)
    if not is_valid:
        return JSONResponse(status_code=422, content={"errors": errors})

    # 3️⃣   Classify
    gcim.intent = detect_intent(gcim)

    # 4️⃣   Return
    return {"gcim": gcim.dict()}


@app.get("/healthz")
async def healthcheck():
    return {"status": "ok"}
