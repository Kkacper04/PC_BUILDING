from dotenv import load_dotenv
load_dotenv()

from decimal import Decimal
from sqlalchemy.orm import Session
from app.db.base import get_engine, Base
from app.models.components import Storage,CPU
from app.models.enums import StorageType, StorageFormFactor, StorageInterface, SocketType
from app.models.components import Storage, CPU, Motherboard
from app.models.enums import StorageType, StorageFormFactor, StorageInterface, SocketType, ChipsetFamily, FormFactor, DDRGeneration
from app.models.components import Storage, CPU, Motherboard, GPU
from app.models.enums import StorageType, StorageFormFactor, StorageInterface, SocketType, ChipsetFamily, FormFactor, DDRGeneration, VRAMType


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
            try:
                price = Decimal(disc.get("price", 0))
            except Exception:
                price = Decimal("0.00")

            if existing_ssd:
                existing_ssd.price = price
                updated += 1
            else:
                new_disc = Storage(
                    name=disc["name"],
                    brand="Unknown", 
                    model="Unknown",
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
        print(f"[DB] Added: {saved}, Updated prices: {updated}")


def save_cpu_to_db(cpu_list):
    engine = get_engine()
    with Session(engine) as session:
        saved=0
        updated=0

        for cpu_data in cpu_list:
            existing_cpu = session.query(CPU).filter(CPU.name ==cpu_data["name"]).first()

            try:
                price = Decimal(cpu_data.get("price",0))
            except Exception:
                price = Decimal("0.00")

            if existing_cpu:
                existing_cpu.price = price
                updated+=1
            else:
                raw_socket = str(cpu_data.get("socket", "")).upper()
                if "AM4" in raw_socket:
                    db_socket = SocketType.AM4
                elif "AM5" in raw_socket:
                    db_socket = SocketType.AM5
                elif "1700" in raw_socket:
                    db_socket = SocketType.LGA1700
                else:
                    db_socket = SocketType.AM5 # default
                
                new_cpu = CPU(
                    name=cpu_data["name"],
                    brand="AMD" if "AMD" in cpu_data["name"] else "Intel", 
                    model="Unknown",
                    price=price,
                    socket=db_socket,
                    cores=cpu_data.get("cores", 4) or 4,
                    threads=cpu_data.get("threads") or cpu_data.get("cores", 4),
                    base_clock_mhz=cpu_data.get("base_clock_mhz", 0),
                    boost_clock_mhz=cpu_data.get("boost_clock_mhz", 0),
                    tdp=cpu_data.get("tdp_w", 65) or 65,
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

            try:
                price = Decimal(data.get("price",0))
            except Exception:
                price = Decimal("0.00")

            if existing_mobo:
                existing_mobo.price = price
                updated+=1
            else:
                raw_socket = str(data.get("socket", "")).upper()
                if "AM4" in raw_socket: db_socket = SocketType.AM4
                elif "AM5" in raw_socket: db_socket = SocketType.AM5
                elif "1700" in raw_socket: db_socket = SocketType.LGA1700
                else: db_socket = SocketType.AM5 
                
                raw_ddr = str(data.get("ddr_generation", "")).upper()
                db_ddr = DDRGeneration.DDR4 if "DDR4" in raw_ddr else DDRGeneration.DDR5

                # mapping format (ATX, uATX itd)
                raw_form = str(data.get("form_factor", "")).upper()
                if "MICRO" in raw_form or "UATX" in raw_form or "MATX" in raw_form:
                    db_form = FormFactor.MICRO_ATX
                elif "MINI" in raw_form or "ITX" in raw_form:
                    db_form = FormFactor.MINI_ITX
                elif "E-ATX" in raw_form or "EXTENDED" in raw_form:
                    db_form = FormFactor.E_ATX
                else:
                    db_form = FormFactor.ATX

                raw_chipset = str(data.get("chipset", "")).upper()
                db_chipset = ChipsetFamily.B650 #default

                for chipset_enum in ChipsetFamily:
                    if chipset_enum.value.upper() in raw_chipset:
                        db_chipset = chipset_enum
                        break

                new_mobo = Motherboard(
                     name=data["name"],
                    brand="Unknown",
                    model="Unknown",
                    price=price,
                    socket=db_socket,
                    chipset=db_chipset,
                    form_factor=db_form,
                    ddr_generation=db_ddr,
                    ram_slots=data.get("ram_slots", 4) or 4,
                    max_ram_speed_mhz=data.get("max_ram_speed_mhz", 4800) or 4800,
                    max_ram_capacity_gb=data.get("max_ram_capacity_gb", 128) or 128
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
            try:
                price = Decimal(data.get("price", 0))
            except Exception:
                price = Decimal("0.00")
            if existing:
                existing.price = price
                updated += 1
            else:
                raw_vram = str(data.get("vram_type", "")).upper()
                if "GDDR6X" in raw_vram:
                    db_vram = VRAMType.GDDR6X
                elif "GDDR7" in raw_vram:
                    db_vram = VRAMType.GDDR7
                else:
                    db_vram = VRAMType.GDDR6 
                
                new_gpu = GPU(
                    name=data["name"],
                    brand="Unknown", 
                    model="Unknown",
                    price=price,
                    chip_manufacturer=data.get("chip_manufacturer", "NVIDIA"),
                    vram_gb=data.get("vram_gb", 8),
                    vram_type=db_vram,
                    base_clock_mhz=data.get("base_clock_mhz", 1500),
                    boost_clock_mhz=data.get("boost_clock_mhz", 1800),
                    length_mm=data.get("length_mm", 280),
                    width_slots=Decimal("2.5"), 
                    tdp=data.get("tdp", 200),
                    recommended_psu_wattage=data.get("recommended_psu_wattage", 550),
                    pcie_power_8pin=1,
                    pcie_power_12vhpwr=0
                )
                session.add(new_gpu)
                saved += 1
                
        session.commit()
        print(f"[DB] Added GPUs: {saved}, Updated prices: {updated}")
