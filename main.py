import os
import time
import re
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

AJAX_URL = "https://petrzalkasportuje.sk/wp-admin/admin-ajax.php"
EVENT_ID = "10024"

CHECK_INTERVAL = 300
DAYS_AHEAD = 45
STATE_FILE = "known_events.json"

def send_telegram(text):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": text},
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
        json.dump(sorted(list(known)), f, ensure_ascii=False, indent=2)

def get_terms_for_day(date):
    payload = {
        "action": "get_event_calendar_available_terms",
        "event_id": EVENT_ID,
        "month": date.month,
        "year": date.year,
        "day": date.day,
    }

    r = requests.post(AJAX_URL, data=payload, timeout=20)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    terms = []

    for block in soup.select(".ticket-combined-term"):
        text = block.get_text(" ", strip=True)

        if "Hokejka a puk - max 20 ľudí" not in text:
            continue

        time_match = re.search(r"(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})", text)
        capacity_match = re.search(r"Voľná kapacita\s*-\s*(\d+)", text)

        time_text = f"{time_match.group(1)} - {time_match.group(2)}" if time_match else "čas neznámy"
        free_capacity = int(capacity_match.group(1)) if capacity_match else None

        event_key = f"{date.isoformat()}|{time_text}|Hokejka a puk max 20"

        terms.append({
            "key": event_key,
            "date": date.strftime("%d.%m.%Y"),
            "time": time_text,
            "free_capacity": free_capacity,
            "raw": text,
        })

    return terms

def scan_all_days():
    today = datetime.now().date()
    all_terms = []

    for i in range(DAYS_AHEAD):
        day = today + timedelta(days=i)
        try:
            all_terms.extend(get_terms_for_day(day))
        except Exception as e:
            print(f"Chyba pri dni {day}: {e}")

    return all_terms

def main():
    known = load_known()

    print("Agent beží - presný API watcher")

    while True:
        try:
            terms = scan_all_days()

            if not terms:
                print("Kontrola OK - žiadne termíny max 20")
            else:
                print(f"Kontrola OK - nájdených termínov: {len(terms)}")

            for term in terms:
                if term["key"] not in known:
                    known.add(term["key"])
                    save_known(known)

                    capacity = (
                        f"{term['free_capacity']} voľných miest"
                        if term["free_capacity"] is not None
                        else "voľná kapacita nezistená"
                    )

                    msg = (
                        "🏒 Nový termín: Hokejka a puk - max 20 ľudí\n\n"
                        f"📅 Dátum: {term['date']}\n"
                        f"🕕 Čas: {term['time']}\n"
                        f"🎟️ Kapacita: {capacity}\n\n"
                        "Rezervuj tu:\n"
                        "https://petrzalkasportuje.sk/events/arena-drazdiak-korculovanie/"
                    )

                    send_telegram(msg)
                    print("Poslaná notifikácia:", term["key"])

        except Exception as e:
            print("Hlavná chyba:", e)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()