import os
from dotenv import load_dotenv
load_dotenv()
import re
import json
import time
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import logging

from scraper.loader import save_case_to_db
from scraper.playwright_utils import fetch_rendered_html

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

URL_CASE = os.getenv("SCRAPER_URL_CASE")

def parse_case_json_ld(html_content: str) -> List[Dict[str, Any]]:
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
                    name = item_data.get("name", "Unknown Case")
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
    
    clean["case_type"] = raw_data.get("Typ obudowy", "Midi Tower").strip()
    clean["psu_form_factor"] = raw_data.get("Zasilacz", "Brak zasilacza").strip()
    
    okno = raw_data.get("Okno", "")
    clean["has_tempered_glass"] = "Szkło" in okno or "Tak" in okno or "oknem" in okno

    gpu_txt = raw_data.get("Maksymalna długość karty graficznej [cm]", "")
    match_gpu = re.search(r'[\d\.]+', gpu_txt.replace(',', '.'))
    clean["max_gpu_length_mm"] = int(float(match_gpu.group()) * 10) if match_gpu else 300
    
    cpu_txt = raw_data.get("Maksymalna wysokość układu chłodzenia CPU [cm]", "")
    match_cpu = re.search(r'[\d\.]+', cpu_txt.replace(',', '.'))
    clean["max_cpu_cooler_height_mm"] = int(float(match_cpu.group()) * 10) if match_cpu else 160
    
    bays_35 = raw_data.get("Wnęki wewnętrzne 3.5 cala", "")
    match_35 = re.search(r'\d+', bays_35)
    clean["drive_bays_35"] = int(match_35.group()) if match_35 else 2
    
    bays_25 = raw_data.get("Wnęki wewnętrzne 2.5 cala", "")
    match_25 = re.search(r'\d+', bays_25)
    clean["drive_bays_25"] = int(match_25.group()) if match_25 else 2

    # Wymiary fizyczne
    h_txt = raw_data.get("Wysokość [cm]", "")
    m_h = re.search(r'[\d\.]+', h_txt.replace(',', '.'))
    clean["height_mm"] = int(float(m_h.group()) * 10) if m_h else None

    w_txt = raw_data.get("Szerokość [cm]", "")
    m_w = re.search(r'[\d\.]+', w_txt.replace(',', '.'))
    clean["width_mm"] = int(float(m_w.group()) * 10) if m_w else None

    l_txt = raw_data.get("Głębokość [cm]", "")
    m_l = re.search(r'[\d\.]+', l_txt.replace(',', '.'))
    clean["length_mm"] = int(float(m_l.group()) * 10) if m_l else None
    
    wg_txt = raw_data.get("Waga [kg]", "")
    m_wg = re.search(r'[\d\.]+', wg_txt.replace(',', '.'))
    clean["weight_kg"] = float(m_wg.group()) if m_wg else None
    
    usb_c = raw_data.get("USB Typ-C", "Brak")
    clean["front_io_usb_c"] = "Brak" not in usb_c and "Nie" not in usb_c

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
    logger.info(f"Starting Morele.net Case scraper. Target: {URL_CASE}")
    raw_html = fetch_rendered_html(URL_CASE)
    if not raw_html:
        logger.warning("Failed to retrieve HTML content. Exiting.")
        return
        
    case_list = parse_case_json_ld(raw_html)
    ready_case = []
    
    for case in case_list[:20]:
        logger.info(f"Extracted -> Price: {case['price']} PLN | Model: {case['name']}")
        url = case.get("url")
        if not url:
            continue
        spec = get_spec(url)
        case.update(spec)
        ready_case.append(case)

        time.sleep(1.5)

    logger.info(f"Successfully extracted {len(ready_case)} Case products.")
    save_case_to_db(ready_case)

if __name__ == "__main__":
    main()
