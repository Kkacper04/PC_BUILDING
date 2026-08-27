
#Pydantic schemas for build validation and AI endpoints.
from pydantic import BaseModel
from typing import Optional


class BuildValidationRequest(BaseModel):
    cpu_id: int
    motherboard_id: int
    ram_id: int
    gpu_id: Optional[int] = None  # Optional for APU/iGPU builds
    case_id: int
    psu_id: int
    cooler_id: Optional[int] = None


class CompatibilityReport(BaseModel):
    is_compatible: bool
    errors: list[str]
    warnings: list[str]


class SSDRecommendation(BaseModel):
    id: int
    name: str
    brand: str
    price: float
    capacity_gb: int
    read_speed_mbps: Optional[int] = None
    value_score: float
