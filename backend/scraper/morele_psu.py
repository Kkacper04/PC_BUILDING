import re
import json
import time
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import logging

from scraper.loader import save_psu_to_db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

URL_PSU = "***REMOVED***"
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

def parse_psu_json_ld(html_content: str) -> List[Dict[str, Any]]:
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
                    name = item_data.get("name", "Unknown PSU")
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
    
    watt_txt = raw_data.get("Moc", "")
    match_watt = re.search(r'\d+', watt_txt)
    clean["wattage"] = int(match_watt.group()) if match_watt else 500
    
    clean["efficiency_rating"] = raw_data.get("Certyfikat sprawności", "80 Plus").strip()
    clean["modular_type"] = raw_data.get("Modularne okablowanie", "Brak").strip()
    clean["form_factor"] = raw_data.get("Standard/Format", "ATX").strip()
    
    clean["eps_8pin"] = raw_data.get("CPU 8-pin (4+4)", raw_data.get("CPU 8-pin", "1"))
    clean["pcie_8pin"] = raw_data.get("PCI-E 8-pin (6+2)", "0")
    clean["pcie_6pin"] = raw_data.get("PCI-E 6-pin", "0")
    
    vhpwr = raw_data.get("PCI-E 16-pin (12+4)", "Nie")
    clean["has_12vhpwr"] = vhpwr != "Nie" and vhpwr != "0"
    
    length_txt = raw_data.get("Głębokość [mm]", "")
    match_len = re.search(r'\d+', length_txt)
    clean["length_mm"] = int(match_len.group()) if match_len else 140

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
    logger.info(f"Starting Morele.net PSU scraper. Target: {URL_PSU}")
    raw_html = fetch_rendered_html(URL_PSU)
    
    psu_list = parse_psu_json_ld(raw_html)
    ready_psu = []
    
    for psu in psu_list[:30]:
        logger.info(f"Extracted -> Price: {psu['price']} PLN | Model: {psu['name']}")
        url = psu.get("url")
        if not url:
            continue
        spec = get_spec(url)
        psu.update(spec)
        ready_psu.append(psu)

        time.sleep(1.5)

    logger.info(f"Successfully extracted {len(ready_psu)} PSU products.")
    save_psu_to_db(ready_psu)

if __name__ == "__main__":
    main()
