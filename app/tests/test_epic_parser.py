import json
from app.parser_epic import parse_fhir_bundle

def test_epic_sample_bundle():
    with open("tests/epic_sample_bundle.json") as f:
        bundle = json.load(f)
    gcim = parse_fhir_bundle(bundle)

    assert gcim.patient.id
    assert gcim.intent == "claim"
    assert "Z00" in gcim.clinical.icd_codes or gcim.clinical.icd_codes
