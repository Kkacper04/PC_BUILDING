from dotenv import load_dotenv
load_dotenv()
import re
from decimal import Decimal
from sqlalchemy.orm import Session
import logging

from app.db.base import get_engine, Base
from app.models.components import Storage, CPU, Motherboard, GPU, RAM, PSU, Case
from app.models.enums import (
    StorageType, StorageFormFactor, StorageInterface, SocketType, 
    ChipsetFamily, FormFactor, DDRGeneration, VRAMType,
    PSUFormFactor, EfficiencyRating, ModularType
)

logger = logging.getLogger(__name__)

from typing import Any

def safe_parse_price(price_raw: Any, product_name: str) -> Decimal:
    if not price_raw:
        return Decimal("0.00")
    try:
        clean_str = str(price_raw).replace(" ", "").replace("zł", "").replace("PLN", "").replace(",", ".")
        return Decimal(clean_str)
    except Exception as e:
        logger.warning(f"Błąd parsowania ceny dla '{product_name}'. Otrzymano: '{price_raw}'. Ustawiam 0.00. Błąd: {e}")
        return Decimal("0.00")

def setup_database():
    print("[DB] Creating tables")
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    print("[DB] Tables ready.")

def save_disc_to_db(disc_list):
    engine = get_engine()
    with Session(engine) as session:
        saved = 0
        updated = 0
        
        for disc in disc_list:
            existing_ssd = session.query(Storage).filter(Storage.name == disc["name"]).first()
            
            if disc.get("form_factor") == "M.2":
                form_factor = StorageFormFactor.M2_2280
            else:
                form_factor = StorageFormFactor.INCH_2_5
           
            if form_factor == StorageFormFactor.M2_2280:
                storage_type = StorageType.NVME_SSD
                interface = StorageInterface.PCIE_GEN4
            else:
                storage_type = StorageType.SATA_SSD
                interface = StorageInterface.SATA3
                
            price = safe_parse_price(disc.get("price"), disc["name"])

            model_val = disc.get("model", "Unknown")
            if existing_ssd:
                existing_ssd.price = price
                if existing_ssd.brand == "Unknown" and "brand" in disc:
                    existing_ssd.brand = disc["brand"]
                if existing_ssd.model == "Unknown" and model_val != "Unknown":
                    existing_ssd.model = model_val
                updated += 1
            else:
                new_disc = Storage(
                    name=disc["name"],
                    brand=disc.get("brand", "Unknown"), 
                    model=model_val,
                    price=price,
                    capacity_gb=disc.get("capacity_gb"),
                    read_speed_mbps=disc.get("read_speed_mbps"),
                    write_speed_mbps=disc.get("write_speed_mbps"),
                    form_factor=form_factor,
                    storage_type=storage_type,
                    interface=interface
                )
                session.add(new_disc)
                saved += 1             
        session.commit()
        print(f"[DB] Added SSDs: {saved}, Updated prices: {updated}")

def save_cpu_to_db(cpu_list):
    engine = get_engine()
    with Session(engine) as session:
        saved=0
        updated=0

        for cpu_data in cpu_list:
            existing_cpu = session.query(CPU).filter(CPU.name == cpu_data["name"]).first()
            price = safe_parse_price(cpu_data.get("price"), cpu_data["name"])
            model_val = cpu_data.get("model", "Unknown")
            if existing_cpu:
                existing_cpu.price = price
                if existing_cpu.brand == "Unknown" and "brand" in cpu_data:
                    existing_cpu.brand = cpu_data["brand"]
                if existing_cpu.model == "Unknown" and model_val != "Unknown":
                    existing_cpu.model = model_val
                updated+=1
            else:
                raw_socket = str(cpu_data.get("socket", "")).upper()
                if "AM4" in raw_socket: db_socket = SocketType.AM4
                elif "AM5" in raw_socket: db_socket = SocketType.AM5
                elif "1700" in raw_socket: db_socket = SocketType.LGA1700
                else: db_socket = None 
                
                brand_val = cpu_data.get("brand", "Unknown")
                if brand_val == "Unknown":
                    if "AMD" in cpu_data["name"].upper(): brand_val = "AMD"
                    elif "INTEL" in cpu_data["name"].upper(): brand_val = "Intel"

                new_cpu = CPU(
                    name=cpu_data["name"],
                    brand=brand_val, 
                    model=model_val,
                    price=price,
                    socket=db_socket,
                    cores=cpu_data.get("cores") or 0,
                    threads=cpu_data.get("threads") or cpu_data.get("cores") or 0,
                    base_clock_mhz=cpu_data.get("base_clock_mhz") or 0,
                    boost_clock_mhz=cpu_data.get("boost_clock_mhz") or 0,
                    tdp=cpu_data.get("tdp_w"),
                    integrated_graphics="Tak" if cpu_data.get("has_integrated_gpu") else "Brak"
                )
                session.add(new_cpu)
                saved += 1
        session.commit()
        print(f"[DB] Added CPUs: {saved}, Updated prices: {updated}")

def save_mobo_to_db(mobo_list):
    engine = get_engine()
    with Session(engine) as session:
        saved = 0
        updated = 0
        for data in mobo_list: 
            existing_mobo = session.query(Motherboard).filter(Motherboard.name == data["name"]).first()
            price = safe_parse_price(data.get("price"), data["name"])

            model_val = data.get("model", "Unknown")
            if existing_mobo:
                existing_mobo.price = price
                if existing_mobo.brand == "Unknown" and "brand" in data:
                    existing_mobo.brand = data["brand"]
                if existing_mobo.model == "Unknown" and model_val != "Unknown":
                    existing_mobo.model = model_val
                updated+=1
            else:
                raw_socket = str(data.get("socket", "")).upper()
                if "AM4" in raw_socket: db_socket = SocketType.AM4
                elif "AM5" in raw_socket: db_socket = SocketType.AM5
                elif "1700" in raw_socket: db_socket = SocketType.LGA1700
                else: db_socket = None 
                
                raw_ddr = str(data.get("ddr_generation", "")).upper()
                db_ddr = None
                if "DDR4" in raw_ddr: db_ddr = DDRGeneration.DDR4
                elif "DDR5" in raw_ddr: db_ddr = DDRGeneration.DDR5

                raw_form = str(data.get("form_factor", "")).upper()
                if "MICRO" in raw_form or "UATX" in raw_form or "MATX" in raw_form: db_form = FormFactor.MICRO_ATX
                elif "MINI" in raw_form or "ITX" in raw_form: db_form = FormFactor.MINI_ITX
                elif "E-ATX" in raw_form or "EXTENDED" in raw_form: db_form = FormFactor.E_ATX
                elif "ATX" in raw_form: db_form = FormFactor.ATX
                else: db_form = None

                raw_chipset = str(data.get("chipset", "")).upper()
                db_chipset = None 
                for chipset_enum in ChipsetFamily:
                    if chipset_enum.value.upper() in raw_chipset:
                        db_chipset = chipset_enum
                        break

                new_mobo = Motherboard(
                    name=data["name"],
                    brand=data.get("brand", "Unknown"),
                    model=model_val,
                    price=price,
                    socket=db_socket,
                    chipset=db_chipset,
                    form_factor=db_form,
                    ddr_generation=db_ddr,
                    ram_slots=data.get("ram_slots") or 0,
                    max_ram_speed_mhz=data.get("max_ram_speed_mhz") or 0,
                    max_ram_capacity_gb=data.get("max_ram_capacity_gb") or 0
                )
                session.add(new_mobo)
                saved+=1

        session.commit()
        print(f"[DB] Added MOBOs: {saved}, Updated prices: {updated}")

def save_gpu_to_db(gpu_list):
    engine = get_engine()
    with Session(engine) as session:
        saved = 0
        updated = 0
        for data in gpu_list:
            existing = session.query(GPU).filter(GPU.name == data["name"]).first()
            price = safe_parse_price(data.get("price"), data["name"])
            
            model_val = data.get("model", "Unknown")
            if existing:
                existing.price = price
                if existing.brand == "Unknown" and "brand" in data:
                    existing.brand = data["brand"]
                if existing.model == "Unknown" and model_val != "Unknown":
                    existing.model = model_val
                if data.get("gpu_chip") and (not existing.gpu_chip or existing.gpu_chip == "Unknown"):
                    existing.gpu_chip = data["gpu_chip"]
                if data.get("memory_bus_width") and not existing.memory_bus_width:
                    existing.memory_bus_width = data["memory_bus_width"]
                updated += 1
            else:
                raw_vram = str(data.get("vram_type", "")).upper()
                db_vram = None
                if "GDDR6X" in raw_vram: db_vram = VRAMType.GDDR6X
                elif "GDDR7" in raw_vram: db_vram = VRAMType.GDDR7
                elif "GDDR6" in raw_vram: db_vram = VRAMType.GDDR6
                elif "GDDR5X" in raw_vram: db_vram = VRAMType.GDDR5X
                elif "GDDR5" in raw_vram: db_vram = VRAMType.GDDR5
                
                new_gpu = GPU(
                    name=data["name"],
                    brand=data.get("brand", "Unknown"), 
                    model=model_val,
                    price=price,
                    chip_manufacturer=data.get("chip_manufacturer", "Unknown"),
                    gpu_chip=data.get("gpu_chip", "Unknown"),
                    vram_gb=data.get("vram_gb") or 0,
                    vram_type=db_vram,
                    memory_bus_width=data.get("memory_bus_width"),
                    base_clock_mhz=data.get("base_clock_mhz") or 0,
                    boost_clock_mhz=data.get("boost_clock_mhz") or 0,
                    length_mm=data.get("length_mm") or 0,
                    width_slots=data.get("width_slots"), 
                    tdp=data.get("tdp"),
                    recommended_psu_wattage=data.get("recommended_psu_wattage") or 0,
                    pcie_power_8pin=data.get("pcie_power_8pin") or 0,
                    pcie_power_12vhpwr=data.get("pcie_power_12vhpwr") or 0
                )
                session.add(new_gpu)
                saved += 1
                
        session.commit()
        print(f"[DB] Added GPUs: {saved}, Updated prices: {updated}")

def save_ram_to_db(ram_list):
    engine = get_engine()
    with Session(engine) as session:
        saved = 0
        updated = 0
        for data in ram_list:
            existing = session.query(RAM).filter(RAM.name == data["name"]).first()
            price = safe_parse_price(data.get("price"), data["name"])
            
            model_val = data.get("model", "Unknown")
            if existing:
                existing.price = price
                if existing.brand == "Unknown" and "brand" in data:
                    existing.brand = data["brand"]
                if existing.model == "Unknown" and model_val != "Unknown":
                    existing.model = model_val
                updated += 1
            else:
                raw_ddr = str(data.get("ddr_generation", "")).upper()
                db_ddr = None
                if "DDR4" in raw_ddr: db_ddr = DDRGeneration.DDR4
                elif "DDR5" in raw_ddr: db_ddr = DDRGeneration.DDR5
                
                new_ram = RAM(
                    name=data["name"],
                    brand=data.get("brand", "Unknown"),
                    model=model_val,
                    price=price,
                    ddr_generation=db_ddr,
                    speed_mhz=data.get("speed_mhz") or 0,
                    total_capacity_gb=data.get("total_capacity_gb") or 0,
                    modules=data.get("modules") or 0,
                    capacity_per_module_gb=data.get("capacity_per_module_gb") or 0,
                    cas_latency=data.get("cas_latency"),
                    voltage=data.get("voltage", None)  
                )
                session.add(new_ram)
                saved += 1
                
        session.commit()
        print(f"[DB] Added RAM: {saved}, Updated prices: {updated}")


def save_psu_to_db(psu_list):
    engine = get_engine()
    with Session(engine) as session:
        saved = 0
        updated = 0
        
        for data in psu_list:
            existing = session.query(PSU).filter(PSU.name == data["name"]).first()
            price = safe_parse_price(data.get("price"), data["name"])
            
            model_val = data.get("model", "Unknown")
            if existing:
                existing.price = price
                if existing.brand == "Unknown" and "brand" in data:
                    existing.brand = data["brand"]
                if existing.model == "Unknown" and model_val != "Unknown":
                    existing.model = model_val
                updated += 1
            else:
                raw_eff = str(data.get("efficiency_rating", "")).upper()
                db_eff = None
                if "TITANIUM" in raw_eff: db_eff = EfficiencyRating.TITANIUM
                elif "PLATINUM" in raw_eff: db_eff = EfficiencyRating.PLATINUM
                elif "GOLD" in raw_eff: db_eff = EfficiencyRating.GOLD
                elif "SILVER" in raw_eff: db_eff = EfficiencyRating.SILVER
                elif "BRONZE" in raw_eff: db_eff = EfficiencyRating.BRONZE
                elif "80" in raw_eff or "PLUS" in raw_eff: db_eff = EfficiencyRating.PLUS_80
                
                raw_mod = str(data.get("modular_type", "")).upper()
                db_mod = None
                if "PEŁNI" in raw_mod or "FULLY" in raw_mod: db_mod = ModularType.FULLY_MODULAR
                elif "SEMI" in raw_mod or "CZĘŚCIOWO" in raw_mod: db_mod = ModularType.SEMI_MODULAR
                elif "NON" in raw_mod or "BRAK" in raw_mod: db_mod = ModularType.NON_MODULAR
                
                raw_form = str(data.get("form_factor", "")).upper()
                db_form = None
                if "SFX-L" in raw_form: db_form = PSUFormFactor.SFX_L
                elif "SFX" in raw_form: db_form = PSUFormFactor.SFX
                elif "ATX" in raw_form: db_form = PSUFormFactor.ATX
                
                def parse_pin(val):
                    if not val or val.lower() == "nie" or val.lower() == "brak": return 0
                    import re
                    match = re.search(r'\d+', str(val))
                    return int(match.group()) if match else 0
                
                new_psu = PSU(
                    name=data["name"],
                    brand=data.get("brand", "Unknown"), 
                    model=model_val,
                    price=price,
                    wattage=data.get("wattage") or 0,
                    efficiency_rating=db_eff,
                    modular_type=db_mod,
                    form_factor=db_form,
                    eps_8pin_connectors=parse_pin(data.get("eps_8pin")),
                    pcie_8pin_connectors=parse_pin(data.get("pcie_8pin")),
                    pcie_6pin_connectors=parse_pin(data.get("pcie_6pin")),
                    has_12vhpwr=data.get("has_12vhpwr", False),
                    num_12vhpwr=1 if data.get("has_12vhpwr", False) else 0
                )
                session.add(new_psu)
                saved += 1
                
        session.commit()
        print(f"[DB] Added PSUs: {saved}, Updated prices: {updated}")


def save_case_to_db(case_list):
    engine = get_engine()
    with Session(engine) as session:
        saved = 0
        updated = 0
        
        for data in case_list:
            existing = session.query(Case).filter(Case.name == data["name"]).first()
            price = safe_parse_price(data.get("price"), data["name"])
            
            model_val = data.get("model", "Unknown")
            if existing:
                existing.price = price
                if existing.brand == "Unknown" and "brand" in data:
                    existing.brand = data["brand"]
                if existing.model == "Unknown" and model_val != "Unknown":
                    existing.model = model_val
                
                existing.height_mm = data.get("height_mm", existing.height_mm)
                existing.width_mm = data.get("width_mm", existing.width_mm)
                existing.length_mm = data.get("length_mm", existing.length_mm)
                existing.weight_kg = data.get("weight_kg", existing.weight_kg)
                if "front_io_usb_c" in data:
                    existing.front_io_usb_c = data["front_io_usb_c"]
                if "drive_bays_35" in data:
                    existing.drive_bays_35 = data["drive_bays_35"]
                if "drive_bays_25" in data:
                    existing.drive_bays_25 = data["drive_bays_25"]
                updated += 1
            else:
                new_case = Case(
                    name=data["name"],
                    brand=data.get("brand", "Unknown"), 
                    model=model_val,
                    price=price,
                    case_type=data.get("case_type", "Unknown"),
                    max_gpu_length_mm=data.get("max_gpu_length_mm"),
                    max_cpu_cooler_height_mm=data.get("max_cpu_cooler_height_mm"),
                    drive_bays_35=data.get("drive_bays_35") or 0,
                    drive_bays_25=data.get("drive_bays_25") or 0,
                    height_mm=data.get("height_mm"),
                    width_mm=data.get("width_mm"),
                    length_mm=data.get("length_mm"),
                    weight_kg=data.get("weight_kg"),
                    front_io_usb_c=data.get("front_io_usb_c", False),
                    included_fans=0,
                    max_fan_slots=0,
                    has_tempered_glass=data.get("has_tempered_glass", False),
                    psu_form_factor=PSUFormFactor.ATX
                )
                session.add(new_case)
                saved += 1
                
        session.commit()
        print(f"[DB] Added Cases: {saved}, Updated prices: {updated}")


