"""
Enum types shared across all component models.

Centralised here to avoid circular imports and to give a single
source of truth for every constrained-choice column.
"""

import enum


# ---------------------------------------------------------------------------
# CPU / Motherboard
# ---------------------------------------------------------------------------

class SocketType(str, enum.Enum):
    """CPU / motherboard socket families."""

    # Intel
    LGA1700 = "LGA1700"
    LGA1851 = "LGA1851"
    LGA2066 = "LGA2066"

    # AMD
    AM4 = "AM4"
    AM5 = "AM5"
    sTRX4 = "sTRX4"
    sWRX8 = "sWRX8"
    TR5 = "TR5"


class ChipsetFamily(str, enum.Enum):
    """Motherboard chipset identifiers."""

    # Intel – 12th/13th/14th gen (LGA1700)
    Z690 = "Z690"
    Z790 = "Z790"
    B660 = "B660"
    B760 = "B760"
    H670 = "H670"
    H770 = "H770"
    H610 = "H610"

    # Intel – Arrow Lake (LGA1851)
    Z890 = "Z890"
    B860 = "B860"
    H810 = "H810"

    # AMD – Ryzen (AM4)
    X570 = "X570"
    B550 = "B550"
    A520 = "A520"

    # AMD – Ryzen 7000+ (AM5)
    X670E = "X670E"
    X670 = "X670"
    X870E = "X870E"
    X870 = "X870"
    B650E = "B650E"
    B650 = "B650"
    B850 = "B850"
    A620 = "A620"

    # AMD – Threadripper
    TRX40 = "TRX40"
    WRX80 = "WRX80"
    TRX50 = "TRX50"


# ---------------------------------------------------------------------------
# Memory
# ---------------------------------------------------------------------------

class DDRGeneration(str, enum.Enum):
    DDR4 = "DDR4"
    DDR5 = "DDR5"


# ---------------------------------------------------------------------------
# Form Factors
# ---------------------------------------------------------------------------

class FormFactor(str, enum.Enum):
    """Motherboard / case form-factors."""

    E_ATX = "E-ATX"
    ATX = "ATX"
    MICRO_ATX = "Micro-ATX"
    MINI_ITX = "Mini-ITX"


# ---------------------------------------------------------------------------
# GPU
# ---------------------------------------------------------------------------

class VRAMType(str, enum.Enum):
    GDDR5 = "GDDR5"
    GDDR5X = "GDDR5X"
    GDDR6 = "GDDR6"
    GDDR6X = "GDDR6X"
    GDDR7 = "GDDR7"


# ---------------------------------------------------------------------------
# PSU
# ---------------------------------------------------------------------------

class EfficiencyRating(str, enum.Enum):
    """80 PLUS efficiency tiers."""

    PLUS_80 = "80+"
    BRONZE = "80+ Bronze"
    SILVER = "80+ Silver"
    GOLD = "80+ Gold"
    PLATINUM = "80+ Platinum"
    TITANIUM = "80+ Titanium"


class ModularType(str, enum.Enum):
    NON_MODULAR = "Non-Modular"
    SEMI_MODULAR = "Semi-Modular"
    FULLY_MODULAR = "Fully Modular"


class PSUFormFactor(str, enum.Enum):
    ATX = "ATX"
    SFX = "SFX"
    SFX_L = "SFX-L"


# ---------------------------------------------------------------------------
# CPU Cooler
# ---------------------------------------------------------------------------

class CoolerType(str, enum.Enum):
    AIR = "Air"
    AIO_120 = "AIO 120mm"
    AIO_140 = "AIO 140mm"
    AIO_240 = "AIO 240mm"
    AIO_280 = "AIO 280mm"
    AIO_360 = "AIO 360mm"
    AIO_420 = "AIO 420mm"


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------

class StorageType(str, enum.Enum):
    NVME_SSD = "NVMe SSD"
    SATA_SSD = "SATA SSD"
    HDD = "HDD"


class StorageFormFactor(str, enum.Enum):
    M2_2280 = "M.2 2280"
    M2_2230 = "M.2 2230"
    INCH_2_5 = "2.5 inch"
    INCH_3_5 = "3.5 inch"


class StorageInterface(str, enum.Enum):
    PCIE_GEN3 = "PCIe Gen3"
    PCIE_GEN4 = "PCIe Gen4"
    PCIE_GEN5 = "PCIe Gen5"
    SATA3 = "SATA III"


class ComponentCategory(str, enum.Enum):
    CPU = "CPU"
    MOTHERBOARD = "Motherboard"
    RAM = "RAM"
    GPU = "GPU"
    CASE = "Case"
    PSU = "PSU"
    CPU_COOLER = "CPU Cooler"
    STORAGE = "Storage"
