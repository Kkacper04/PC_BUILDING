import json
import logging
from typing import Dict, List, Optional, Any
import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from scraper.loader import setup_database,save_gpu_to_db
from scraper.morele_cpu import  fetch_rendered_html
import time

# Configure standard Python logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

URL_GPU = "***REMOVED***"
DEFAULT_TIMEOUT_MS = 30000


def parse_gpu_json_ld(html_content: str) -> List[Dict[str, Any]]:
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
                    
                    name = item_data.get("name", "Unknown GPU")
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
    chipset = raw_data.get("Chipset karty graficznej", "").upper()
    if "RTX" in chipset or "GTX" in chipset or "NVIDIA" in chipset:
        clean["chip_manufacturer"] = "NVIDIA"
    elif "RX" in chipset or "RADEON" in chipset or "AMD" in chipset:
        clean["chip_manufacturer"] = "AMD"
    else:
        clean["chip_manufacturer"] = "NVIDIA"

    vram_txt = raw_data.get("Ilość pamięci RAM", "")
    match_vram = re.search(r'\d+', vram_txt)
    clean["vram_gb"] = int(match_vram.group()) if match_vram else 8
    clean["vram_type"] = raw_data.get("Rodzaj pamięci RAM", "GDDR6").strip().upper()

    base_txt = raw_data.get("Taktowanie rdzenia", "")
    match_base = re.search(r'\d+', base_txt)
    clean["base_clock_mhz"] = int(match_base.group()) if match_base else 2000
    
    boost_txt = raw_data.get("Taktowanie rdzenia w trybie boost", "")
    match_boost = re.search(r'\d+', boost_txt)
    clean["boost_clock_mhz"] = int(match_boost.group()) if match_boost else 2500

    length_txt = raw_data.get("Długość karty", "")
    match_length = re.search(r'\d+', length_txt)
    clean["length_mm"] = int(match_length.group()) if match_length else 280
    
    psu_txt = raw_data.get("Rekomendowana moc zasilacza", "")
    match_psu = re.search(r'\d+', psu_txt)
    clean["recommended_psu_wattage"] = int(match_psu.group()) if match_psu else 600
    clean["tdp"] = clean["recommended_psu_wattage"] // 2 


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
    logger.info("Starting GPU extraction routine via Playwright")
    
    raw_html = fetch_rendered_html(URL_GPU)
    if not raw_html:
        logger.warning("Failed to retrieve HTML content. Exiting.")
        return
        
    gpu_list = parse_gpu_json_ld(raw_html)
    ready_gpu = []
    
    for gpu in gpu_list[:6]:
        logger.info(f"Extracted -> Price: {gpu['price']} PLN | Model: {gpu['name']}")
        url = gpu.get("url")
        if not url:
            continue
        spec = get_spec(url)
        gpu.update(spec)
        ready_gpu.append(gpu)

        time.sleep(1.5)

    logger.info(f"Successfully extracted {len(ready_gpu)} GPU products.")
    save_gpu_to_db(ready_gpu)

if __name__ == "__main__":
    main()