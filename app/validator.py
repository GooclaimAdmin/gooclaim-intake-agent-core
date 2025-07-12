"""
GCIM Validator
==============

Basic Phase-1 validation rules:
• Required Patient.id
• At least one of {clinical.icd_codes, clinical.cpt_codes}
• CPT format  : 5 digits (e.g. "99213")
• ICD-10 format: 1 letter + 2-6 alphanumerics, optional '.' after 3rd char
• Visit.date cannot be in the future
"""

import re
from datetime import date, datetime
from typing import List, Tuple

from models.gcim import GCIM

# Pre-compiled regex patterns
_CPT_RE  = re.compile(r"^\d{5}$")
_ICD_RE  = re.compile(r"^[A-TV-Z][0-9A-Z]{2}(?:\.[0-9A-Z]{1,4})?$")  # Simple ICD-10

# ---------------------------------------------------------------------------

def validate_gcim(gcim: GCIM) -> Tuple[bool, List[str]]:
    """
    Validate a GCIM instance.
    Returns (is_valid, [error strings])
    """
    errors: List[str] = []

    # ── Patient ────────────────────────────────────────────────────────────
    if not gcim.patient or not gcim.patient.id:
        errors.append("patient.id is required")

    # ── Clinical codes ─────────────────────────────────────────────────────
    icds = gcim.clinical.icd_codes if gcim.clinical else []
    cpts = gcim.clinical.cpt_codes if gcim.clinical else []

    if not icds and not cpts:
        errors.append("at least one ICD or CPT code is required")

    for code in icds:
        if code and not _ICD_RE.match(code):
            errors.append(f"invalid ICD-10 code: {code}")

    for code in cpts:
        if code and not _CPT_RE.match(code):
            errors.append(f"invalid CPT code: {code}")

    # ── Visit date sanity ──────────────────────────────────────────────────
    if gcim.visit and gcim.visit.date:
        if gcim.visit.date > date.today():
            errors.append("visit.date cannot be in the future")

    # ── Return result ──────────────────────────────────────────────────────
    return len(errors) == 0, errors
