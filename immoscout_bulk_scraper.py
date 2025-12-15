import undetected_chromedriver as uc
import json
import time
import os
import csv
import random

# --- CONFIGURATION ---
OUTPUT_FILE = "all_listings.csv"

# "Big" cantons are split by price ranges to keep results under 1000 items (50 pages).
TARGETS = [
    # --- GROUP A: THE BIG CANTONS (Split by Price) ---
    
    # 1. ZÜRICH (Very large, needs 3 splits)
    ("Zürich (Cheap)",      "https://www.immoscout24.ch/en/real-estate/rent/canton-zurich?pt=2000"),
    ("Zürich (Mid)",        "https://www.immoscout24.ch/en/real-estate/rent/canton-zurich?pf=2001&pt=2800"),
    ("Zürich (Mid+)",        "https://www.immoscout24.ch/en/real-estate/rent/canton-zurich?pf=2801&pt=3500"),
    ("Zürich (Expensive)",  "https://www.immoscout24.ch/en/real-estate/rent/canton-zurich?pf=3501"),

    # 2. BERN
    ("Bern (Cheap)",        "https://www.immoscout24.ch/en/real-estate/rent/canton-bern?pt=1300"),
    ("Bern (mid)",        "https://www.immoscout24.ch/en/real-estate/rent/canton-bern?pf=1301&pt=1600"),
    ("Bern (Expensive)",    "https://www.immoscout24.ch/en/real-estate/rent/canton-bern?pf=1601"),

    # 3. VAUD (Waadt)
    ("Vaud (Cheap)",        "https://www.immoscout24.ch/en/real-estate/rent/canton-vaud?pt=1500"),
    ("Vaud (mid)",        "https://www.immoscout24.ch/en/real-estate/rent/canton-vaud?pf=1501&pt=2000"),
    ("Vaud (Expensive)",    "https://www.immoscout24.ch/en/real-estate/rent/canton-vaud?pf=2001"),

    # 4. GENEVA (Genf)
    ("Geneva",      "https://www.immoscout24.ch/en/real-estate/rent/canton-geneva"),

    # 5. AARGAU
    ("Aargau (Cheap)",      "https://www.immoscout24.ch/en/real-estate/rent/canton-aargau?pt=1800"),
    ("Aargau (Expensive)",  "https://www.immoscout24.ch/en/real-estate/rent/canton-aargau?pf=1801"),

    # 6. ST. GALLEN
    ("St. Gallen (Cheap)",     "https://www.immoscout24.ch/en/real-estate/rent/canton-st-gallen?pt=1600"),
    ("St. Gallen (Expensive)", "https://www.immoscout24.ch/en/real-estate/rent/canton-st-gallen?pf=1601"),

    # 7. TICINO (Tessin)
    ("Ticino (Cheap)",      "https://www.immoscout24.ch/en/real-estate/rent/canton-ticino?pt=1600"),
    ("Ticino (Expensive)",  "https://www.immoscout24.ch/en/real-estate/rent/canton-ticino?pf=1601"),

    # 8. VALAIS (Wallis)
    ("Valais (Cheap)",      "https://www.immoscout24.ch/en/real-estate/rent/canton-valais?pt=1600"),
    ("Valais (Expensive)",  "https://www.immoscout24.ch/en/real-estate/rent/canton-valais?pf=1601"),

    # 9. LUCERNE (Luzern)
    ("Luzern (Cheap)",      "https://www.immoscout24.ch/en/real-estate/rent/canton-lucerne?pt=1800"),
    ("Luzern (Expensive)",  "https://www.immoscout24.ch/en/real-estate/rent/canton-lucerne?pf=1801"),
    
    # --- GROUP B: THE SMALLER CANTONS (Single Link) ---
    ("Basel-Stadt",         "https://www.immoscout24.ch/en/real-estate/rent/canton-basel-stadt"),
    ("Basel-Landschaft",    "https://www.immoscout24.ch/en/real-estate/rent/canton-basel-landschaft"),
    ("Solothurn",           "https://www.immoscout24.ch/en/real-estate/rent/canton-solothurn"),
    ("Fribourg",            "https://www.immoscout24.ch/en/real-estate/rent/canton-fribourg"),
    ("Thurgau",             "https://www.immoscout24.ch/en/real-estate/rent/canton-thurgau"),
    ("Graubünden",          "https://www.immoscout24.ch/en/real-estate/rent/canton-graubuenden"),
    ("Neuchâtel",           "https://www.immoscout24.ch/en/real-estate/rent/canton-neuchatel"),
    ("Schwyz",              "https://www.immoscout24.ch/en/real-estate/rent/canton-schwyz"),
    ("Zug",                 "https://www.immoscout24.ch/en/real-estate/rent/canton-zug"),
    ("Schaffhausen",        "https://www.immoscout24.ch/en/real-estate/rent/canton-schaffhausen"),
    ("Jura",                "https://www.immoscout24.ch/en/real-estate/rent/canton-jura"),
    ("Appenzell AR",        "https://www.immoscout24.ch/en/real-estate/rent/canton-appenzell-ausserrhoden"),
    ("Appenzell AI",        "https://www.immoscout24.ch/en/real-estate/rent/canton-appenzell-innerrhoden"),
    ("Nidwalden",           "https://www.immoscout24.ch/en/real-estate/rent/canton-nidwalden"),
    ("Obwalden",            "https://www.immoscout24.ch/en/real-estate/rent/canton-obwalden"),
    ("Glarus",              "https://www.immoscout24.ch/en/real-estate/rent/canton-glarus"),
    ("Uri",                 "https://www.immoscout24.ch/en/real-estate/rent/canton-uri"),
]

def init_driver():
    options = uc.ChromeOptions()
    options.add_argument('--lang=en-US')
    
    # Use your persistent profile to avoid 403 blocks
    base_dir = os.getcwd()
    profile_path = os.path.join(base_dir, "chrome_profile")
    options.user_data_dir = profile_path
    
    driver = uc.Chrome(options=options)
    return driver

def extract_listings_from_state(driver):
    """
    Extracts the list of items from the window.__INITIAL_STATE__ variable.
    """
    try:
        # Get the raw JSON blob from the browser
        data = driver.execute_script("return window.__INITIAL_STATE__;")
        if not data: return []
        
        # Path: resultList -> search -> fullSearch -> result -> listings
        try:
            return data['resultList']['search']['fullSearch']['result']['listings']
        except (KeyError, TypeError):
            return []
            
    except Exception as e:
        print(f"   ⚠️ Extraction Error: {e}")
        return []

def parse_item(item):
    """
    Extracts clean fields from the raw JSON item.
    """
    try:
        # 1. ID
        l_id = item.get('id', 'N/A')
        
        # 2. Navigate to the main 'listing' object
        listing = item.get('listing', {})
        
        # 3. Title (Logic: Try 'de' text, fallback to any other)
        title = "No Title"
        loc = listing.get('localization', {})
        primary_lang = loc.get('primary', 'de')
        
        if primary_lang in loc:
            title = loc[primary_lang].get('text', {}).get('title', 'No Title')
        
        # 4. Price
        prices = listing.get('prices', {}).get('rent', {})
        price = prices.get('gross', 'On Request')
        
        # 5. Address / City
        address = listing.get('address', {})
        city = address.get('locality', 'Unknown')
        zip_code = address.get('postalCode', '')
        
        # 6. Details
        chars = listing.get('characteristics', {})
        rooms = chars.get('numberOfRooms', 'N/A')
        space = chars.get('livingSpace', 'N/A')
        
        # 7. Construct Link
        link = f"https://www.immoscout24.ch/rent/{l_id}"
        
        return [l_id, title, price, f"{zip_code} {city}", rooms, space, link]
        
    except Exception as e:
        print(f"Error parsing item {item.get('id')}: {e}")
        return None

def main():
    driver = init_driver()
    
    # Initialize CSV file with headers
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Region', 'ID', 'Title', 'Price', 'Location', 'Rooms', 'Space', 'Link'])

    print(f"🚀 Starting Country-Wide Scrape ({len(TARGETS)} Regions)...")
    print(f"💾 Output: {OUTPUT_FILE}")

    try:
        # --- OUTER LOOP: Go through every Canton/Region ---
        for region_name, base_url in TARGETS:
            print(f"\n--- 🌍 Starting Region: {region_name} ---")
            
            # Reset page counter for each new region
            page = 1
            
            while True:
                # Add pagination parameter to the URL
                # If URL already has '?', we add '&pn=', otherwise '?pn='
                separator = "&" if "?" in base_url else "?"
                url = f"{base_url}{separator}pn={page}"
                
                print(f"   📄 Page {page}...", end="", flush=True)
                driver.get(url)
                
                # --- RETRY LOGIC (Wait for Data) ---
                items = []
                for _ in range(10):
                    items = extract_listings_from_state(driver)
                    if items: break
                    time.sleep(1)
                
                if not items:
                    print(" ⏹️ No more items (End of Region).")
                    break 
                
                # --- PROCESS ITEMS ---
                saved_count = 0
                with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    for item in items:
                        row = parse_item(item)
                        if row:
                            # Prepend the Region Name to the row
                            writer.writerow([region_name] + row)
                            saved_count += 1
                
                print(f" ✅ Saved {saved_count} items.")
                
                # Stop if we hit the hard limit (Page 50)
                if page >= 50:
                    print(f"   ⚠️ WARNING: Hit Page 50 limit for {region_name}. Some data might be missing.")
                    break
                
                page += 1
                # New: "Human" Pacing
                # 1. Standard wait between pages (5 to 10 seconds is safer than 2)
                time.sleep(5 + random.random() * 5) 

                # 2. Every 10 pages, take a "Coffee Break" (30-60 seconds)
                if page % 10 == 0:
                    print("   ☕ Taking a short break...")
                    time.sleep(30 + random.random() * 30)

    except KeyboardInterrupt:
        print("\n🛑 Stopped by user.")
    finally:
        driver.quit()
        print(f"\n✅ Job Done.")

if __name__ == "__main__":
    main()
