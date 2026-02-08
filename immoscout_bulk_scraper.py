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

    # # 3. VAUD (Waadt)
    ("Vaud (Cheap)",        "https://www.immoscout24.ch/en/real-estate/rent/canton-vaud?pt=1500"),
    ("Vaud (mid)",        "https://www.immoscout24.ch/en/real-estate/rent/canton-vaud?pf=1501&pt=2000"),
    ("Vaud (Expensive)",    "https://www.immoscout24.ch/en/real-estate/rent/canton-vaud?pf=2001"),

    # # 4. GENEVA (Genf)
    ("Geneva",      "https://www.immoscout24.ch/en/real-estate/rent/canton-geneva"),

    # # 5. AARGAU
    ("Aargau (Cheap)",      "https://www.immoscout24.ch/en/real-estate/rent/canton-aargau?pt=1800"),
    ("Aargau (Expensive)",  "https://www.immoscout24.ch/en/real-estate/rent/canton-aargau?pf=1801"),

    # # 6. ST. GALLEN
    ("St. Gallen (Cheap)",     "https://www.immoscout24.ch/en/real-estate/rent/canton-st-gallen?pt=1600"),
    ("St. Gallen (Expensive)", "https://www.immoscout24.ch/en/real-estate/rent/canton-st-gallen?pf=1601"),

    # 7. TICINO (Tessin)
    ("Ticino (Cheap)",      "https://www.immoscout24.ch/en/real-estate/rent/canton-ticino?pt=1600"),
    ("Ticino (Expensive)",  "https://www.immoscout24.ch/en/real-estate/rent/canton-ticino?pf=1601"),

    # # 8. VALAIS (Wallis)
    ("Valais (Cheap)",      "https://www.immoscout24.ch/en/real-estate/rent/canton-valais?pt=1600"),
    ("Valais (Expensive)",  "https://www.immoscout24.ch/en/real-estate/rent/canton-valais?pf=1601"),

    # # 9. LUCERNE (Luzern)
    ("Luzern (Cheap)",      "https://www.immoscout24.ch/en/real-estate/rent/canton-lucerne?pt=1800"),
    ("Luzern (Expensive)",  "https://www.immoscout24.ch/en/real-estate/rent/canton-lucerne?pf=1801"),
    
    # # --- GROUP B: THE SMALLER CANTONS (Single Link) ---
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
    Extracts comprehensive data including distances, specific types, and eco-labels.
    """
    try:
        # 1. Basic ID & Link
        l_id = item.get('id', 'N/A')
        link = f"https://www.immoscout24.ch/rent/{l_id}"
        listing = item.get('listing', {})
        
        # 2. Text Content
        loc = listing.get('localization', {})
        primary_lang = loc.get('primary', 'de')
        text_data = loc.get(primary_lang, {}).get('text', {})
        
        title = text_data.get('title', 'No Title')
        # Clean description to prevent CSV breakage
        description = (text_data.get('description', '')
            .replace('\n', ' ')
            .replace('\r', '')
            .replace('\u2028', ' ')  # Replaces "Line Separator"
            .replace('\u2029', ' ')  # Replaces "Paragraph Separator"
            .replace(';', ',')
            [:1000])

        # 3. Categories (Safe access)
        cats = listing.get('categories', [])
        prop_type = cats[0] if len(cats) > 0 else 'Unknown'
        sub_type = cats[1] if len(cats) > 1 else '' 
        
        # 4. Price
        prices = listing.get('prices', {}).get('rent', {})
        price = prices.get('gross', '')
        net_price = prices.get('net', '')
        
        # 5. Address & Coordinates
        address = listing.get('address', {})
        street = address.get('street', '')
        zip_code = address.get('postalCode', '')
        city = address.get('locality', 'Unknown')
        
        coords = address.get('geoCoordinates', {})
        lat = coords.get('latitude', '')
        lon = coords.get('longitude', '')
        
        # 6. Characteristics
        chars = listing.get('characteristics', {})
        rooms = chars.get('numberOfRooms', '')
        space = chars.get('livingSpace', '')
        floor = chars.get('floor', '')
        year_built = chars.get('yearBuilt', '')
        year_renovated = chars.get('yearLastRenovated', '')
        
        # 7. Amenities (1 = Yes, 0 = No)
        def get_int(key):
            val = chars.get(key)
            return 1 if val is True else 0

        balcony = get_int('hasBalcony')
        elevator = get_int('hasElevator')
        view = get_int('hasNiceView')
        fireplace = get_int('hasFireplace')
        child_friendly = get_int('isChildFriendly')
        cable_tv = get_int('hasCableTv')
        
        # Logic: If either Garage OR Parking is true -> 1
        has_garage = chars.get('hasGarage')
        has_parking = chars.get('hasParking')
        parking = 1 if (has_garage is True or has_parking is True) else 0
        
        # 8. Building Standards
        is_new = get_int('isNewBuilding')
        minergie = get_int('isMinergieCertified') 
        wheelchair = get_int('isWheelchairAccessible')
        
        # 9. Distances (Meters)
        dist_transport = chars.get('distancePublicTransport', '')
        dist_shop = chars.get('distanceShop', '')
        dist_kindergarten = chars.get('distanceKindergarten', '')
        dist_school = chars.get('distancePrimarySchool', '')
        dist_motorway = chars.get('distanceMotorway', '')
        
        # 10. Metadata
        created_at = listing.get('meta', {}).get('createdAt', '')
        
        return [
            l_id, prop_type, sub_type, price, net_price, 
            zip_code, city, street, lat, lon,
            rooms, space, floor, year_built, year_renovated,
            balcony, elevator, parking, view, fireplace, child_friendly, cable_tv,
            is_new, minergie, wheelchair,
            dist_transport, dist_shop, dist_kindergarten, dist_school, dist_motorway,
            created_at, link, title, description 
        ]
        
    except Exception as e:
        print(f"Error parsing item {item.get('id', '?')}: {e}")
        return None

def check_for_captcha(driver):
    """
    Checks if the page is a Cloudflare/Bot challenge.
    Pauses execution and RINGS AN ALARM until the user manually solves it.
    """
    try:
        # Common indicators of a block
        page_title = driver.title.lower()
        page_source = driver.page_source.lower()
        
        # Keywords usually found on block pages
        block_keywords = ["access denied", "challenge-platform", "security check", "verify you are human"]
        
        is_blocked = any(keyword in page_title or keyword in page_source for keyword in block_keywords)
        
        if is_blocked:
            print("\n" + "!"*50)
            print("🚨 BOT DETECTION TRIGGERED! 🚨")
            print("The script has paused. Please go to the Chrome window")
            print("and solve the CAPTCHA manually.")
            print("!"*50)
            
            # --- MAKE NOISE ---
            import platform
            system_os = platform.system()
            
            # Ring 2 times to make sure you hear it
            for _ in range(2):
                if system_os == "Windows":
                    try:
                        import winsound
                        # Frequency 1000Hz, Duration 1000ms (1 second)
                        winsound.Beep(350, 1000)
                    except:
                        print('\a') # Fallback
                elif system_os == "Darwin": # Mac
                    # Text-to-Speech
                    os.system('say "Bot detection triggered. Please help."')
                else: # Linux
                    print('\a')
                
                time.sleep(1)

            # Wait for user confirmation
            input("⌨️  Press ENTER here once you have solved the captcha... ")
            print("✅ Resuming...")
            
            # Give it a moment to reload data
            time.sleep(3)
            return True
            
    except Exception as e:
        pass
    return False

def main():
    driver = init_driver()
    
    with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        headers = [
            'Region', 'ID', 'Type', 'SubType', 'Gross_Rent', 'Net_Rent',
            'Zip', 'City', 'Street', 'Lat', 'Lon',
            'Rooms', 'Area_m2', 'Floor', 'Year_Built', 'Year_Renovated',
            'Balcony', 'Elevator', 'Parking', 'View', 'Fireplace', 'Child_Friendly', 'CableTV',
            'New_Building', 'Minergie', 'Wheelchair',
            'Dist_Transport', 'Dist_Shop', 'Dist_Kindergarten', 'Dist_School', 'Dist_Motorway',
            'Date_Created', 'Link', 'Title', 'Description'
        ]
        writer.writerow(headers)

    print(f"🚀 Starting Country-Wide Scrape ({len(TARGETS)} Regions)...")
    print(f"💾 Output: {OUTPUT_FILE}")

    try:
        # --- OUTER LOOP: Go through every Canton/Region ---
        for region_name, base_url in TARGETS:
            print(f"\n--- 🌍 Starting Region: {region_name} ---")
            
            # Reset page counter for each new region
            page = 1
            
            consecutive_failures = 0  # Counter for "One Strike" fix
            MAX_FAILURES = 3          # Allow 3 empty pages before giving up on a region

            while True:
                # 1. URL Construction
                separator = "&" if "?" in base_url else "?"
                url = f"{base_url}{separator}pn={page}"
                
                print(f"   📄 Page {page}...", end="", flush=True)
                driver.get(url)
                
                # 2. BOT DETECTION CHECK
                check_for_captcha(driver)

                # 3. EXTRACTION with RETRY (Wait for Data)
                items = []
                # Try to get data for up to 10 seconds
                for attempt in range(5): 
                    items = extract_listings_from_state(driver)
                    if items: 
                        break
                    time.sleep(2) # Wait a bit for JS to load
                
                # 4. "ONE STRIKE" FIX
                if not items:
                    consecutive_failures += 1
                    print(f" ⚠️ Empty/Failed ({consecutive_failures}/{MAX_FAILURES})", end="")
                    
                    if consecutive_failures >= MAX_FAILURES:
                        print(f" ⏹️ Max failures reached. Moving to next region.")
                        break
                    else:
                        # If we failed, maybe we just need a longer pause or a refresh
                        print(" -> Retrying next page...")
                        page += 1
                        time.sleep(5)
                        continue
                else:
                    # Reset failure counter on success
                    consecutive_failures = 0
                
                # --- PROCESS ITEMS (Standard logic) ---
                saved_count = 0
                with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    for item in items:
                        row = parse_item(item)
                        if row:
                            writer.writerow([region_name] + row)
                            saved_count += 1
                
                print(f" ✅ Saved {saved_count} items.")
                
                # 5. HARD LIMIT (Page 50)
                if page >= 50:
                    print(f"   ⚠️ Hit Page 50 limit.")
                    break
                
                page += 1
                
                # 6. PACING
                time.sleep(3 + random.random() * 4) 
                if page % 10 == 0:
                    print("   ☕ Taking a break...")
                    time.sleep(20)

    except KeyboardInterrupt:
        print("\n🛑 Stopped by user.")
    finally:
        driver.quit()
        print(f"\n✅ Job Done.")

if __name__ == "__main__":
    main()
