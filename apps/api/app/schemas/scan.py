from pydantic import BaseModel, Field
from typing import List


class PreviewResponse(BaseModel):
    scan_id: str
    skin_type_ar: str
    confidence: float
    confidence_pct: int
    attributes_ar: List[str]
    preview_ar: dict
    locked: bool
    unlock_options: dict
    disclaimer_ar: str
    latency_ms: int


class Answers(BaseModel):
    tzone_shiny: bool
    irritates_easily: bool


class FullRequest(BaseModel):
    scan_id: str
    answers: Answers
    unlock_via: str = Field(default="paid")


class FullResponse(BaseModel):
    scan_id: str
    skin_type_ar: str
    confidence: float
    confidence_pct: int
    attributes_ar: List[str]
    full_report_ar: dict
    unlocked_via: str
    disclaimer_ar: str
    latency_ms: int
