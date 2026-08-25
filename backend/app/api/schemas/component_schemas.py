from pydantic import BaseModel, ConfigDict
from typing import Optional
from decimal import Decimal


class ComponentBase(BaseModel):
    #Shared fields for all components.
    model_config = ConfigDict(from_attributes=True)

    id: int
    brand: str
    model: str
    name: str
    price: Decimal
    image_url: Optional[str] = None


class CPUResponse(ComponentBase):
    socket: str
    cores: int
    threads: int
    base_clock_mhz: int
    boost_clock_mhz: int
    tdp: int
    l3_cache_mb: Optional[int] = None
    supports_ddr4: bool = False
    supports_ddr5: bool = False
    integrated_graphics: Optional[str] = None
    benchmark_score: int = 0


class GPUResponse(ComponentBase):
    chip_manufacturer: str
    gpu_chip: Optional[str] = None
    vram_gb: int
    vram_type: str
    base_clock_mhz: int
    boost_clock_mhz: int
    memory_bus_width: Optional[int] = None
    length_mm: int
    tdp: int
    recommended_psu_wattage: int
    benchmark_score: int = 0


class MotherboardResponse(ComponentBase):
    socket: str
    chipset: str
    form_factor: str
    ddr_generation: str
    ram_slots: int
    max_ram_speed_mhz: int
    max_ram_capacity_gb: int
    m2_slots: int = 1
    sata_ports: int = 4
    has_wifi: bool = False
    has_bluetooth: bool = False


class RAMResponse(ComponentBase):
    ddr_generation: str
    speed_mhz: int
    total_capacity_gb: int
    modules: int
    capacity_per_module_gb: int
    cas_latency: Optional[int] = None
    voltage: Optional[float] = None


class PSUResponse(ComponentBase):
    wattage: int
    efficiency_rating: str
    modular_type: str
    form_factor: str
    pcie_8pin_connectors: int = 0
    has_12vhpwr: bool = False
    num_12vhpwr: int = 0


class CaseResponse(ComponentBase):
    case_type: str
    max_gpu_length_mm: int
    max_cpu_cooler_height_mm: int
    drive_bays_35: int = 2
    drive_bays_25: int = 2
    height_mm: Optional[int] = None
    width_mm: Optional[int] = None
    length_mm: Optional[int] = None
    has_tempered_glass: bool = False
    front_io_usb_c: bool = False
    psu_form_factor: str


class StorageResponse(ComponentBase):
    storage_type: str
    form_factor: str
    interface: str
    capacity_gb: int
    read_speed_mbps: Optional[int] = None
    write_speed_mbps: Optional[int] = None
    nand_type: Optional[str] = None
    tbw: Optional[int] = None
