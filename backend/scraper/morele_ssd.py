import requests 
from bs4 import BeautifulSoup
import json
import time
import re
from scraper.loader import setup_database, save_disc_to_db

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
def norm_data(data):
    convert = {}
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
    soup = download_data(url)
    if not soup:
        return {}
        
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



def main():
    print ("SSD-SCRAPER")
    print()

    setup_database()


    products = scrape_categories(max_pages=1)

    if not products:
        print("\nNo products found")
        return
    print()
  
    print("Extracting detailed specs for the first 7 products...")

    ready_to_save = []
    
   
    for i, p in enumerate(products[:7], 1):
        price = f"{p['price']} {p['currency']}"
        print(f"\n{i:>3}.  {price:>10}   {p['name']}")
        
        spec = get_spec(p['url'])
        p.update(spec)
        ready_to_save.append(p)

        print("      [Normalized specifications]:")
        for key, value in spec.items():
            print(f"        - {key}: {value}")
            
        time.sleep(REQUEST_DELAY)
    save_disc_to_db(ready_to_save)

    print("\nEND")

if __name__ == "__main__":
    main()