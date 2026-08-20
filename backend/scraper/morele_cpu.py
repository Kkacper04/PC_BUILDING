import json
import logging
from typing import Dict, List, Optional

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# Configure standard Python logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

URL_CPU = "***REMOVED***"
DEFAULT_TIMEOUT_MS = 30000

def fetch_rendered_html(url: str) -> Optional[str]:
    """
    Spins up a headless Chromium instance to fetch JS-rendered HTML content.
    """
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

def parse_cpu_json_ld(html_content: str) -> List[Dict[str, str]]:
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
                    
                    products.append({"name": name, "price": price})
                
                # We found the main product list, no need to parse further scripts
                break 
                
        except json.JSONDecodeError:
            logger.debug("Failed to decode JSON block, skipping...")
            continue
            
    return products

def main():
    logger.info("Starting CPU extraction routine via Playwright")
    
    raw_html = fetch_rendered_html(URL_CPU)
    if not raw_html:
        logger.warning("Failed to retrieve HTML content. Exiting.")
        return
        
    cpu_list = parse_cpu_json_ld(raw_html)
    
    for cpu in cpu_list:
        logger.info(f"Extracted -> Price: {cpu['price']} PLN | Model: {cpu['name']}")
        
    logger.info(f"Successfully extracted {len(cpu_list)} CPU products.")

if __name__ == "__main__":
    main()