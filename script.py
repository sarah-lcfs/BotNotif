import pymsteams
import os
from dotenv import load_dotenv

load_dotenv()
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
BUTTON_FILE = "button_state.txt"
STATE_FILE = "alert_state.txt"

def sendTeamsMessage(message):
    try:
        response = pymsteams.connectorcard(WEBHOOK_URL)
        response.title("Notification alerte")

        if has_alert_been_actived():
            response.text("Action déjà en cours")
        else:
            response.text(message)
            response.addLinkButton("Clique ici", "http://localhost:5000/button_clicked")
            mark_alert_as_actived()
            if os.path.exists(BUTTON_FILE):
                os.remove(BUTTON_FILE)


        assert response.send()

        print("Message envoyé avec succès sur Teams !")

    except Exception as e:
        print(f"Une erreur est survenue : {e}")

def checkCondition():
    valeur = 15
    if valeur > 10:
        sendTeamsMessage(f"Alerte : Valeur incorrecte ({valeur})")

def has_button_been_clicked():
    return os.path.exists(BUTTON_FILE)

def mark_button_as_clicked():
    with open(BUTTON_FILE , "w") as f:
        f.write("clicked")

def has_alert_been_actived():
    return os.path.exists(STATE_FILE)

def mark_alert_as_actived():
    with open(STATE_FILE, "w") as f:
        f.write("actived")

if __name__ == '__main__':
    checkCondition()
