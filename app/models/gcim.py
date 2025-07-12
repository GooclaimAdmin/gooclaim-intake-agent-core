from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime


class Patient(BaseModel):
    id: str
    name: Optional[str]
    dob: Optional[date]
    gender: Optional[str]


class Provider(BaseModel):
    npi: Optional[str]
    name: Optional[str]
    location: Optional[str]


class Payer(BaseModel):
    payer_id: Optional[str]
    name: Optional[str]
    plan_name: Optional[str]
    eligibility_status: Optional[str]


class Visit(BaseModel):
    date: Optional[date]
    encounter_type: Optional[str]
    reason: Optional[str]


class Clinical(BaseModel):
    icd_codes: List[str] = Field(default_factory=list)
    cpt_codes: List[str] = Field(default_factory=list)
    notes: Optional[str]


class Insurance(BaseModel):
    policy_number: Optional[str]
    group_number: Optional[str]
    coverage_start: Optional[date]
    coverage_end: Optional[date]


class Meta(BaseModel):
    source_ehr: Optional[str]
    source_type: Optional[str]  # e.g., 'provider' or 'payer'
    ingested_at: datetime = Field(default_factory=datetime.utcnow)
    confidence_score: Optional[float]


class GCIM(BaseModel):
    patient: Patient
    provider: Optional[Provider]
    payer: Optional[Payer]
    visit: Optional[Visit]
    clinical: Optional[Clinical]
    insurance: Optional[Insurance]
    meta: Optional[Meta]
    intent: Optional[str]  # e.g., 'claim', 'preauth', 'referral', 'adjudication'
