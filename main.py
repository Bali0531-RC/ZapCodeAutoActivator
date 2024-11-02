import requests
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchWindowException

# Configuration Constants
COUPON_FILE = 'coupons.txt'      # File containing coupon codes, one per line
ACTIVATION_URL = 'https://zap-hosting.com/en/customer/home/cashbox/'  # Activation endpoint
LOGIN_URL = 'https://zap-hosting.com/en/#login'  # Login URL
RATE_LIMIT_SECONDS = 30           # Delay between activations per account
PROXY_URL = 'http://username:password@0.0.0.0:8080'  # Proxy to use for all requests

# Setup Logging
logging.basicConfig(
    filename='coupon_activation.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_coupons(file_path: str):
    """Load coupon codes from a text file."""
    try:
        with open(file_path, 'r') as file:
            coupons = [line.strip() for line in file if line.strip()]
        logging.info(f"Loaded {len(coupons)} coupons from {file_path}.")
        return coupons
    except FileNotFoundError:
        logging.error(f"Coupons file {file_path} not found.")
        return []

def start_browser_and_login():
    """Open Chrome without proxy, prompt login, and capture cookies."""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--incognito")  # Use incognito mode

    # Start a browser session without proxy
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Open the login page
    driver.get(LOGIN_URL)
    print("Please log in to the site manually...")
    
    # Wait for the user to complete the CAPTCHA and login
    input("Press Enter after completing CAPTCHA and logging in to continue...")

    return driver

def get_cookies_from_driver(driver):
    """Retrieve cookies from an open Chrome driver session."""
    try:
        # Retrieve cookies after login
        cookies = driver.get_cookies()
        # Convert cookies to a dictionary format expected by requests
        session_cookies = {cookie['name']: cookie['value'] for cookie in cookies}
        return session_cookies
    except NoSuchWindowException:
        print("The browser window was closed before cookies could be retrieved.")
        return {}

def activate_coupon(coupon_code: str, zap_session: str, cookies: dict):
    """Activate a single coupon code with retry logic using the captured cookies and proxy."""
    data = {
        'code': coupon_code,
        'addCoupon': ''
    }
    attempt = 0
    success = False
    
    while attempt < 3 and not success:
        attempt += 1
        session = requests.Session()
        # Apply proxy only for requests
        session.proxies.update({
            "http": PROXY_URL,
            "https": PROXY_URL
        })
        session.cookies.update(cookies)
        session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        })
        
        try:
            response = session.post(ACTIVATION_URL, data=data, timeout=30)
            if response.status_code == 200:
                if "Coupon successfully applied" in response.text:
                    logging.info(f"[{zap_session}] SUCCESS: Activated coupon {coupon_code}.")
                    print(f"[{zap_session}] SUCCESS: Activated coupon {coupon_code}.")
                    success = True
                else:
                    logging.warning(f"[{zap_session}] INFO: Response received for coupon {coupon_code}. Check manually.")
                    print(f"[{zap_session}] INFO: Response received for coupon {coupon_code}. Check manually.")
                    success = True  # Consider non-critical errors as successful attempts
            else:
                logging.error(f"[{zap_session}] ERROR: Failed to activate coupon {coupon_code}. Status Code: {response.status_code}")
                print(f"[{zap_session}] ERROR: Failed to activate coupon {coupon_code}. Status Code: {response.status_code}")
        except requests.RequestException as e:
            logging.exception(f"[{zap_session}] EXCEPTION: Error activating coupon {coupon_code}: {e}")
            print(f"[{zap_session}] EXCEPTION: Error activating coupon {coupon_code}: {e}")

        if not success:
            print(f"[{zap_session}] Retrying activation for coupon {coupon_code} (Attempt {attempt}/3)")
            time.sleep(RATE_LIMIT_SECONDS)

    if not success:
        logging.error(f"[{zap_session}] FAILED: Skipping coupon {coupon_code} after 3 unsuccessful attempts.")
        print(f"[{zap_session}] FAILED: Skipping coupon {coupon_code} after 3 unsuccessful attempts.")

def process_account(coupons: list, cookies: dict):
    """Process coupon activations using the captured cookies."""
    zap_session = cookies.get("zap_session", "UnknownSession")

    logging.info(f"[{zap_session}] Starting coupon activations.")
    print(f"[{zap_session}] Starting coupon activations.")

    for idx, coupon in enumerate(coupons, start=1):
        print(f"[{zap_session}] Activating coupon {idx}/{len(coupons)}: {coupon}")
        activate_coupon(coupon, zap_session, cookies)
        if idx < len(coupons):
            print(f"[{zap_session}] Waiting for {RATE_LIMIT_SECONDS} seconds to respect rate limit...")
            time.sleep(RATE_LIMIT_SECONDS)

    logging.info(f"[{zap_session}] Completed all coupon activations.")
    print(f"[{zap_session}] Completed all coupon activations.")

def main():
    # Load coupons
    coupons = load_coupons(COUPON_FILE)
    if not coupons:
        print("No coupons to process. Exiting.")
        return

    # Process multiple accounts by prompting for new login after each account
    while True:
        # Start browser and prompt for login, keeping browser open
        driver = start_browser_and_login()
        cookies = get_cookies_from_driver(driver)
        if not cookies:
            print("Failed to retrieve cookies. Exiting.")
            driver.quit()
            break

        # Process coupon activations with captured cookies
        process_account(coupons, cookies)

        # Close browser only after all activations are complete
        driver.quit()

        # Prompt to log in to a new account if needed
        repeat = input("Would you like to log in to another account and continue? (y/n): ").strip().lower()
        if repeat != 'y':
            break

    print("\nAll accounts have been processed.")
    logging.info("All accounts have been processed.")

if __name__ == "__main__":
    main()
