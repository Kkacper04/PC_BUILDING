import json
import logging
from typing import Dict, List, Optional, Any
import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from scraper.loader import setup_database,save_mobo_to_db
import time
from scraper.morele_cpu import  fetch_rendered_html

# Configure standard Python logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

URL_MOBO = "***REMOVED***"
DEFAULT_TIMEOUT_MS = 30000
def parse_mobo_json_ld(html_content: str) -> List[Dict[str, Any]]:
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
                    
                    name = item_data.get("name", "Unknown MOBO")
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
    clean["socket"] = raw_data.get("Gniazdo procesora", "Unknown").strip()
    clean["chipset"] = raw_data.get("Chipset płyty", "Unknown").strip()
    clean["form_factor"] = raw_data.get("Standard płyty", "Unknown").strip()
    clean["ddr_generation"] = raw_data.get("Standard pamięci", "Unknown").strip()

    ram_slots_txt = raw_data.get("Liczba gniazd pamięci")
    if ram_slots_txt and ram_slots_txt.isdigit():
        clean["ram_slots"] = int (ram_slots_txt)
    else:
        clean["ram_slots"] = 4

    max_ram_txt = raw_data.get("Maksymalna ilość pamięci", "")

    match = re.search(r'\d+',max_ram_txt)

    if match:
        clean["max_ram_capacity_gb"] = int(match.group())
    else:
        clean["max_ram_capacity_gb"] = 128

    speed_txt = raw_data.get("Częstotliwości pracy pamięci", "")
    all = re.findall(r'\d+', speed_txt)

    if all:
        clean["max_ram_speed_mhz"] = max([int(speed) for speed in all])
    else:
        clean["max_ram_speed_mhz"] = 4800
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

    raw_html = fetch_rendered_html(URL_MOBO)
    if not raw_html:
        return
    mobo_list = parse_mobo_json_ld(raw_html)

    for mobo in mobo_list[:4]:
        url= mobo.get("url")
        if not url:
            continue

        spec = get_spec(url)
        mobo.update(spec)

        print(f"Nazwa: {mobo.get('name')}")
        print(f"Socket: {mobo.get('socket')} | Chipset: {mobo.get('chipset')}")
        print(f"Max RAM: {mobo.get('max_ram_capacity_gb')} GB | Predkosc RAM: {mobo.get('max_ram_speed_mhz')} MHz")

        time.sleep(1.5)

    logger.info(f"Successfully extracted {len(mobo_list)} Motherboards to db ")
    save_mobo_to_db(mobo_list[:4])

if __name__ == "__main__":
    main()

