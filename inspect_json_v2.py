import json

def find_listings_v2():
    try:
        with open("immoscout_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        print("🔍 Inspecting 'resultList'...")
        
        # 1. Grab the section
        results_container = data.get('resultList', {})
        print(f"Keys inside 'resultList': {list(results_container.keys())}")
        
        # 2. Heuristic Search for the list
        # It's usually under 'search' -> 'results' OR directly under 'items'
        items = []
        
        # Scenario A: resultList -> search -> results
        if 'search' in results_container:
            search_blob = results_container['search']
            if 'results' in search_blob:
                items = search_blob['results']
                print("✅ Found items in: resultList -> search -> results")
        
        # Scenario B: resultList -> items
        elif 'items' in results_container:
            items = results_container['items']
            print("✅ Found items in: resultList -> items")
            
        # Scenario C: resultList -> list -> items
        elif 'list' in results_container:
             items = results_container['list'].get('items', [])
             print("✅ Found items in: resultList -> list -> items")

        # 3. Validation
        if items:
            print(f"📊 Count: {len(items)} listings found.")
            # Print first one to verify data
            first = items[0]
            # Try to find a title or ID
            title = first.get('title') or first.get('listing', {}).get('title') or "Unknown Title"
            price = first.get('price') or first.get('listing', {}).get('price') or "Unknown Price"
            print(f"📝 Sample Listing: {title} | {price}")
        else:
            print("⚠️ Still empty. Please copy-paste the 'Keys inside resultList' output here.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    find_listings_v2()