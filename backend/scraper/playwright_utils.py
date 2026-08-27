import logging
from typing import Optional
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_MS = 30000

def fetch_rendered_html(url: str, page=None) -> Optional[str]:
    """
    Fetches rendered HTML using Playwright.
    If a `page` object is provided, it reuses it (good for batching).
    Otherwise, it spins up a new headless chromium instance and closes it.
    """
    logger.info(f"Navigating to URL: {url}")
    
    if page:
        try:
            page.goto(url, timeout=DEFAULT_TIMEOUT_MS)
            page.wait_for_timeout(2000)
            return page.content()
        except PlaywrightTimeoutError:
            logger.error(f"Timeout while trying to load {url}")
            return None
            
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        new_page = browser.new_page()
        
        new_page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
        try:
            new_page.goto(url, timeout=DEFAULT_TIMEOUT_MS)
            new_page.wait_for_timeout(2000) 
            return new_page.content()
            
        except PlaywrightTimeoutError:
            logger.error(f"Timeout while trying to load {url}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during page load: {e}")
            return None
        finally:
            browser.close()
