from flask import Flask, jsonify
from flask_cors import CORS
from playwright.sync_api import sync_playwright
import time, threading, os

app = Flask(__name__)
CORS(app)

cache = {"data": None, "updated": 0}
CACHE_TTL = 1800

BRANDS = ["Krooning","Alexela","Circle K","Neste","Olerex","JetOil","Terminal Oil","Hepa","GO Oil","Saare Kutus","Premium 7","Eesti Gaas","Texor","Levax JK OU","Eksar-Transoil","Anna Kutus","OBB Kaubanduse OU"]

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
    chrome_bin = os.environ.get("CHROME_BIN", "/usr/bin/chromium")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=chrome_bin, args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu"])
        page = browser.new_page()
        page.goto("https://fuelest.ee/?fuelTypeId=6&countryId=1")
        page.wait_for_timeout(12000)
        content = page.inner_text("body")
        browser.close()
    lines = [l.strip() for l in content.split("\n") if l.strip()]
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
        if any(v is not None for v in prices.values()):
            stations.append({"name": name_in_row or brand, "brand": (name_in_row or brand).split()[0], "prices": prices})
    return stations

def refresh_cache():
    print("Uuendan hindasid...")
    try:
        data = scrape_fuelest()
        cache["data"] = data
        cache["updated"] = time.time()
        print("Uuendatud - " + str(len(data)) + " tanklat")
    except Exception as e:
        print("Viga: " + str(e))
        import traceback; traceback.print_exc()

@app.route("/api/stations")
def get_stations():
    if not cache["data"] or time.time() - cache["updated"] > CACHE_TTL:
        refresh_cache()
    return jsonify({"stations": cache["data"] or [], "updated": cache["updated"], "count": len(cache["data"]) if cache["data"] else 0})

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    threading.Thread(target=refresh_cache).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
