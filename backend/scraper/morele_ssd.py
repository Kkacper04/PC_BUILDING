import requests 
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "***REMOVED***"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
REQUEST_DELAY = 1.5

def download_data(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)

        if response.status_code!= 200:
            print(f"Error : {response.status_code} for:  {url}")
            return None

        soup = BeautifulSoup(response.text, "lxml")
        return soup

    except requests.RequestException as e:
        print(f"Error, Not possible to download {url}: {e}")
        return None


def get_product(soup):
    products = []

    scripts_json = soup.find_all("script", type="application/ld+json")
    for script in scripts_json:
        if not script.string:
            continue
        try:
            data = json.loads(script.string)
        except json.JSONDecodeError:
            continue

        if data.get("@type") != "ItemList":
            continue

        for element in data.get("itemListElement", []):
            product = element.get("item", {})
            offer = product.get("offers",{})
            images = product.get("image",[])
            image = images[0] if images else None

            products.append({
                "name": product.get("name", "Brak nazwy"),
                "price": offer.get("price", "0"),
                "currency": offer.get("priceCurrency", "PLN"),
                "url": product.get("url", ""),
                "image": image,
            })
        break
    if not products:
        print("No product in  JSON-LD on this website.")
    return products

def scrape_categories(max_pages =2):
    all_products = []
    for page_number in range (1,max_pages +1):
        url = f"{BASE_URL}{page_number}/"
        print(f"Downloading site {page_number}: {url}")

        soup = download_data(url)
        if soup is None:
            print("downloading failure")
            break
        products = get_product(soup)
        if not products:
            print("Not available products on website")
            break

        all_products.extend(products)
        print("found {len(products)} products, total ammount : {len(all_products)}")
        if page_number < max_pages:
                time.sleep(REQUEST_DELAY)

    return all_products

def main():
    print ("SSD-SCRAPER")
    print()

    products = scrape_categories(max_pages=2)

    if not products:
        print("\nNo products found")
        return
    print()
  
    print(f"  {'#':>3}   {'CENA':>10}   Name")
   
    for i, p in enumerate(products, 1):
        price = f"{p['price']} {p['currency']}"
        print(f"  {i:>3}.  {price:>10}   {p['name']}")
    print("-" * 70)
    print(f"\n  total: {len(products)} products")
    prices = []
    for p in products:
        try:
            prices.append(float(p["price"]))
        except ValueError:
            pass
    if prices:
        print(f"  Cheapest:    {min(prices):>10.2f} PLN")
        print(f"  Most expensive:   {max(prices):>10.2f} PLN")
        print(f"  Average price: {sum(prices) / len(prices):>10.2f} PLN")
    print()

if __name__ == "__main__":
    main()
