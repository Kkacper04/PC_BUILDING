
#API v1 — Component listing endpoints.
#Each endpoint returns a filtered list of components from the database.

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.db.base import get_db
from app.models.components import CPU, GPU, Motherboard, RAM, PSU, Case, Storage, CPUCooler
from app.api.schemas.component_schemas import (
    CPUResponse, GPUResponse, MotherboardResponse, RAMResponse,
    PSUResponse, CaseResponse, StorageResponse, CPUCoolerResponse,
)

router = APIRouter(tags=["Components"])


def _get_or_404(db: Session, model, obj_id: int):
    obj = db.get(model, obj_id)
    if not obj:
        raise HTTPException(status_code=404, detail=f"{model.__name__} with id={obj_id} not found.")
    return obj


# CPU 
@router.get("/cpus", response_model=list[CPUResponse])
def list_cpus(
    brand: Optional[str] = Query(None, description="Filter by brand (e.g. AMD, Intel)"),
    socket: Optional[str] = Query(None, description="Filter by socket (e.g. AM5, LGA1700)"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(CPU)
    if brand:
        query = query.filter(CPU.brand.ilike(f"%{brand}%"))
    if socket:
        query = query.filter(CPU.socket == socket)
    return query.offset(offset).limit(limit).all()

@router.get("/cpus/{item_id}", response_model=CPUResponse)
def get_cpu(item_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, CPU, item_id)


# GPU
@router.get("/gpus", response_model=list[GPUResponse])
def list_gpus(
    brand: Optional[str] = Query(None),
    min_vram: Optional[int] = Query(None, description="Minimum VRAM in GB"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(GPU)
    if brand:
        query = query.filter(GPU.brand.ilike(f"%{brand}%"))
    if min_vram:
        query = query.filter(GPU.vram_gb >= min_vram)
    return query.offset(offset).limit(limit).all()

@router.get("/gpus/{item_id}", response_model=GPUResponse)
def get_gpu(item_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, GPU, item_id)


# Motherboard 
@router.get("/motherboards", response_model=list[MotherboardResponse])
def list_motherboards(
    socket: Optional[str] = Query(None),
    form_factor: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Motherboard)
    if socket:
        query = query.filter(Motherboard.socket == socket)
    if form_factor:
        query = query.filter(Motherboard.form_factor == form_factor)
    return query.offset(offset).limit(limit).all()

@router.get("/motherboards/{item_id}", response_model=MotherboardResponse)
def get_motherboard(item_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, Motherboard, item_id)


# RAM 
@router.get("/ram", response_model=list[RAMResponse])
def list_ram(
    ddr: Optional[str] = Query(None, description="DDR4 or DDR5"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(RAM)
    if ddr:
        query = query.filter(RAM.ddr_generation == ddr)
    return query.offset(offset).limit(limit).all()

@router.get("/ram/{item_id}", response_model=RAMResponse)
def get_ram(item_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, RAM, item_id)


# PSU
@router.get("/psus", response_model=list[PSUResponse])
def list_psus(
    min_wattage: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(PSU)
    if min_wattage:
        query = query.filter(PSU.wattage >= min_wattage)
    return query.offset(offset).limit(limit).all()

@router.get("/psus/{item_id}", response_model=PSUResponse)
def get_psu(item_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, PSU, item_id)


# Case 
@router.get("/cases", response_model=list[CaseResponse])
def list_cases(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return db.query(Case).offset(offset).limit(limit).all()

@router.get("/cases/{item_id}", response_model=CaseResponse)
def get_case(item_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, Case, item_id)


# Storage (SSD/HDD)
@router.get("/storage", response_model=list[StorageResponse])
def list_storage(
    min_capacity: Optional[int] = Query(None, description="Minimum capacity in GB"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Storage)
    if min_capacity:
        query = query.filter(Storage.capacity_gb >= min_capacity)
    return query.offset(offset).limit(limit).all()

@router.get("/storage/{item_id}", response_model=StorageResponse)
def get_storage(item_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, Storage, item_id)


# CPU Cooler
@router.get("/coolers", response_model=list[CPUCoolerResponse])
def list_coolers(
    cooler_type: Optional[str] = Query(None, description="Filter by type: air, aio_liquid"),
    min_tdp: Optional[int] = Query(None, description="Minimum TDP dissipation in watts"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(CPUCooler)
    if cooler_type:
        query = query.filter(CPUCooler.cooler_type == cooler_type)
    if min_tdp:
        query = query.filter(CPUCooler.max_tdp >= min_tdp)
    return query.offset(offset).limit(limit).all()

@router.get("/coolers/{item_id}", response_model=CPUCoolerResponse)
def get_cooler(item_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, CPUCooler, item_id)
