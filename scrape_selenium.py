import undetected_chromedriver as uc
import json
import time
import os

def fetch_with_persistence():
    print("🚀 Launching Browser with Permanent Profile...")
    
    options = uc.ChromeOptions()
    
    # CRITICAL CHANGE: Create a local folder to save your cookies/session
    # This makes you look like a returning user, not a fresh bot.
    base_dir = os.getcwd()
    profile_path = os.path.join(base_dir, "chrome_profile")
    options.user_data_dir = profile_path
    
    # Initialize driver
    driver = uc.Chrome(options=options)

    try:
        url = "https://www.immoscout24.ch/en/real-estate/rent/country-switzerland-fl"
        print(f"🌍 Navigating to: {url}")
        driver.get(url)
        
        # --- THE "HUMAN" WAITING LOOP ---
        print("\n🛑 CHECKPOINT: I will wait here until YOU get past the security check.")
        print("   -> If you see a captcha, click it.")
        print("   -> If you see a '403 Forbidden', try refreshing the page manually.")
        print("   -> Waiting for data to appear in the browser memory...\n")

        max_retries = 20
        found_data = False
        
        for i in range(max_retries):
            try:
                # Ask the browser: "Do you have the data yet?"
                # We check for the specific JSON variable ImmoScout uses
                data = driver.execute_script("return window.__INITIAL_STATE__;")
                
                if data:
                    print("✅ SUCCESS! Cloudflare let us in and data is present.")
                    
                    # Save the data
                    with open("immoscout_data.json", "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)
                    
                    print(f"📄 Data saved to 'immoscout_data.json'. Loop finishing.")
                    found_data = True
                    break
                else:
                    print(f"   ⏳ Attempt {i+1}/{max_retries}: Page loaded, but data variable is missing/null...")
            except Exception:
                # If we get an error here, it usually means the page is still loading or on the error screen
                print(f"   ⏳ Attempt {i+1}/{max_retries}: Browser is blocked or loading...")
            
            time.sleep(5) # Wait 5 seconds before checking again

        if not found_data:
            print("\n❌ TIMEOUT: Could not get the data after 100 seconds.")
            print("   Tip: Try browsing manually in this window for a bit, then run the script again.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print("👋 Closing browser (Your profile is saved in 'chrome_profile' folder)")
        driver.quit()

if __name__ == "__main__":
    fetch_with_persistence()