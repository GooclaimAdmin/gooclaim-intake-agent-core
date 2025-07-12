from models.gcim import GCIM, Patient, Clinical
from validator import validate_gcim

def test_validator_happy_path():
    gcim = GCIM(
        patient=Patient(id="123"),
        provider=None,
        payer=None,
        visit=None,
        clinical=Clinical(icd_codes=["A00.1"]),
        insurance=None,
        meta=None,
        intent="claim",
    )
    ok, errs = validate_gcim(gcim)
    assert ok and not errs

def test_validator_errors():
    gcim = GCIM(
        patient=Patient(id=""),
        provider=None,
        payer=None,
        visit=None,
        clinical=Clinical(icd_codes=[], cpt_codes=[]),
        insurance=None,
        meta=None,
        intent=None,
    )
    ok, errs = validate_gcim(gcim)
    assert not ok
    assert "patient.id is required" in errs
