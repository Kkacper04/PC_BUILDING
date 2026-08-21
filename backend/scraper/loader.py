from dotenv import load_dotenv
load_dotenv()

from decimal import Decimal
from sqlalchemy.orm import Session
from app.db.base import get_engine, Base
from app.models.components import Storage,CPU
from app.models.enums import StorageType, StorageFormFactor, StorageInterface, SocketType

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