from flask import Flask, render_template, request
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

app = Flask(__name__)

# --- BRAVE BROWSER SETUP ---
BRAVE_PATH = "/usr/bin/brave-browser"
DRIVER_PATH = './chromedriver'
PROFILE_PATH = os.path.join(os.getcwd(), 'brave_profile')

def scrape_list(driver, wait):
    scrollable_div_selector = "div.x1lliihq.x1iyjqo2"
    try:
        scrollable_div = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, scrollable_div_selector)))
    except TimeoutException:
        return set()
    print("Waiting for the list dialog to appear...")
    usernames = set()
    consecutive_scrolls_with_no_new_users = 0
    max_scrolls = 50
    scroll_count = 0
    import re
    def is_valid_instagram_username(u):
        return bool(re.match(r'^[a-zA-Z0-9._]{1,30}$', u))

    while consecutive_scrolls_with_no_new_users < 3 and scroll_count < max_scrolls:
        usernames_before_scroll = len(usernames)
        try:
            # Find all username spans inside user profile links in the dialog
            user_spans = driver.find_elements(By.CSS_SELECTOR, "div[role='dialog'] a.notranslate._a6hd span._ap3a")
            if not user_spans and not usernames:
                print("\n--- DEBUGGING ---")
                print("Could not find any user spans. Printing container HTML:")
                inner_html = driver.execute_script("return arguments[0].innerHTML;", scrollable_div)
                print(inner_html)
                print("--- END DEBUGGING ---\n")
                return set()
            for span in user_spans:
                username = span.text.strip().lower()
                if username and is_valid_instagram_username(username):
                    usernames.add(username)
        except StaleElementReferenceException:
            print("Stale element found, continuing...")
            continue
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
        print(f"[DEBUG] Scrolled to bottom (scroll {scroll_count+1}). Waiting for users to load...")
        import time; time.sleep(7)
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
    if scroll_count == max_scrolls:
        print("[DEBUG] Reached max scroll limit. There may be more users not loaded.")
    print(f"Reached the bottom or max scrolls. Total usernames: {len(usernames)}")
    return usernames

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        if not username:
            error = "Please enter your Instagram username."
        else:
            try:
                options = Options()
                options.binary_location = BRAVE_PATH
                options.add_argument(f"user-data-dir={PROFILE_PATH}")
                options.add_argument("--headless=new")
                service = ChromeService(executable_path=DRIVER_PATH)
                driver = webdriver.Chrome(service=service, options=options)
                wait = WebDriverWait(driver, 10)
                profile_url = f"https://www.instagram.com/{username}/"
                driver.get(profile_url)
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"a[href='/{username}/following/']"))).click()
                following_set = scrape_list(driver, wait)
                try:
                    close_btn = driver.find_element(By.CSS_SELECTOR, "div[role='dialog'] svg[aria-label='Close']")
                    close_btn.click()
                except Exception:
                    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                import time; time.sleep(1)
                wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div[role='dialog']")))
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"a[href='/{username}/followers/']"))).click()
                followers_set = scrape_list(driver, wait)
                # Normalize usernames for comparison
                following_list = sorted([u.strip().lower() for u in following_set])
                followers_list = sorted([u.strip().lower() for u in followers_set])
                # Build table rows: each row is a username in following_list, with a matching username in followers_list if present
                table_rows = []
                followers_set_lower = set(followers_list)
                for user in following_list:
                    if user in followers_set_lower:
                        table_rows.append({'following': user, 'follows_back': user})
                    else:
                        table_rows.append({'following': user, 'follows_back': ''})
                result = {
                    'total_following': len(following_list),
                    'total_followers': len(followers_list),
                    'table_rows': table_rows,
                    'followers_list': followers_list,
                    'following_list': following_list
                }
            except Exception as e:
                error = f"Error: {e}\n{traceback.format_exc()}"
            finally:
                try:
                    driver.quit()
                except Exception:
                    pass
    return render_template('index.html', result=result, error=error)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
