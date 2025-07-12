"""
Rule-based intent classifier
----------------------------
Phase-1 logic:
  • claim          – any CPT codes present
  • preauth        – keyword match in clinical.notes
  • referral       – keyword match in clinical.notes
  • adjudication   – payer-originated intake with codes
"""

import re
from typing import Optional

from models.gcim import GCIM


# ──────────────────────────────────────────────────────────────────────────────
# Keyword patterns (case-insensitive)
# ──────────────────────────────────────────────────────────────────────────────
_PREAUTH_RE   = re.compile(r"\b(prior[- ]?auth(oriz|or)|pre[- ]?auth)\b", re.I)
_REFERRAL_RE  = re.compile(r"\b(referral|refer\s+to)\b", re.I)


# ──────────────────────────────────────────────────────────────────────────────
# Main API
# ──────────────────────────────────────────────────────────────────────────────
def detect_intent(gcim: GCIM) -> Optional[str]:
    """Return 'claim' | 'preauth' | 'referral' | 'adjudication' | None."""
    notes = (gcim.clinical.notes or "") if gcim.clinical else ""

    # 1) Claim if CPT codes exist
    if gcim.clinical and gcim.clinical.cpt_codes:
        return "claim"

    # 2) Pre-Authorization
    if _PREAUTH_RE.search(notes):
        return "preauth"

    # 3) Referral
    if _REFERRAL_RE.search(notes):
        return "referral"

    # 4) Payer adjudication intake
    if gcim.meta and gcim.meta.source_type == "payer" and gcim.clinical and gcim.clinical.icd_codes:
        return "adjudication"

    # Nothing matched
    return None
