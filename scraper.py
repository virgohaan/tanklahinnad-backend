from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json, time

def get_prices():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        print("Avan FuelEsti...")
        driver.get("https://fuelest.ee")
        time.sleep(5)

        print("Otsin hinnaelemete...")
        rows = driver.find_elements(By.CSS_SELECTOR, "table tr")
        print(f"Leitud {len(rows)} rida")

        driver.save_screenshot("fuelest_screenshot.png")
        print("Screenshot salvestatud: fuelest_screenshot.png")

        page_text = driver.find_element(By.TAG_NAME, "body").text
        lines = [l.strip() for l in page_text.split("\n") if l.strip()]
        print("\nLehe sisu (esimesed 50 rida):")
        for line in lines[:50]:
            print(line)

    finally:
        driver.quit()

get_prices()
