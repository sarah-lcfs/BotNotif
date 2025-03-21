import json

from flask import Flask, Response, request
import pymsteams
import os
from dotenv import load_dotenv

from BotNotif.script import changeStatus, has_alert_been_actived

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "microservices.json"), "r") as json_file:
    microservices = json.load(json_file)

app = Flask(__name__)

load_dotenv()
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

def sendTeamsMessageResponse(service):
    try:
        teams_message = pymsteams.connectorcard(WEBHOOK_URL)
        teams_message.text(f"Le micro service <strong>{service}</strong> a été résolu.")
        teams_message.send()
        print("Message envoyé sur Teams")
    except Exception as e:
        print(f"Erreur lors de l'envoi du message Teams : {e}")


def resetStatus(service, status):

    microservices_path = os.path.join(BASE_DIR, "microservices.json")

    with open(microservices_path, "r") as json_file:
        microservices = json.load(json_file)

    if service in microservices:
        microservices[service]["status"] = status

        with open(microservices_path, "w", encoding="utf-8") as json_file:
            json.dump(microservices, json_file, indent=4)

        print(f"Changement de l'alerte - {service} : {microservices[service]}")

    else:
        print(f"Service {service} non trouvé.")


@app.route('/button_clicked/<service>', methods=['GET'])
def button_clicked(service):
    print("OK")

    if has_alert_been_actived(service) == False:
        teams_message = pymsteams.connectorcard(WEBHOOK_URL)
        teams_message.text("Ce bouton a déjà été utilisé. Action refusée")
        teams_message.send()
    else:
        sendTeamsMessageResponse(service)
        resetStatus(service, "Healthy")

    return Response('<script>window.close();</script>', mimetype='text/html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
