import requests, json, os, re

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
URL = "https://publicgold.com.my"
FILE = "last_price.json"

def get_price():
    html = requests.get(URL, timeout=20,
                        headers={"User-Agent": "Mozilla/5.0"}).text
    m = re.search(r"RM\s*(\d+(?:\.\d+)?)\s*=\s*1\.0000\s*gram", html)
    return float(m.group(1))

price = get_price()
last = json.load(open(FILE))["p"] if os.path.exists(FILE) else None

if price != last:
    diff = price - last if last is not None else 0
    arrow = "🔼" if diff > 0 else "🔽"
    r = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID,
              "text": f"{arrow} Public Gold GAP: RM{price:g}/g ({diff:+g})"})
    r.raise_for_status()
    json.dump({"p": price}, open(FILE, "w"))
