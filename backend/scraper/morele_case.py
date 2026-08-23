import re
import json
import time
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import logging
from app.db.base import get_engine
from sqlalchemy.orm import Session
from app.models.components import Case
from scraper.loader import save_case_to_db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

URL_CASE = "***REMOVED***"
DEFAULT_TIMEOUT_MS = 30000


def fetch_rendered_html(url: str) -> str:
    logger.info(f"Initializing headless browser for URL: {url}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, timeout=DEFAULT_TIMEOUT_MS)
            page.wait_for_selector(".product-specification__table", timeout=10000)
        except Exception:
            try:
                page.wait_for_selector(".cat-product", timeout=5000)
            except Exception:
                pass
        html_content = page.content()
        browser.close()
        return html_content

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
    clean["has_tempered_glass"] = "Szkło" in raw_data.get("Okno", "") or "Tak" in raw_data.get("Okno", "")

    gpu_txt = raw_data.get("Maksymalna długość karty graficznej [cm]", "")
    match_gpu = re.search(r'\d+', gpu_txt)
    clean["max_gpu_length_mm"] = int(float(match_gpu.group()) * 10) if match_gpu else 300
    
    cpu_txt = raw_data.get("Maksymalna wysokość układu chłodzenia CPU [cm]", "")
    match_cpu = re.search(r'\d+', cpu_txt)
    clean["max_cpu_cooler_height_mm"] = int(float(match_cpu.group()) * 10) if match_cpu else 160
    
    clean["drive_bays_35"] = 2
    clean["drive_bays_25"] = 2
    
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
    
    case_list = parse_case_json_ld(raw_html)
    ready_case = []
    
    for case in case_list[:6]:
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
