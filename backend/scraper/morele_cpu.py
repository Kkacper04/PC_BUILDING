import json
import logging
from typing import Dict, List, Optional, Any
import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from scraper.loader import setup_database,save_cpu_to_db
import time

# Configure standard Python logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

URL_CPU = "***REMOVED***"
DEFAULT_TIMEOUT_MS = 30000

def fetch_rendered_html(url: str) -> Optional[str]:
    logger.info(f"Initializing headless browser for URL: {url}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Spoof user-agent to mitigate basic bot-detection mechanisms
        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
        try:
            page.goto(url, timeout=DEFAULT_TIMEOUT_MS)
            
            # Allow time for asynchronous client-side rendering (dynamic product grids)
            # Using playwright's built-in wait rather than time.sleep()
            page.wait_for_timeout(2000) 
            
            html_content = page.content()
            return html_content
            
        except PlaywrightTimeoutError:
            logger.error(f"Timeout while trying to load {url}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during page load: {e}")
            return None
        finally:
            browser.close()

def parse_cpu_json_ld(html_content: str) -> List[Dict[str, Any]]:
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
                    
                    name = item_data.get("name", "Unknown CPU")
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
    clean["socket"] = raw_data.get("Gniazdo procesora", "Unknown").strip()
    cores_txt =  raw_data.get("Liczba rdzeni")
    if cores_txt and cores_txt.isdigit():
        clean["cores"] = int (cores_txt)
    else:
        clean["cores"] = 0

    tdp_txt = raw_data.get("TDP", "")
    result = re.search(r'\d+',tdp_txt)
    if result:
         clean["tdp_w"] = int(result.group())
    else:
        clean["tdp_w"] = 0

    graphic_txt = raw_data.get("Zintegrowany układ graficzny", "Brak")
    if "brak" in graphic_txt.lower():
        clean["has_integrated_gpu"] = False
    else:
        clean["has_integrated_gpu"] = True
    threads_txt = raw_data.get("Wątki") or raw_data.get("Liczba wątków")
    if threads_txt and threads_txt.isdigit():
        clean["threads"] = int(threads_txt)
    else:
        clean["threads"] = clean.get("cores", 4)

    base_txt = raw_data.get("Częstotliwość taktowania procesora", "")
    base_match = re.search(r'(\d+[\.,]\d+)', base_txt)
    
    if base_match:
        with_dot = base_match.group(1).replace(',', '.')
        clean["base_clock_mhz"] = int(float(with_dot) * 1000)
    else:
        base_match_int = re.search(r'\d+', base_txt)
        clean["base_clock_mhz"] = int(base_match_int.group()) * 1000 if base_match_int else 0

    max_txt = raw_data.get("Częstotliwość maksymalna Turbo", "")
    max_match = re.search(r'(\d+[\.,]\d+)', max_txt)
        
    if max_match:
        max_with_dot = max_match.group(1).replace(',', '.')
        clean["boost_clock_mhz"] = int(float(max_with_dot) * 1000)
    else:
        max_match_int = re.search(r'\d+', max_txt)
        clean["boost_clock_mhz"] = int(max_match_int.group()) * 1000 if max_match_int else 0


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
    logger.info("Starting CPU extraction routine via Playwright")
    
    raw_html = fetch_rendered_html(URL_CPU)
    if not raw_html:
        logger.warning("Failed to retrieve HTML content. Exiting.")
        return
        
    cpu_list = parse_cpu_json_ld(raw_html)
    ready_cpu = []
    
    for cpu in cpu_list[:6]:
        logger.info(f"Extracted -> Price: {cpu['price']} PLN | Model: {cpu['name']}")
        url = cpu.get("url")
        if not url:
            continue
        spec = get_spec(url)
        cpu.update(spec)
        ready_cpu.append(cpu)

        time.sleep(1.5)

    logger.info(f"Successfully extracted {len(ready_cpu)} CPU products.")
    save_cpu_to_db(ready_cpu)

if __name__ == "__main__":
    main()