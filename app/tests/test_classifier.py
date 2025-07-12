from models.gcim import GCIM, Patient, Clinical, Meta
from classifier import detect_intent


def test_claim_intent():
    gcim = GCIM(
        patient=Patient(id="1"),
        provider=None,
        payer=None,
        visit=None,
        clinical=Clinical(cpt_codes=["99213"]),
        insurance=None,
        meta=None,
        intent=None,
    )
    assert detect_intent(gcim) == "claim"


def test_preauth_intent():
    gcim = GCIM(
        patient=Patient(id="1"),
        provider=None,
        payer=None,
        visit=None,
        clinical=Clinical(notes="Need prior auth for MRI"),
        insurance=None,
        meta=None,
        intent=None,
    )
    assert detect_intent(gcim) == "preauth"


def test_referral_intent():
    gcim = GCIM(
        patient=Patient(id="1"),
        provider=None,
        payer=None,
        visit=None,
        clinical=Clinical(notes="Patient given referral to cardiology"),
        insurance=None,
        meta=None,
        intent=None,
    )
    assert detect_intent(gcim) == "referral"


def test_adjudication_intent():
    gcim = GCIM(
        patient=Patient(id="1"),
        provider=None,
        payer=None,
        visit=None,
        clinical=Clinical(icd_codes=["A00"]),
        insurance=None,
        meta=Meta(source_ehr="PayerSys", source_type="payer"),
        intent=None,
    )
    assert detect_intent(gcim) == "adjudication"
