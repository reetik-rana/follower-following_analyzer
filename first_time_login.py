import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options

print("--- Starting Manual Login Helper ---")

# --- BRAVE BROWSER SETUP ---
BRAVE_PATH = "/usr/bin/brave-browser"
options = Options()
options.binary_location = BRAVE_PATH
options.add_argument(f"user-data-dir={os.path.join(os.getcwd(), 'brave_profile')}")

# --- DRIVER SETUP ---
DRIVER_PATH = './chromedriver'
service = ChromeService(executable_path=DRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

# --- MANUAL LOGIN ---
driver.get("https://www.instagram.com/accounts/login/")
print("\n>>> A Brave window has opened.")
print(">>> Please log in to Instagram manually in that window.")
print(">>> Make sure to click 'Save Info' if prompted.")

# This line will keep the script running and the browser open
# until you are done and press Enter here in the terminal.
input("\n>>> Press ENTER here after you have finished logging in. <<<")

driver.quit()
print("--- Login session saved. You can now run the main bot. ---")