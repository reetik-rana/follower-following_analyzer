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
    usernames = set()
    consecutive_scrolls_with_no_new_users = 0
    max_scrolls = 50
    scroll_count = 0
    while consecutive_scrolls_with_no_new_users < 3 and scroll_count < max_scrolls:
        usernames_before_scroll = len(usernames)
        try:
            current_elements = driver.find_elements(By.CSS_SELECTOR, "a[href^='/'][role='link']")
            for el in current_elements:
                href = el.get_attribute("href")
                if href:
                    username = href.split("/")[-2] if href.endswith("/") else href.split("/")[-1]
                    if username and username != 'verified':
                        usernames.add(username)
        except StaleElementReferenceException:
            continue
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
        # Shorter sleep for webapp
        import time; time.sleep(3)
        usernames_after_scroll = len(usernames)
        if usernames_after_scroll == usernames_before_scroll:
            consecutive_scrolls_with_no_new_users += 1
        else:
            consecutive_scrolls_with_no_new_users = 0
        scroll_count += 1
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
                non_followers = following_set - followers_set
                result = {
                    'total_following': len(following_set),
                    'total_followers': len(followers_set),
                    'non_followers': sorted(list(non_followers))
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
    app.run(debug=True)
