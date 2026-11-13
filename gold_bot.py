import requests, json, os, re
from datetime import datetime, timezone, timedelta

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
URL = "https://publicgold.com.my"
FILE = "last_price.json"

def get_price():
    html = requests.get(URL, timeout=20,
                        headers={"User-Agent": "Mozilla/5.0"}).text
    m = re.search(r"RM\s*(\d+(?:\.\d+)?)\s*=\s*1\.0000\s*gram", html)
    return float(m.group(1))

# Malaysia time (UTC+8)
now = datetime.now(timezone(timedelta(hours=8)))
today = f"{now.day} {now:%b %Y}"
ampm = "am" if now.hour < 12 else "pm"
stamp = f"{today} @ {now.hour % 12 or 12}:{now:%M} {ampm}"

price = get_price()
data = json.load(open(FILE)) if os.path.exists(FILE) else {}
last = data.get("p")

if price != last:
    if data.get("low") is None or price < data["low"]:
        data["low"], data["low_date"] = price, today
    if data.get("high") is None or price > data["high"]:
        data["high"], data["high_date"] = price, today

    lines = [
        "Public Gold GAP",
        f"RM 100 = {100 / price:.4f} gram",
        f"RM {price:g} = 1.0000 gram",
        "",
    ]
    if last is not None:
        diff = price - last
        arrow = "🔼" if diff > 0 else "🔽"
        lines += [f"Harga GAP {arrow} RM {abs(diff):g}", ""]
    lines += [
        f"Terendah: RM {data['low']:g} ({data['low_date']})",
        f"Tertinggi: RM {data['high']:g} ({data['high_date']})",
        "",
        f"Dikemaskini: {stamp}",
    ]

    r = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": "\n".join(lines)})
    r.raise_for_status()
    data["p"] = price
    json.dump(data, open(FILE, "w"))
