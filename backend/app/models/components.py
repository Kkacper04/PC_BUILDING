
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Table,
    Text,
    Column,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base
from app.models.enums import (
    ChipsetFamily,
    CoolerType,
    DDRGeneration,
    EfficiencyRating,
    FormFactor,
    ModularType,
    PSUFormFactor,
    SocketType,
    StorageFormFactor,
    StorageInterface,
    StorageType,
    VRAMType,
)



cooler_socket_compatibility = Table(
    "cooler_socket_compatibility",
    Base.metadata,
    Column("cooler_id", Integer, ForeignKey("cpu_coolers.id", ondelete="CASCADE"), primary_key=True),
    Column("socket", Enum(SocketType), primary_key=True),
)
#Which sockets a CPU cooler's mounting kit supports.


case_form_factor_support = Table(
    "case_form_factor_support",
    Base.metadata,
    Column("case_id", Integer, ForeignKey("cases.id", ondelete="CASCADE"), primary_key=True),
    Column("form_factor", Enum(FormFactor), primary_key=True),
)
#Which motherboard form factors physically fit inside a case.


chipset_socket_map = Table(
    "chipset_socket_map",
    Base.metadata,
    Column("chipset", Enum(ChipsetFamily), primary_key=True),
    Column("socket", Enum(SocketType), primary_key=True),
)


class _ComponentMixin:
   
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    brand: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    model: Mapped[str] = mapped_column(String(200), nullable=False)
    name: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
        index=True,
        comment="Marketing / display name, e.g. 'ASUS ROG STRIX Z790-E'",
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Current retail price in PLN",
    )
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    release_year: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )



class CPU(_ComponentMixin, Base):

    __tablename__ = "cpus"
    __table_args__ = (
        CheckConstraint("cores > 0", name="ck_cpu_cores_positive"),
        CheckConstraint("threads >= cores", name="ck_cpu_threads_gte_cores"),
        CheckConstraint("tdp > 0", name="ck_cpu_tdp_positive"),
        Index("ix_cpus_socket_brand", "socket", "brand"),
    )

   
    socket: Mapped[Optional[SocketType]] = mapped_column(Enum(SocketType), nullable=True, index=True)
    chipset_family: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Comma-separated compatible chipsets, e.g. 'Z790,B760,H770'",
    )

    
    cores: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    threads: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    base_clock_mhz: Mapped[int] = mapped_column(Integer, nullable=False, comment="Base clock in MHz")
    boost_clock_mhz: Mapped[int] = mapped_column(Integer, nullable=False, comment="Max boost clock in MHz")
    l3_cache_mb: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True, comment="L3 cache in MB")

   
    tdp: Mapped[int] = mapped_column(Integer, nullable=False, comment="Thermal Design Power in watts")
    max_turbo_power: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="PBP / MTP – maximum power draw under all-core turbo (watts)",
    )

    
    supports_ddr4: Mapped[bool] = mapped_column(Boolean, default=False)
    supports_ddr5: Mapped[bool] = mapped_column(Boolean, default=False)
    max_memory_speed_mhz: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Max officially supported memory speed in MHz",
    )
    max_memory_capacity_gb: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Maximum supported RAM capacity in GB",
    )

   
    integrated_graphics: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="iGPU model name, NULL if absent",
    )
    pcie_gen: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Highest PCIe generation, e.g. '5.0'",
    )
    pcie_lanes: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    unlocked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="True if multiplier-unlocked (K/KF for Intel, all Ryzen)",
    )

   
    benchmark_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Synthetic multi-thread benchmark score (higher is better)",
    )
    benchmark_single_core: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Single-thread benchmark score (higher is better)",
    )

   
    builds: Mapped[List["Build"]] = relationship(back_populates="cpu")

    def __repr__(self) -> str:
        socket_str = self.socket.value if self.socket else "Unknown Socket"
        return f"<CPU {self.brand} {self.model} ({socket_str})>"




class Motherboard(_ComponentMixin, Base):

    __tablename__ = "motherboards"
    __table_args__ = (
        CheckConstraint("ram_slots > 0", name="ck_mb_ram_slots_positive"),
        Index("ix_motherboards_socket_chipset", "socket", "chipset"),
    )

   
    socket: Mapped[Optional[SocketType]] = mapped_column(Enum(SocketType), nullable=True, index=True)
    chipset: Mapped[Optional[ChipsetFamily]] = mapped_column(Enum(ChipsetFamily), nullable=True, index=True)
    form_factor: Mapped[Optional[FormFactor]] = mapped_column(Enum(FormFactor), nullable=True, index=True)

   
    ddr_generation: Mapped[DDRGeneration] = mapped_column(Enum(DDRGeneration), nullable=False)
    ram_slots: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=4)
    max_ram_speed_mhz: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Max supported memory speed in MHz (with XMP/EXPO)",
    )
    max_ram_capacity_gb: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=128,
        comment="Total maximum RAM capacity in GB",
    )

    
    pcie_x16_slots: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    pcie_x4_slots: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    pcie_x1_slots: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    pcie_gen: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Highest PCIe generation for GPU slot",
    )

    
    m2_slots: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    m2_pcie_gen: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Highest PCIe gen for M.2, e.g. '5.0'",
    )
    sata_ports: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=4)

   
    usb_type_a_ports: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=4)
    usb_type_c_ports: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    has_wifi: Mapped[bool] = mapped_column(Boolean, default=False)
    has_bluetooth: Mapped[bool] = mapped_column(Boolean, default=False)
    audio_codec: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ethernet_speed_gbps: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="e.g. '2.5', '10'",
    )

   
    cpu_power_phases: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    eps_power_connectors: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=1,
        comment="Number of 8-pin EPS CPU power connectors",
    )

    
    builds: Mapped[List["Build"]] = relationship(back_populates="motherboard")

    def __repr__(self) -> str:
        socket_str = self.socket.value if self.socket else "Unknown"
        ff_str = self.form_factor.value if self.form_factor else "Unknown"
        return f"<Motherboard {self.brand} {self.model} ({socket_str} / {ff_str})>"



class RAM(_ComponentMixin, Base):

    __tablename__ = "ram"
    __table_args__ = (
        CheckConstraint("modules > 0", name="ck_ram_modules_positive"),
        CheckConstraint("capacity_per_module_gb > 0", name="ck_ram_cap_positive"),
        Index("ix_ram_ddr_speed", "ddr_generation", "speed_mhz"),
    )

    ddr_generation: Mapped[DDRGeneration] = mapped_column(Enum(DDRGeneration), nullable=False, index=True)
    speed_mhz: Mapped[int] = mapped_column(Integer, nullable=False, comment="e.g. 3200, 6000")
    capacity_per_module_gb: Mapped[int] = mapped_column(Integer, nullable=False, comment="Per-stick capacity")
    modules: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment="Number of sticks in the kit")
    total_capacity_gb: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="modules × capacity_per_module_gb (denormalised for query convenience)",
    )
    cas_latency: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True, comment="CAS Latency (CL)")
    voltage: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 3), nullable=True, comment="Operating voltage, e.g. 1.350")
    module_height_mm: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Physical height including heatspreader (mm) — tall RAM can conflict with air coolers",
    )
    is_ecc: Mapped[bool] = mapped_column(Boolean, default=False)
    has_rgb: Mapped[bool] = mapped_column(Boolean, default=False)

   
    benchmark_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

   
    builds: Mapped[List["Build"]] = relationship(back_populates="ram")

    def __repr__(self) -> str:
        return f"<RAM {self.brand} {self.model} {self.total_capacity_gb}GB {self.ddr_generation.value}-{self.speed_mhz}>"



class GPU(_ComponentMixin, Base):
   

    __tablename__ = "gpus"
    __table_args__ = (
        CheckConstraint("tdp > 0", name="ck_gpu_tdp_positive"),
        CheckConstraint("length_mm > 0", name="ck_gpu_length_positive"),
    )

    chip_manufacturer: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Chip designer: NVIDIA, AMD, or Intel",
    )
    gpu_chip: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="GPU chip codename, e.g. 'AD102', 'Navi 31'",
    )

    
    vram_gb: Mapped[int] = mapped_column(Integer, nullable=False)
    vram_type: Mapped[VRAMType] = mapped_column(Enum(VRAMType), nullable=False)
    base_clock_mhz: Mapped[int] = mapped_column(Integer, nullable=False)
    boost_clock_mhz: Mapped[int] = mapped_column(Integer, nullable=False)
    memory_bus_width: Mapped[Optional[int]] = mapped_column(
        SmallInteger,
        nullable=True,
        comment="Memory bus width in bits, e.g. 256",
    )
    cuda_cores: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="CUDA / Stream / Xe cores")
    ray_tracing_cores: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

   
    length_mm: Mapped[int] = mapped_column(Integer, nullable=False, comment="Total card length in mm")
    width_slots: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 1),
        nullable=True,
        comment="Slot width, e.g. 2.0, 2.5, 3.0, 3.5",
    )
    height_mm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="Card height in mm")

    
    tdp: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="Total board power in watts")
    recommended_psu_wattage: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Manufacturer-recommended PSU wattage",
    )
    pcie_power_8pin: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=0,
        comment="Number of 8-pin (6+2) PCIe power connectors required",
    )
    pcie_power_12vhpwr: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=0,
        comment="Number of 12VHPWR / 12V-2x6 connectors required",
    )

   
    pcie_gen: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    pcie_lanes: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=16)

    
    hdmi_ports: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    displayport_ports: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=3)

   
    benchmark_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="3D benchmark score (higher is better)",
    )

   
    builds: Mapped[List["Build"]] = relationship(back_populates="gpu")

    def __repr__(self) -> str:
        return f"<GPU {self.brand} {self.model} ({self.vram_gb}GB)>"



class Case(_ComponentMixin, Base):
    __tablename__ = "cases"

    case_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="e.g. Full Tower, Mid Tower, Mini Tower, SFF",
    )

   
    max_gpu_length_mm: Mapped[int] = mapped_column(Integer, nullable=False)
    max_cpu_cooler_height_mm: Mapped[int] = mapped_column(Integer, nullable=False)
    max_psu_length_mm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

   
    drive_bays_35: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=2)
    drive_bays_25: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=2)

    included_fans: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    max_fan_slots: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=6)
    max_radiator_mm: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Largest radiator supported, e.g. 360",
    )
    front_radiator_support_mm: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Comma-separated, e.g. '120,240,360'",
    )
    top_radiator_support_mm: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Comma-separated, e.g. '120,240'",
    )

    length_mm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="Depth")
    width_mm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height_mm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    weight_kg: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)

    has_tempered_glass: Mapped[bool] = mapped_column(Boolean, default=False)
    front_io_usb_c: Mapped[bool] = mapped_column(Boolean, default=False, comment="Front panel USB-C header")
    psu_form_factor: Mapped[PSUFormFactor] = mapped_column(
        Enum(PSUFormFactor),
        nullable=False,
        default=PSUFormFactor.ATX,
        comment="PSU size supported",
    )

   
    builds: Mapped[List["Build"]] = relationship(back_populates="case")

    def __repr__(self) -> str:
        return f"<Case {self.brand} {self.model} ({self.case_type})>"




class PSU(_ComponentMixin, Base):

    __tablename__ = "psus"
    __table_args__ = (
        CheckConstraint("wattage > 0", name="ck_psu_wattage_positive"),
    )

    wattage: Mapped[int] = mapped_column(Integer, nullable=False, comment="Rated continuous output in watts")
    efficiency_rating: Mapped[EfficiencyRating] = mapped_column(Enum(EfficiencyRating), nullable=False)
    modular_type: Mapped[ModularType] = mapped_column(Enum(ModularType), nullable=False)
    form_factor: Mapped[PSUFormFactor] = mapped_column(
        Enum(PSUFormFactor),
        nullable=False,
        default=PSUFormFactor.ATX,
    )


    eps_8pin_connectors: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=1,
        comment="8-pin EPS (CPU power) connectors",
    )
    pcie_8pin_connectors: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=0,
        comment="8-pin (6+2) PCIe connectors",
    )
    pcie_6pin_connectors: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=0,
    )
    has_12vhpwr: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="Native 12VHPWR / 12V-2x6 connector",
    )
    num_12vhpwr: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=0,
        comment="Number of 12VHPWR connectors",
    )
    sata_connectors: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=6)
    molex_connectors: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=2)
    has_24pin_atx: Mapped[bool] = mapped_column(Boolean, default=True)

   
    depth_mm: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="PSU depth in mm — must fit case PSU bay",
    )
    fan_size_mm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_fanless: Mapped[bool] = mapped_column(Boolean, default=False)

    builds: Mapped[List["Build"]] = relationship(back_populates="psu")

    def __repr__(self) -> str:
        return f"<PSU {self.brand} {self.model} ({self.wattage}W {self.efficiency_rating.value})>"



class CPUCooler(_ComponentMixin, Base):
   

    __tablename__ = "cpu_coolers"
    __table_args__ = (
        CheckConstraint("max_tdp > 0", name="ck_cooler_tdp_positive"),
    )

    cooler_type: Mapped[CoolerType] = mapped_column(Enum(CoolerType), nullable=False, index=True)

    
    height_mm: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Total height for tower coolers (mm). NULL for AIOs.",
    )
    radiator_size_mm: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Radiator length in mm (120, 240, 280, 360, 420). NULL for air coolers.",
    )
    radiator_thickness_mm: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Radiator thickness in mm",
    )
    fan_count: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    fan_size_mm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="Fan diameter, e.g. 120, 140")

    
    max_tdp: Mapped[int] = mapped_column(Integer, nullable=False, comment="Maximum rated TDP dissipation in watts")

    
    max_noise_dba: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
        comment="Maximum noise level in dB(A)",
    )
    max_fan_rpm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

   
    has_rgb: Mapped[bool] = mapped_column(Boolean, default=False)
    bearing_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="e.g. 'Fluid Dynamic', 'Ball Bearing'",
    )

   
    builds: Mapped[List["Build"]] = relationship(back_populates="cpu_cooler")

    def __repr__(self) -> str:
        return f"<CPUCooler {self.brand} {self.model} ({self.cooler_type.value})>"






class Storage(_ComponentMixin, Base):
    

    __tablename__ = "storage"
    __table_args__ = (
        CheckConstraint("capacity_gb > 0", name="ck_storage_capacity_positive"),
    )

    storage_type: Mapped[StorageType] = mapped_column(Enum(StorageType), nullable=False, index=True)
    form_factor: Mapped[StorageFormFactor] = mapped_column(Enum(StorageFormFactor), nullable=False)
    interface: Mapped[StorageInterface] = mapped_column(Enum(StorageInterface), nullable=False)

    capacity_gb: Mapped[int] = mapped_column(Integer, nullable=False)
    read_speed_mbps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    write_speed_mbps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    iops_random_read: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    iops_random_write: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    has_dram_cache: Mapped[bool] = mapped_column(Boolean, default=False)
    nand_type: Mapped[Optional[str]] = mapped_column(
        String(30),
        nullable=True,
        comment="e.g. 'TLC', 'QLC', 'MLC'",
    )
    tbw: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Total Bytes Written endurance rating (TB)",
    )
    rpm: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Rotational speed for HDDs, e.g. 7200. NULL for SSDs.",
    )
    power_watts: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True, comment="Active power draw")

    
    benchmark_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    def __repr__(self) -> str:
        return f"<Storage {self.brand} {self.model} ({self.capacity_gb}GB {self.storage_type.value})>"




class Build(Base):


    __tablename__ = "builds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, default="Untitled Build")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

   
    cpu_id: Mapped[Optional[int]] = mapped_column(ForeignKey("cpus.id", ondelete="SET NULL"), nullable=True)
    motherboard_id: Mapped[Optional[int]] = mapped_column(ForeignKey("motherboards.id", ondelete="SET NULL"), nullable=True)
    ram_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ram.id", ondelete="SET NULL"), nullable=True)
    gpu_id: Mapped[Optional[int]] = mapped_column(ForeignKey("gpus.id", ondelete="SET NULL"), nullable=True)
    case_id: Mapped[Optional[int]] = mapped_column(ForeignKey("cases.id", ondelete="SET NULL"), nullable=True)
    psu_id: Mapped[Optional[int]] = mapped_column(ForeignKey("psus.id", ondelete="SET NULL"), nullable=True)
    cpu_cooler_id: Mapped[Optional[int]] = mapped_column(ForeignKey("cpu_coolers.id", ondelete="SET NULL"), nullable=True)

   
    total_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Cached total build price",
    )
    total_tdp: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Cached total TDP in watts",
    )
    is_compatible: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
        comment="Cached result of last compatibility check",
    )

    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

   
    cpu: Mapped[Optional["CPU"]] = relationship(back_populates="builds", lazy="joined")
    motherboard: Mapped[Optional["Motherboard"]] = relationship(back_populates="builds", lazy="joined")
    ram: Mapped[Optional["RAM"]] = relationship(back_populates="builds", lazy="joined")
    gpu: Mapped[Optional["GPU"]] = relationship(back_populates="builds", lazy="joined")
    case: Mapped[Optional["Case"]] = relationship(back_populates="builds", lazy="joined")
    psu: Mapped[Optional["PSU"]] = relationship(back_populates="builds", lazy="joined")
    cpu_cooler: Mapped[Optional["CPUCooler"]] = relationship(back_populates="builds", lazy="joined")
    storage_items: Mapped[List["BuildStorage"]] = relationship(
        back_populates="build",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Build #{self.id} '{self.name}'>"


class BuildStorage(Base):
   

    __tablename__ = "build_storage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    build_id: Mapped[int] = mapped_column(
        ForeignKey("builds.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    storage_id: Mapped[int] = mapped_column(
        ForeignKey("storage.id", ondelete="CASCADE"),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)

    
    build: Mapped["Build"] = relationship(back_populates="storage_items")
    storage: Mapped["Storage"] = relationship()

    def __repr__(self) -> str:
        return f"<BuildStorage build={self.build_id} storage={self.storage_id} qty={self.quantity}>"
