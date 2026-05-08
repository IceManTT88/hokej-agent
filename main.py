import os
import time
import json
import hashlib
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://petrzalkasportuje.sk/events/arena-drazdiak-korculovanie/"
CHECK_INTERVAL = 300
STATE_FILE = "known_events.json"

def send_telegram(message):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": message},
        timeout=15
    )

def load_known():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except:
        return set()

def save_known(known):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(list(known), f, ensure_ascii=False, indent=2)

def make_event_id(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def fetch_relevant_events():
    r = requests.get(URL, timeout=20)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text("\n")

    blocks = []
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for i, line in enumerate(lines):
        if "Hokejka a puk" in line:
            context = lines[max(0, i-5): i+8]
            block = "\n".join(context)

            # filter max 20 ľudí / kapacita 20
            if "20" in block:
                blocks.append(block)

    return blocks

def main():
    if not BOT_TOKEN or not CHAT_ID:
        print("Missing BOT_TOKEN or CHAT_ID")
        return

    known = load_known()
    print("Agent beží - anti-spam verzia")

    while True:
        try:
            events = fetch_relevant_events()

            if not events:
                print("Kontrola OK - nič nové")
            else:
                for event in events:
                    event_id = make_event_id(event)

                    if event_id not in known:
                        known.add(event_id)
                        save_known(known)

                        msg = (
                            "🏒 Nový termín Hokejka a puk!\n\n"
                            f"{event}\n\n"
                            f"{URL}"
                        )

                        send_telegram(msg)
                        print("Poslaná nová notifikácia")
                    else:
                        print("Už známy termín - neposielam")

        except Exception as e:
            print("Chyba:", e)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()