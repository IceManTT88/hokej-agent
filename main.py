import requests
import time
import os

BOT_TOKEN = os.environ["8681396624:AAGJL9sPc-OXOHclAbGg9jB43TUDJ3fSUWM"]
CHAT_ID = os.environ["457833924"]

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