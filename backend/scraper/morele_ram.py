import json
import logging
from typing import Dict, List, Optional, Any
import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from scraper.loader import setup_database, save_ram_to_db
import time
from scraper.morele_cpu import  fetch_rendered_html

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


URL_RAM = "***REMOVED***"
DEFAULT_TIMEOUT_MS = 30000


def parse_ram_json_ld(html_content: str) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html_content, "lxml")
    json_scripts = soup.find_all("script", type="application/ld+json")
    
    products = []
    
    for script in json_scripts:
        if not script.string:
            continue
            
        try:
            data = json.loads(script.string)
            if data.get("@type") == "ItemList":
                items = data.get("itemListElement", [])
                for element in items:
                    item_data = element.get("item", {})
                    
                    name = item_data.get("name", "Unknown Ram")
                    price = item_data.get("offers", {}).get("price", "0")
                    url = item_data.get("url")
                    
                    products.append({"name": name, "price": price, "url": url})
                
               
                break 
                
        except json.JSONDecodeError:
            logger.debug("Failed to decode JSON block, skipping...")
            continue
            
    return products


def norm_data(raw_data: dict) -> dict:
    clean = {}
    brand_raw = raw_data.get("Producent") or raw_data.get("Marka") or "Unknown"
    clean["brand"] = brand_raw.strip()
    clean["model"] = raw_data.get("Kod producenta", "Unknown").strip()
    clean["ddr_generation"] = raw_data.get("Typ pamięci", "DDR5").strip()

    capacity_txt = raw_data.get("Pojemność całkowita", "")

    match_cap = re.search(r'\d+', capacity_txt)

    clean["total_capacity_gb"]= int(match_cap.group()) if match_cap else 16

    modules_txt = raw_data.get("Liczba modułów", "2")

    if modules_txt and modules_txt.isdigit():
        clean["modules"] = int(modules_txt)
    else:
        clean["modules"] = 2

    clean["capacity_per_module_gb"] = clean["total_capacity_gb"] // clean.get("modules", 2)

    operating_frequency_txt = raw_data.get("Częstotliwość pracy [MHz]", "")
    match =re.search(r'\d+' , operating_frequency_txt)
 
    clean["speed_mhz"] = int(match.group()) if match else 6000

    delay_txt = raw_data.get("Opóźnienie", "")
    match_del = re.search(r'\d+',delay_txt)
    clean["cas_latency"] = int(match_del.group()) if match_del else 32

    voltage_txt = raw_data.get("Napięcie [V]", "")
    match_vol = re.search(r'(\d+[\.,]\d+)', voltage_txt)

    if match_vol:
        value = match_vol.group(1).replace(',','.')
        clean["voltage"] = float(value)
    else:
        clean["voltage"] = None
    return clean
def get_spec(url):
    html_content = fetch_rendered_html(url)
    
    if not html_content:
        return {}
            
    soup = BeautifulSoup(html_content, "lxml")
    raw_data ={}
    table =soup.find("div", class_="product-specification__table")
    
    if table:
        rows = table.find_all("div", class_="specification__row")
    
        for row in rows:
            el_name = row.find("span", class_="specification__name")
            el_val = row.find("span", class_="specification__value")
    
            if el_name and el_val:
                key= el_name.text.strip()
                value = el_val.text.strip()
                raw_data[key] = value
    
        return norm_data(raw_data)
    return {}

def main():
    logger.info("Starting Motherboard extraction routine via Playwright")

    raw_html = fetch_rendered_html(URL_RAM)
    if not raw_html:
        return
    ram_list = parse_ram_json_ld(raw_html)

    ready_ram = []
    for ram in ram_list[:10]:
        url= ram.get("url")
        if not url:
            continue

        spec = get_spec(url)
        ram.update(spec)
        ready_ram.append(ram)

        print(f"Nazwa: {ram.get('name')}")
        print(f"Typ: {ram.get('ddr_generation')} | {ram.get('total_capacity_gb')}GB ({ram.get('modules')}x{ram.get('capacity_per_module_gb')}GB)")
        print(f"Prędkość: {ram.get('speed_mhz')} MHz | CL {ram.get('cas_latency')} | {ram.get('voltage', 'Brak')} V")

        time.sleep(1.5)

    logger.info(f"Successfully extracted {len(ready_ram)} rams to db ")
    save_ram_to_db(ready_ram)

if __name__ == "__main__":
    main()




