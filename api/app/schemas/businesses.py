from typing import Literal

from pydantic import BaseModel, Field


MedicalDomain = Literal[
    "DERMATOLOGY",
    "PLASTIC_SURGERY",
    "ORTHOPEDICS",
    "OPHTHALMOLOGY",
    "OTOLARYNGOLOGY",
]


class CreateBusinessRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    medical_domain: MedicalDomain
    location_name: str = Field(min_length=2, max_length=120)
    timezone: str = "Asia/Seoul"


class BusinessLocation(BaseModel):
    business_id: str
    location_id: str
    tenant_id: str
    name: str
    medical_domain: MedicalDomain
    location_name: str
    timezone: str
