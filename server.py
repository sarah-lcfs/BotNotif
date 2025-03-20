from flask import Flask, Response
import pymsteams
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
BUTTON_FILE  = "button_state.txt"
STATE_FILE = "alert_state.txt"

def sendTeamsMessageResponse(message):
    try:
        teams_message = pymsteams.connectorcard(WEBHOOK_URL)
        teams_message.text(message)
        teams_message.send()
        print("Message envoyé sur Teams : ", message)
    except Exception as e:
        print(f"Erreur lors de l'envoi du message Teams : {e}")

@app.route('/button_clicked', methods=['GET'])
def button_clicked():
    print("OK")

    if os.path.exists(BUTTON_FILE):
        sendTeamsMessageResponse("Ce bouton a déjà été utilisé. Action refusée")
    else:
        sendTeamsMessageResponse("Bouton cliqué ! Action enregistrée")
        with open(BUTTON_FILE, "w") as f:
            f.write("clicked")
        os.remove(STATE_FILE)

    return Response('<script>window.close();</script>', mimetype='text/html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
