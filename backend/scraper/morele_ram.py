import json
import logging
from scraper.playwright_utils import fetch_rendered_html
from typing import Dict, List, Optional, Any
import re
from bs4 import BeautifulSoup
from scraper.loader import save_ram_to_db
import time
from scraper.morele_cpu import  fetch_rendered_html

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


URL_RAM = "***REMOVED***"


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
    logger.info(f"Starting Morele.net RAM scraper. Target: {URL_RAM}")
    
    all_rams = []
    
    for page in range(1, 3):  
        page_url = URL_RAM if page == 1 else f"{URL_RAM}?page={page}"
        logger.info(f"Fetching page {page}...")
        raw_html = fetch_rendered_html(page_url)
        if not raw_html:
            continue
        page_items = parse_ram_json_ld(raw_html)
        all_rams.extend(page_items)
        
    if not all_rams:
        logger.warning("Failed to retrieve any RAMs. Exiting.")
        return
        
    ready_ram = []
    
    for ram in all_rams[:50]:
        logger.info(f"Extracted -> Price: {ram['price']} PLN | Model: {ram['name']}")
        url = ram.get("url")
        if not url:
            continue
        spec = get_spec(url)
        ram.update(spec)
        ready_ram.append(ram)
        time.sleep(1.5)

    logger.info(f"Successfully extracted {len(ready_ram)} RAM products.")
    save_ram_to_db(ready_ram)

if __name__ == "__main__":
    main()




