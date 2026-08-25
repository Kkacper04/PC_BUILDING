
#API v1 — Component listing endpoints.
#Each endpoint returns a filtered list of components from the database.

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.base import get_db
from app.models.components import CPU, GPU, Motherboard, RAM, PSU, Case, Storage
from app.api.schemas.component_schemas import (
    CPUResponse, GPUResponse, MotherboardResponse, RAMResponse,
    PSUResponse, CaseResponse, StorageResponse,
)

router = APIRouter(tags=["Components"])


# CPU 
@router.get("/cpus", response_model=list[CPUResponse])
def list_cpus(
    brand: Optional[str] = Query(None, description="Filter by brand (e.g. AMD, Intel)"),
    socket: Optional[str] = Query(None, description="Filter by socket (e.g. AM5, LGA1700)"),
    db: Session = Depends(get_db),
):
    query = db.query(CPU)
    if brand:
        query = query.filter(CPU.brand.ilike(f"%{brand}%"))
    if socket:
        query = query.filter(CPU.socket == socket)
    return query.all()


# GPU
@router.get("/gpus", response_model=list[GPUResponse])
def list_gpus(
    brand: Optional[str] = Query(None),
    min_vram: Optional[int] = Query(None, description="Minimum VRAM in GB"),
    db: Session = Depends(get_db),
):
    query = db.query(GPU)
    if brand:
        query = query.filter(GPU.brand.ilike(f"%{brand}%"))
    if min_vram:
        query = query.filter(GPU.vram_gb >= min_vram)
    return query.all()


# Motherboard 
@router.get("/motherboards", response_model=list[MotherboardResponse])
def list_motherboards(
    socket: Optional[str] = Query(None),
    form_factor: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Motherboard)
    if socket:
        query = query.filter(Motherboard.socket == socket)
    if form_factor:
        query = query.filter(Motherboard.form_factor == form_factor)
    return query.all()


# RAM 
@router.get("/ram", response_model=list[RAMResponse])
def list_ram(
    ddr: Optional[str] = Query(None, description="DDR4 or DDR5"),
    db: Session = Depends(get_db),
):
    query = db.query(RAM)
    if ddr:
        query = query.filter(RAM.ddr_generation == ddr)
    return query.all()


# PSU
@router.get("/psus", response_model=list[PSUResponse])
def list_psus(
    min_wattage: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(PSU)
    if min_wattage:
        query = query.filter(PSU.wattage >= min_wattage)
    return query.all()


# Case 
@router.get("/cases", response_model=list[CaseResponse])
def list_cases(
    db: Session = Depends(get_db),
):
    return db.query(Case).all()


# Storage (SSD/HDD)
@router.get("/storage", response_model=list[StorageResponse])
def list_storage(
    min_capacity: Optional[int] = Query(None, description="Minimum capacity in GB"),
    db: Session = Depends(get_db),
):
    query = db.query(Storage)
    if min_capacity:
        query = query.filter(Storage.capacity_gb >= min_capacity)
    return query.all()
