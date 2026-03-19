from flask import Flask, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time, re, threading, os

app = Flask(__name__)
CORS(app)

cache = {"data": None, "updated": 0}
CACHE_TTL = 1800

BRANDS = ["Krooning","Alexela","Circle K","Neste","Olerex","JetOil","Terminal Oil","Hepa","GO Oil","Saare Kütus","Premium 7","Eesti Gaas","Texor","Moora R-Jaamad","JetGas OÜ","Levax JK OÜ","Eksar-Transoil","Anna Kütus","OBB Kaubanduse OÜ"]

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36")

    chrome_bin = os.environ.get("GOOGLE_CHROME_BIN") or os.environ.get("CHROME_BIN")
    chromedriver_path = os.environ.get("CHROMEDRIVER_PATH")

    if chrome_bin:
        options.binary_location = chrome_bin

    if chromedriver_path:
        service = Service(chromedriver_path)
    else:
        service = Service(ChromeDriverManager().install())

    return webdriver.Chrome(service=service, options=options)

def parse_row(text):
    parts = te
cat > ~/tanklahinnad-backend/app.py << 'PYEOF'
from flask import Flask, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time, re, threading, os

app = Flask(__name__)
CORS(app)

cache = {"data": None, "updated": 0}
CACHE_TTL = 1800

BRANDS = ["Krooning","Alexela","Circle K","Neste","Olerex","JetOil","Terminal Oil","Hepa","GO Oil","Saare Kütus","Premium 7","Eesti Gaas","Texor","Moora R-Jaamad","JetGas OÜ","Levax JK OÜ","Eksar-Transoil","Anna Kütus","OBB Kaubanduse OÜ"]

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36")

    chrome_bin = os.environ.get("GOOGLE_CHROME_BIN") or os.environ.get("CHROME_BIN")
    chromedriver_path = os.environ.get("CHROMEDRIVER_PATH")

    if chrome_bin:
        options.binary_location = chrome_bin

    if chromedriver_path:
        service = Service(chromedriver_path)
    else:
        service = Service(ChromeDriverManager().install())

    return webdriver.Chrome(service=service, options=options)

def parse_row(text):
    parts = text.split()
    prices = {"95": None, "98": None, "D": None, "CNG": None, "LPG": None}
    keys = ["95", "98", "D", "CNG", "LPG"]
    idx = 0
    for p in parts:
        if idx >= 5: break
        try:
            v = float(p)
            if 0.4 < v < 5.0:
                prices[keys[idx]] = v
        except:
            pass
        idx += 1
    return prices

def scrape_fuelest():
    driver = get_driver()
    try:
        driver.get("https://fuelest.ee/?fuelTypeId=6&countryId=1")
        time.sleep(12)
        page = driver.find_element(By.TAG_NAME, "body").text
        lines = [l.strip() for l in page.split("\n") if l.strip()]

        start = None
        for i, l in enumerate(lines):
            if "Tanklakett" in l:
                start = i + 1
                break

        if start is None:
            return []

        stations = []
        for i, brand in enumerate(BRANDS):
            if start + i >= len(lines):
                break
            row = lines[start + i]
            if row in ["-", "", "- - - - -"]:
                continue

            name_in_row = None
            for b in BRANDS:
                if row.startswith(b):
                    name_in_row = b
                    row = row[len(b):].strip()
                    break

            prices = parse_row(row)
            has_price = any(v is not None for v in prices.values())
            if has_price:
                stations.append({
                    "name": name_in_row or brand,
                    "brand": (name_in_row or brand).split()[0],
                    "prices": prices
                })

        return stations
    finally:
        driver.quit()

def refresh_cache():
    print("Uuendan hindasid...")
    try:
        data = scrape_fuelest()
        cache["data"] = data
        cache["updated"] = time.time()
        print(f"Uuendatud — {len(data)} tanklat")
    except Exception as e:
        print(f"Viga: {e}")
        import traceback; traceback.print_exc()

@app.route("/api/stations")
def get_stations():
    if not cache["data"] or time.time() - cache["updated"] > CACHE_TTL:
        refresh_cache()
    return jsonify({
        "stations": cache["data"] or [],
        "updated": cache["updated"],
        "count": len(cache["data"]) if cache["data"] else 0
    })

@app.route("/health")
def health():
    return jsonify({"status": "ok", "cached": cache["updated"] > 0})

if __name__ == "__main__":
    threading.Thread(target=refresh_cache).start()
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)
