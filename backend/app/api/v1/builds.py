
#API v1 — Build validation and AI endpoints.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.components import CPU, GPU, Motherboard, RAM, PSU, Case, CPUCooler
from app.logic.compatibility import CompatibilityChecker
from app.ai.ssd_recommender import recommend_best_disc
from app.api.schemas.build_schemas import (
    BuildValidationRequest, CompatibilityReport, BottleneckRequest,
)

router = APIRouter(tags=["Builds"])


def _get_or_404(db: Session, model, obj_id: int, label: str):
    obj = db.query(model).get(obj_id)
    if not obj:
        raise HTTPException(status_code=404, detail=f"{label} with id={obj_id} not found.")
    return obj


# Build Validation 
@router.post("/build/validate", response_model=CompatibilityReport)
def validate_build(
    req: BuildValidationRequest,
    db: Session = Depends(get_db),
):
    cpu = _get_or_404(db, CPU, req.cpu_id, "CPU")
    mobo = _get_or_404(db, Motherboard, req.motherboard_id, "Motherboard")
    ram = _get_or_404(db, RAM, req.ram_id, "RAM")
    gpu = _get_or_404(db, GPU, req.gpu_id, "GPU")
    case = _get_or_404(db, Case, req.case_id, "Case")
    psu = _get_or_404(db, PSU, req.psu_id, "PSU")

    cooler = None
    if req.cooler_id:
        cooler = _get_or_404(db, CPUCooler, req.cooler_id, "CPU Cooler")

    checker = CompatibilityChecker()
    result = checker.validate_build(cpu, mobo, ram, gpu, case, psu, cooler)

    return CompatibilityReport(**result)


# SSD Recommendation 
@router.get("/build/recommend-ssd")
def recommend_ssd(db: Session = Depends(get_db)):
    return recommend_best_disc(db)
