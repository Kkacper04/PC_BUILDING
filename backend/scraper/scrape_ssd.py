import os
from dotenv import load_dotenv
load_dotenv()
import json
import logging
from scraper.playwright_utils import fetch_rendered_html
from typing import Dict, List, Optional, Any
import re
import time
from bs4 import BeautifulSoup

from scraper.loader import save_disc_to_db
from scraper.playwright_utils import fetch_rendered_html

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

URL_SSD = os.getenv("SCRAPER_URL_SSD")

def parse_ssd_json_ld(html_content: str) -> List[Dict[str, Any]]:
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
                    
                    name = item_data.get("name", "Unknown SSD")
                    price = item_data.get("offers", {}).get("price", "0")
                    url = item_data.get("url")
                    
                    products.append({"name": name, "price": price, "url": url})
                
                break 
                
        except json.JSONDecodeError:
            logger.debug("Failed to decode JSON block, skipping...")
            continue
            
    return products

def norm_data(data):
    convert = {}
    brand_raw = data.get("Producent") or data.get("Marka") or "Unknown"
    convert["brand"] = brand_raw.strip()
    convert["model"] = data.get("Kod producenta", "Unknown").strip()
    capacity_txt = data.get("Pojemność dysku")
    if capacity_txt:
        match = re.search(r'(\d+)\s*(TB|GB)', capacity_txt)
        if match:
            value = int(match.group(1))
            unit = match.group(2)
            if unit == "TB":
                convert["capacity_gb"] = value * 1000
            else:
                convert["capacity_gb"] = value
    
    read_speed_txt = data.get("Szybkość odczytu")
    if read_speed_txt:
       match = re.search(r'(\d+)', read_speed_txt)
       if match:
             convert["read_speed_mbps"] = int(match.group(1))
    
    write_speed_txt = data.get("Szybkość zapisu")
    if write_speed_txt:
        match = re.search(r'(\d+)', write_speed_txt)
        if match:
            convert["write_speed_mbps"] = int(match.group(1))
    
    format_txt = data.get("Format dysku")
    if format_txt:
       format_txt_lower = format_txt.lower()
       if "m.2" in format_txt_lower:
            convert["form_factor"] = "M.2"
       elif "2.5" in format_txt_lower:
            convert["form_factor"] = "2.5-inch"
       else:
            convert["form_factor"] = "Inny"
    return convert

def get_spec(url):
    html_content = fetch_rendered_html(url)
    
    if not html_content:
        return {}
            
    soup = BeautifulSoup(html_content, "lxml")
    raw_data = {}
    table = soup.find("div", class_="product-specification__table")

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
    logger.info("Starting SSD extraction routine via Playwright")
    
    raw_html = fetch_rendered_html(URL_SSD)
    if not raw_html:
        logger.warning("Failed to retrieve HTML content. Exiting.")
        return
        
    ssd_list = parse_ssd_json_ld(raw_html)
    ready_to_save = []
    
    for ssd in ssd_list[:30]:
        logger.info(f"Extracting: {ssd['name']}")
        
        url = ssd.get("url")
        if not url:
            continue
            
        spec = get_spec(url)
        ssd.update(spec)
        ready_to_save.append(ssd)
        
        print(f"Name: {ssd.get('name')}")
        print(f"Capacity: {ssd.get('capacity_gb')} GB | Form factor: {ssd.get('form_factor')}")
        print(f"Speed (Read/Write): {ssd.get('read_speed_mbps', 0)} / {ssd.get('write_speed_mbps', 0)} MB/s")

        time.sleep(1.5)
        
    logger.info("Finished extracting SSDs. Saving to database...")
    save_disc_to_db(ready_to_save)

if __name__ == "__main__":
    main()