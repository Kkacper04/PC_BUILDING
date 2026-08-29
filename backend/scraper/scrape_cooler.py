import os
from dotenv import load_dotenv
load_dotenv()
import re
import json
import time
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import logging
from scraper.playwright_utils import fetch_rendered_html
from scraper.loader import save_cooler_to_db



logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

URL_COOLER = os.getenv("SCRAPER_URL_COOLER")

def parse_cooler_json_ld(html_content: str) -> List[Dict[str, Any]]:
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
                    name = item_data.get("name", "Unknown Cooler")
                    price = item_data.get("offers", {}).get("price", "0")
                    url = item_data.get("url")
                    if url:
                        products.append({"name": name, "price": price, "url": url})
                break 
        except json.JSONDecodeError:
            continue
            
    return products

def norm_data(raw_data: dict) -> dict:
    clean = {}
    brand_raw = raw_data.get("Producent") or raw_data.get("Marka") or "Unknown"
    clean["brand"] = brand_raw.strip()
    clean["model"] = raw_data.get("Kod producenta", "Unknown").strip()
    
    # cooler_type (air vs aio_liquid)
    chlodzenie = raw_data.get("Typ chłodzenia", "").lower()
    
    if "wodn" in chlodzenie or "aio" in chlodzenie:
        clean["cooler_type"] = "aio_liquid"
    else:
        clean["cooler_type"] = "air"
        
    # height_mm
    h_txt = raw_data.get("Wysokość [mm]", "")
    m_h = re.search(r'\d+', h_txt)
    clean["height_mm"] = int(m_h.group()) if m_h else None
    
    # radiator_size_mm
    rad_txt = raw_data.get("Rozmiar chłodnicy", "")
    m_rad = re.search(r'\d+', rad_txt)
    if clean["cooler_type"] == "aio_liquid" and m_rad:
        clean["radiator_size_mm"] = int(m_rad.group())
    else:
        clean["radiator_size_mm"] = None
        
    # fan_count
    f_txt = raw_data.get("Liczba wentylatorów", "")
    m_f = re.search(r'\d+', f_txt)
    clean["fan_count"] = int(m_f.group()) if m_f else 1
    
    # fan_size_mm
    fs_txt = raw_data.get("Średnica wentylatora", "")
    m_fs = re.search(r'\d+', fs_txt)
    clean["fan_size_mm"] = int(m_fs.group()) if m_fs else None
    
    # max_tdp
    tdp_txt = raw_data.get("Maksymalne TDP", "")
    m_tdp = re.search(r'\d+', tdp_txt)
    clean["max_tdp"] = int(m_tdp.group()) if m_tdp else 150
    
    # max_noise_dba
    noise_txt = raw_data.get("Maksymalny poziom hałasu", "")
    m_noise = re.search(r'\d+(\.\d+)?', noise_txt.replace(',', '.'))
    clean["max_noise_dba"] = float(m_noise.group()) if m_noise else None
    
    # has_rgb
    rgb_txt = raw_data.get("Podświetlenie", "").lower()
    clean["has_rgb"] = "rgb" in rgb_txt or "argb" in rgb_txt
    
    return clean    

def get_spec(url):
    html_content = fetch_rendered_html(url)
    if not html_content:
        return {}
    
    soup = BeautifulSoup(html_content, "lxml")
    table = soup.find("div", class_="product-specification__table")
    
    if not table:
        return {}
        
    raw_data = {}
    rows = table.find_all("div", class_="specification__row")
    for r in rows:
        name_tag = r.find("span", class_="specification__name")
        val_tag = r.find("span", class_="specification__value")
        if name_tag and val_tag:
            raw_data[name_tag.text.strip()] = val_tag.text.strip()
            
    return norm_data(raw_data)

def main():
    logger.info(f"Starting Morele.net Cooler scraper. Target: {URL_COOLER}")
    raw_html = fetch_rendered_html(URL_COOLER)
    if not raw_html:
        logger.warning("Failed to retrieve HTML content. Exiting.")
        return
        
    cooler_list = parse_cooler_json_ld(raw_html)
    ready_coolers = []
    
    for cooler in cooler_list[:30]:
        logger.info(f"Extracted -> Price: {cooler['price']} PLN | Model: {cooler['name']}")
        url = cooler.get("url")
        if not url:
            continue
        spec = get_spec(url)
        cooler.update(spec)
        ready_coolers.append(cooler)

        time.sleep(1.5)

    logger.info(f"Successfully extracted {len(ready_coolers)} Cooler products.")
    save_cooler_to_db(ready_coolers)

if __name__ == "__main__":
    main()
