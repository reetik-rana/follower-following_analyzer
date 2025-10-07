# Instagram Follower Analyzer

A Python web app to analyze your Instagram followers and following lists using browser automation (Selenium + Chrome/Brave/Chromium).

## Features
- See who doesn't follow you back
- Modern web UI (Flask)
- Works for your own account (private/public), public accounts, and private accounts you follow

## Prerequisites
- Python 3.8+
- Google Chrome, Chromium, or Brave browser
- ChromeDriver (matching your browser version)

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/reetik-rana/follower-following_analyzer.git
cd follower-following_analyzer
```

### 2. Install Python dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Install Chrome/Chromium/Brave and ChromeDriver
- **Linux (Ubuntu):**
  ```bash
  sudo apt update
  sudo apt install -y chromium-browser chromium-chromedriver
  # OR for Chrome:
  # Download Chrome from https://www.google.com/chrome/
  # Download ChromeDriver from https://chromedriver.chromium.org/downloads
  ```
- **Windows/Mac:**
  - Download Chrome/Brave from their official sites
  - Download ChromeDriver from https://chromedriver.chromium.org/downloads
  - Place `chromedriver.exe` in your project folder or add to PATH

### 4. Configure browser path (if needed)
- In `webapp/app.py`, set the correct browser and driver paths:
  ```python
  CHROME_PATH = "/usr/bin/chromium-browser"  # or your Chrome/Brave path
  CHROMEDRIVER_PATH = "/usr/bin/chromedriver"  # or your chromedriver path
  options = Options()
  options.binary_location = CHROME_PATH
  options.add_argument("--headless=new")
  service = ChromeService(executable_path=CHROMEDRIVER_PATH)
  driver = webdriver.Chrome(service=service, options=options)
  ```

### 5. Run the app
```bash
python webapp/app.py
```
- Open your browser and go to `http://127.0.0.1:5000/`

## Troubleshooting
- Make sure ChromeDriver version matches your browser version
- If you get a browser not found error, update the paths in `app.py`
- If you see permission errors, try running with `sudo` (Linux)

## License
MIT

## Author
[reetik-rana](https://github.com/reetik-rana)
