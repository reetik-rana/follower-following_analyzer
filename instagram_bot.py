
import time
import os
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.keys import Keys

# --- CONFIGURATION ---
TARGET_USERNAME = "reetikrana"

# --- BRAVE BROWSER SETUP ---
BRAVE_PATH = "/usr/bin/brave-browser"
options = Options()
options.binary_location = BRAVE_PATH
options.add_argument(f"user-data-dir={os.path.join(os.getcwd(), 'brave_profile')}")

# --- DRIVER SETUP ---
DRIVER_PATH = './chromedriver'
service = ChromeService(executable_path=DRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)

def scrape_list():
    """Scrolls through a dialog and scrapes usernames."""
    print("Waiting for the list dialog to appear...")
    scrollable_div_selector = "div.x1lliihq.x1iyjqo2"  # Updated selector for scrollable container
    
    try:
        scrollable_div = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, scrollable_div_selector)))
    except TimeoutException:
        print("ERROR: Could not find the scrollable list container. The page structure may have changed.")
        return set()

    print("Dialog appeared. Starting to scrape...")
    usernames = set()
    
    # --- THIS IS THE FIX ---
    # New, more reliable logic to check for the end of the list
    consecutive_scrolls_with_no_new_users = 0
    

    max_scrolls = 50  # Prevent infinite loops
    scroll_count = 0
    while consecutive_scrolls_with_no_new_users < 3 and scroll_count < max_scrolls:
        usernames_before_scroll = len(usernames)
        try:
            # Find all <a> tags that look like profile links
            current_elements = driver.find_elements(By.CSS_SELECTOR, "a[href^='/'][role='link']")
            if not current_elements and not usernames:
                print("\n--- DEBUGGING ---")
                print("Could not find any usernames with the selector a[href^='/'][role='link']. Printing container HTML:")
                inner_html = driver.execute_script("return arguments[0].innerHTML;", scrollable_div)
                print(inner_html)
                print("--- END DEBUGGING ---\n")
                return set() # Exit if we can't find anything from the start
            # Extract username from href (e.g., /username/)
            for el in current_elements:
                href = el.get_attribute("href")
                if href:
                    username = href.split("/")[-2] if href.endswith("/") else href.split("/")[-1]
                    if username and username != 'verified':
                        usernames.add(username)
        except StaleElementReferenceException:
            print("Stale element found, continuing...")
            continue
        # Scroll to bottom and wait longer for new users to load
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
        print(f"[DEBUG] Scrolled to bottom (scroll {scroll_count+1}). Waiting for users to load...")
        time.sleep(7)  # Increased wait to allow for slow network/user loading
        usernames_after_scroll = len(usernames)
        print(f"Scraped {len(usernames)} usernames so far...")
        if usernames_after_scroll == usernames_before_scroll:
            consecutive_scrolls_with_no_new_users += 1
            print(f"[DEBUG] No new users found after scroll. ({consecutive_scrolls_with_no_new_users}/3)")
        else:
            consecutive_scrolls_with_no_new_users = 0
        scroll_count += 1
    if scroll_count == max_scrolls:
        print("[DEBUG] Reached max scroll limit. There may be more users not loaded.")

    print(f"Reached the bottom or max scrolls. Total usernames: {len(usernames)}")
    return usernames

# --- MAIN SCRIPT ---
# [The main script logic remains exactly the same]
print("🚀 Starting the Instagram bot...")
followers_set = set()
following_set = set()
try:
    profile_url = f"https://www.instagram.com/{TARGET_USERNAME}/"
    driver.get(profile_url)
    print(f"Navigated to {TARGET_USERNAME}'s profile.")

    print("[DEBUG] Attempting to open 'Following' dialog...")
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"a[href='/{TARGET_USERNAME}/following/']"))).click()
    print("[DEBUG] 'Following' dialog opened. Scraping...")
    following_set = scrape_list()

    print("[DEBUG] Finished scraping 'Following'. Closing dialog...")
    # Try to close the dialog by clicking the close button (X)
    try:
        close_btn = driver.find_element(By.CSS_SELECTOR, "div[role='dialog'] svg[aria-label='Close']")
        close_btn.click()
        print("[DEBUG] Clicked close button on dialog.")
    except Exception as e:
        print(f"[DEBUG] Could not click close button: {e}. Trying ESC key...")
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
    time.sleep(1)
    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div[role='dialog']")))
    print("✅ 'Following' dialog closed.")

    print("[DEBUG] Attempting to open 'Followers' dialog...")
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"a[href='/{TARGET_USERNAME}/followers/']"))).click()
    print("[DEBUG] 'Followers' dialog opened. Scraping...")
    followers_set = scrape_list()
    print("[DEBUG] Finished scraping 'Followers'.")

    # Analyze and Print Results
    print("\n--- ANALYSIS COMPLETE ---")
    non_followers = following_set - followers_set
    print(f"Total Following: {len(following_set)}")
    print(f"Total Followers: {len(followers_set)}")
    print(f"Doesn't Follow You Back: {len(non_followers)}")
    print("-------------------------")
    if non_followers:
        print("Accounts that don't follow you back:")
        for user in sorted(list(non_followers)):
            print(user)
    else:
        print("Everyone you follow also follows you back!")
except Exception as e:
    print(f"An error occurred: {e}")
    print("[TRACEBACK]")
    traceback.print_exc()
finally:
    input("\n--- Script finished. Press Enter to close the browser. ---")
    driver.quit()