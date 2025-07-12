"""
Epic FHIR ➜ GCIM v1 parser
--------------------------------------------------
• Accepts a FHIR Bundle (Python dict)
• Extracts Patient, Encounter, Condition, Procedure, Coverage
• Returns a GCIM (Gooclaim Common Intake Model) object
"""

from datetime import datetime
from typing import List, Dict, Any, Optional

from models.gcim import (
    GCIM,
    Patient,
    Provider,
    Visit,
    Clinical,
    Insurance,
    Meta,
)


# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────

def _resources(bundle: Dict[str, Any], resource_type: str) -> List[Dict[str, Any]]:
    """Return all resources in bundle matching resource_type."""
    return [
        e["resource"]
        for e in bundle.get("entry", [])
        if e.get("resource", {}).get("resourceType") == resource_type
    ]


def _first(bundle: Dict[str, Any], resource_type: str) -> Dict[str, Any]:
    """Return first matching resource or {}."""
    items = _resources(bundle, resource_type)
    return items[0] if items else {}


def _human_name(name_field: Optional[List[dict]]) -> Optional[str]:
    """
    Convert FHIR HumanName list → 'First Last'
    """
    if not name_field:
        return None
    given = " ".join(name_field[0].get("given", []))
    family = name_field[0].get("family", "")
    full = f"{given} {family}".strip()
    return full or None


def _get_date(date_str: Optional[str]):
    """
    Accept 'YYYY-MM-DD' or ISO string → datetime.date (or None)
    """
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str).date()
    except ValueError:
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Field-level parsers
# ──────────────────────────────────────────────────────────────────────────────

def _parse_patient(bundle: Dict[str, Any]) -> Patient:
    pat = _first(bundle, "Patient")
    return Patient(
        id=pat.get("id"),
        name=_human_name(pat.get("name")),
        dob=_get_date(pat.get("birthDate")),
        gender=pat.get("gender"),
    )


def _parse_provider(bundle: Dict[str, Any]) -> Provider:
    enc = _first(bundle, "Encounter")
    participant = (enc.get("participant") or [{}])[0]
    ref = participant.get("individual", {}).get("reference")  # e.g. Practitioner/123
    npi = ref.split("/")[-1] if ref else None
    return Provider(npi=npi, name=None, location=None)


def _parse_visit(bundle: Dict[str, Any]) -> Visit:
    enc = _first(bundle, "Encounter")
    period = enc.get("period", {})
    return Visit(
        date=_get_date(period.get("start")),
        encounter_type=enc.get("type", [{}])[0].get("text"),
        reason=(enc.get("reasonCode") or [{}])[0].get("text"),
    )


def _parse_clinical(bundle: Dict[str, Any]) -> Clinical:
    icd = [
        c.get("code", {}).get("coding", [{}])[0].get("code")
        for c in _resources(bundle, "Condition")
    ]
    cpt = [
        p.get("code", {}).get("coding", [{}])[0].get("code")
        for p in _resources(bundle, "Procedure")
    ]
    notes = "; ".join(
        filter(
            None,
            [
                c.get("code", {}).get("text")
                for c in _resources(bundle, "Condition")
            ],
        )
    )
    return Clinical(icd_codes=icd, cpt_codes=cpt, notes=notes or None)


def _parse_insurance(bundle: Dict[str, Any]) -> Insurance:
    cov = _first(bundle, "Coverage")
    return Insurance(
        policy_number=cov.get("subscriberId"),
        group_number=cov.get("grouping", {}).get("group"),
        coverage_start=_get_date(cov.get("period", {}).get("start")),
        coverage_end=_get_date(cov.get("period", {}).get("end")),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Public entry point
# ──────────────────────────────────────────────────────────────────────────────

def parse_fhir_bundle(bundle: Dict[str, Any]) -> GCIM:
    """
    Convert an Epic FHIR Bundle (dict) → GCIM object
    """
    patient   = _parse_patient(bundle)
    provider  = _parse_provider(bundle)
    visit     = _parse_visit(bundle)
    clinical  = _parse_clinical(bundle)
    insurance = _parse_insurance(bundle)

    meta = Meta(
        source_ehr="Epic",
        source_type="provider",
        ingested_at=datetime.utcnow(),
        confidence_score=None,
    )

    intent = "claim" if clinical.cpt_codes else None

    return GCIM(
        patient=patient,
        provider=provider,
        payer=None,
        visit=visit,
        clinical=clinical,
        insurance=insurance,
        meta=meta,
        intent=intent,
    )
