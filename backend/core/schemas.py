from typing import Any, Literal
from pydantic import BaseModel, Field


class RunRequest(BaseModel):
    force: bool = True


class Issue(BaseModel):
    id: str
    parcel_id: str | None = None
    type: str
    severity: Literal['INFO', 'WARNING', 'CRITICAL']
    description: str
    sources: list[str] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)
    recommended_action: str = 'Verify source observation'
    confidence: float | None = None


class Parcel(BaseModel):
    parcel_id: str
    survey_number: str | None = None
    municipal_property_id: str | None = None
    revenue_record_id: str | None = None
    owner_name: str | None = None
    land_use: str | None = None
    recorded_area_sqm: float | None = None
    geometry: dict[str, Any]
    area_sqm: float
    perimeter_m: float
    metrics: dict[str, Any]
    source_ids: dict[str, str]
    source_count: int
    confidence: float
    overall_confidence: float
    status: Literal['MATCHED', 'REVIEW_REQUIRED', 'CONFLICT']
    topology: str
    conflicts: list[dict[str, Any]]
    changes: list[dict[str, Any]]
    explanation: list[str]
    recommendation: str
    auto_harmonized: bool
    review_required: bool
    metadata: dict[str, Any]
