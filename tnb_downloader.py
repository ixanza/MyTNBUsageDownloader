import os
import configparser
from datetime import datetime
from playwright.sync_api import sync_playwright

# --- CONFIGURATION LOADING ---

# Define the name of the configuration file
CONFIG_FILE = 'config.ini'

def load_config():
    """Loads configuration and credentials from config.ini."""
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(
            f"Configuration file '{CONFIG_FILE}' not found. Please create it "
            "with [Credentials] and [Navigation] sections."
        )

    # Disable interpolation to handle '%' signs in URL-encoded strings
    config = configparser.ConfigParser(interpolation=None) 
    config.read(CONFIG_FILE)
    
    # Check for required sections/keys
    if 'Credentials' not in config or 'Navigation' not in config:
        raise ValueError(f"'{CONFIG_FILE}' must contain [Credentials] and [Navigation] sections.")
    
    # Return loaded values
    return (
        config['Credentials']['USERNAME'],
        config['Credentials']['PASSWORD'],
        config['Navigation']['ENERGY_DASHBOARD_CA_NO'],
        config['Navigation']['DOWNLOAD_DIR_PATH'] 
    )

# Load configuration and assign to constants
try:
    (
        USERNAME, 
        PASSWORD, 
        ENERGY_DASHBOARD_CA_NO, 
        DOWNLOAD_DIR_PATH
    ) = load_config()
except (FileNotFoundError, ValueError) as e:
    print(f"Configuration Error: {e}")
    exit(1)


# Path where the downloaded file will be saved
DOWNLOAD_DIR = os.path.join(os.getcwd(), DOWNLOAD_DIR_PATH)
os.makedirs(DOWNLOAD_DIR, exist_ok=True) 

# Define the expected URLs
INITIAL_PORTAL_URL = "https://www.mytnb.com.my/"
SSO_HANDLER_URL_PATTERN = "https://myaccount.mytnb.com.my/SSO/SSOHandler**"
USAGE_PAGE_URL = "https://smartliving.myaccount.mytnb.com.my/commodity/electric/usage"

# Base domains for navigation
ENERGY_DASHBOARD_DOMAIN = "https://myaccount.mytnb.com.my/AccountManagement/SmartMeter/Index/TRIL?caNo="
# -----------------------------


def automate_tnb_download():
    """Automates the login and CSV download process on the MyTNB portal."""
    
    # Generate the date stamp once for consistent filenames
    date_stamp = datetime.now().strftime("%Y%m%d")

    with sync_playwright() as p:
        print("Launching browser...")
        
        # Define a common desktop viewport size for stealth
        VIEWPORT_SIZE = {"width": 1280, "height": 720}
        browser = p.chromium.launch(headless=True) 
        
        # Create a new context with stealth settings
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport=VIEWPORT_SIZE
        )
        page = context.new_page()

        try:
            print("1. Navigating to initial portal URL.")
            page.goto(INITIAL_PORTAL_URL, timeout=60000)

            # --- POP-UP HANDLING STEP ---
            print("   Dismissing pop-up.")
            
            try:
                page.wait_for_timeout(2000) 
                page.keyboard.press('Escape')
                page.wait_for_timeout(500) 
                print("   Pop-up dismissed.")
            except Exception as e:
                print("   Error dismissing pop-up. Proceeding.")
            # ----------------------------------------------------------------------

            # --- SIMPLIFIED LOGIN FLOW (Step 2) ---
            print("2. Logging in.")
            
            page.fill('#Email', USERNAME) 
            page.fill('#Password', PASSWORD) 

            with page.expect_navigation(url=SSO_HANDLER_URL_PATTERN, timeout=60000):
                page.get_by_role("button", name="Login").click()
            
            # --- LOGIN SUCCESS CHECK ---
            print("   Waiting for Individual Dashboard URL.")
            page.wait_for_url("https://myaccount.mytnb.com.my/AccountManagement/IndividualDashboard", timeout=60000)
            
            page.wait_for_load_state('load', timeout=30000)
            actual_title = page.title()
            
            if "Individual Dashboard" in actual_title:
                print(f"   Login successful.")
            else:
                print(f"   Warning: Landed on dashboard URL but title is unexpected: '{actual_title}'")
            
            # ------------------------------------------------------------------
            
            # --- Navigation to Energy Usage Dashboard (Step 3) ---
            
            print("3. Navigating to Energy Dashboard.")
            
            # Construct the ABSOLUTE URL
            ABSOLUTE_URL = ENERGY_DASHBOARD_DOMAIN + ENERGY_DASHBOARD_CA_NO
            
            with page.expect_navigation(url="https://smartliving.myaccount.mytnb.com.my/dashboard", timeout=60000):
                 page.goto(ABSOLUTE_URL)

            # Wait for the final URL and validate the title
            page.wait_for_url("https://smartliving.myaccount.mytnb.com.my/dashboard", timeout=30000)
            page.wait_for_load_state('load', timeout=30000) 

            page_title = page.title()
            if "Energy Engage" in page_title:
                 print(f"   Navigation successful.")
            else:
                 print(f"   Warning: Landed on Energy Dashboard URL but title is unexpected: '{page_title}'")
            
            # ------------------------------------------------------------------
            
            # --- Step 4: Click 'My Energy' to trigger stable redirect ---
            print("4. Navigating to Usage Tab.")
            
            try:
                page.locator('span.my-commodity').get_by_text("My Energy").click()
            except Exception as e:
                print("   Warning: Specific locator failed. Attempting generic click and longer wait.")
                page.get_by_text("My Energy").click(timeout=15000)


            # Wait for the page to land on the specific usage page URL after the click
            page.wait_for_url(USAGE_PAGE_URL, timeout=30000) 
            
            print("   Usage Tab reached.")
            
            # --- Step 5: Monthly Download Action using ID ---
            
            print("5a. Downloading Monthly CSV.")
            
            with page.expect_download(timeout=60000) as download_info:
                page.locator('#csvdownload').click()

            # Save the Monthly file
            download_monthly = download_info.value
            monthly_filename = f"monthly_usage_{date_stamp}.csv"
            monthly_file_path = os.path.join(DOWNLOAD_DIR, monthly_filename)
            download_monthly.save_as(monthly_file_path)
            
            print(f"   Monthly Download successful: {monthly_file_path}")
            
            # --- Step 5b: Daily Download Action ---
            
            print("5b. Switching to 1 Day view and downloading Daily CSV.")
            
            # 1. Click the 1 Day span element
            page.locator('#span-zoom-1d').click()
            
            # 2. Wait for 1 second for the data/link to refresh (as requested)
            page.wait_for_timeout(1000)
            
            # 3. Trigger the download again
            with page.expect_download(timeout=60000) as download_info_daily:
                page.locator('#csvdownload').click()

            # 4. Save the Daily file
            download_daily = download_info_daily.value
            daily_filename = f"daily_usage_{date_stamp}.csv"
            daily_file_path = os.path.join(DOWNLOAD_DIR, daily_filename)
            download_daily.save_as(daily_file_path)
            
            print(f"   Daily Download successful: {daily_file_path}")
            
        except Exception as e:
            print(f"\n--- ERROR ---")
            print(f"An error occurred: {e}")
            print(f"Current URL: {page.url}")
            print("Debugging tip: Try setting 'headless=False' to visually inspect where the script stopped.")
        
        finally:
            print("Closing browser.")
            browser.close()

if __name__ == "__main__":
    automate_tnb_download()