import json

def find_listings():
    try:
        with open("immoscout_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        print("🔍 Scanning JSON structure...")
        
        # 1. Try to find the common path for ImmoScout data
        # Usually: state -> resultList -> list -> items
        try:
            # Note: The key names might differ slightly (e.g. 'props', 'pageProps')
            # Look at the top level keys first
            print(f"Top Level Keys: {list(data.keys())}")
            
            # Let's try to dig down based on standard Redux/Vue structures
            # Modify these keys if your output shows something different!
            
            # PATH A: The standard "Redux" path
            if 'state' in data:
                items = data['state'].get('resultList', {}).get('list', {}).get('items', [])
                if items:
                    print(f"✅ FOUND MATCH (Path A): {len(items)} listings found.")
                    print("Sample Item Title:", items[0].get('title', 'No Title'))
                    return

            # PATH B: The "Props" path (Next.js style)
            if 'props' in data:
                listings = data['props'].get('pageProps', {}).get('initialState', {}).get('resultList', {}).get('list', {}).get('items', [])
                if listings:
                    print(f"✅ FOUND MATCH (Path B): {len(listings)} listings found.")
                    return

            print("⚠️ Could not auto-detect the list. Please check the 'Top Level Keys' above.")
            
        except Exception as e:
            print(f"Error digging into JSON: {e}")

    except FileNotFoundError:
        print("❌ immoscout_data.json not found. Make sure it's in the same folder.")

if __name__ == "__main__":
    find_listings()