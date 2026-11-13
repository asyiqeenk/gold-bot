import requests, json, os, re, html as ihtml
from datetime import datetime, timezone, timedelta

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
URL = "https://publicgold.com.my"
FILE = "last_jewel.json"
NUM = r"(\d[\d,]*(?:\.\d+)?)"

def page_text():
    raw = requests.get(URL, timeout=20,
                       headers={"User-Agent": "Mozilla/5.0"}).text
    raw = re.sub(r"(?is)<(script|style).*?</\1>", " ", raw)
    text = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", ihtml.unescape(text))

def num(s):
    return float(s.replace(",", ""))

def send(text):
    for cid in CHAT_ID.split(","):
        r = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": cid.strip(), "text": text})
        r.raise_for_status()

t = page_text()
j = re.search(r"PG JEWEL.*?\b999\s+" + NUM + r"\s+" + NUM +
              r"\s+916\s+" + NUM + r"\s+" + NUM, t, re.I)
n = re.search(r"NON-PG GOLD BUYBACK.*?\b999\s+" + NUM +
              r"\s+916\s+" + NUM, t, re.I)
if not (j and n):
    i = t.lower().find("pg jewel")
    raise SystemExit("Table not found. Text near PG JEWEL: " + t[i:i + 400])

keys = ["j999_sell", "j999_buy", "j916_sell", "j916_buy", "n999", "n916"]
p = dict(zip(keys, [num(x) for x in j.groups() + n.groups()]))
jewel_keys = keys[:4]
non_keys = keys[4:]

state = json.load(open(FILE)) if os.path.exists(FILE) else {}

# Malaysia time (UTC+8)
now = datetime.now(timezone(timedelta(hours=8)))
ampm = "am" if now.hour < 12 else "pm"
stamp = f"{now.day} {now:%b %Y} @ {now.hour % 12 or 12}:{now:%M} {ampm}"

if any(p[k] != state.get(k) for k in jewel_keys):
    send("\n".join([
        "💍 Harga Emas PG Jewel",
        "",
        "Harga barang kemas PG Jewel baru sahaja dikemaskini.",
        "",
        "🏷️ PG Jewel (Sell)",
        f"🪙 Emas 999 = RM {p['j999_sell']:g}",
        f"🪙 Emas 916 = RM {p['j916_sell']:g}",
        "",
        "💵 PG Jewel (Buy)",
        f"🪙 Emas 999 = RM {p['j999_buy']:g}",
        f"🪙 Emas 916 = RM {p['j916_buy']:g}",
        "",
        f"🕒 Dikemaskini: {stamp}",
    ]))
    state.update({k: p[k] for k in jewel_keys})
    json.dump(state, open(FILE, "w"))

if any(p[k] != state.get(k) for k in non_keys):
    send("\n".join([
        "✨ Harga Buyback Non-PG Gold",
        "",
        "Harga beli balik emas Non-PG baru sahaja dikemaskini.",
        "",
        f"🪙 Emas 999 = RM {p['n999']:g}",
        f"🪙 Emas 916 = RM {p['n916']:g}",
        "",
        f"🕒 Dikemaskini: {stamp}",
    ]))
    state.update({k: p[k] for k in non_keys})
    json.dump(state, open(FILE, "w"))
