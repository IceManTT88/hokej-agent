import requests
import time
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://petrzalkasportuje.sk/events/arena-drazdiak-korculovanie/"

known = set()

def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": msg
        }
    )

while True:
    try:
        r = requests.get(URL)

        html = r.text

        if "Hokejka a puk" in html:

            if html not in known:

                known.add(html)

                send(
                    "🏒 Nový termín Hokejka a puk!\n\n"
                    + URL
                )

                print("Notifikácia poslaná")

        print("Kontrola OK")

    except Exception as e:
        print(e)

    time.sleep(300)