import json
import os
import pymsteams
from flask import Flask, Response
from dotenv import load_dotenv

from BotNotif.script import changeStatus, has_alert_been_actived

# Chargement des variables d'environnement
load_dotenv()
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MICROSERVICES_FILE = os.path.join(BASE_DIR, "microservices.json")

# Vérification et chargement des microservices
def load_json(file_path):
    """ Charge un fichier JSON et vérifie son existence """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Le fichier {file_path} est introuvable.")

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

# Charger les microservices
microservices = load_json(MICROSERVICES_FILE)

# Initialisation de l'application Flask
app = Flask(__name__)

def send_teams_resolution_message(service):
    """ Envoie un message sur Teams indiquant qu'un service est résolu """
    try:
        teams_message = pymsteams.connectorcard(WEBHOOK_URL)
        teams_message.text(f"Le microservice **{service}** a été résolu.")
        teams_message.send()
        print(f"Résolution envoyée sur Teams pour {service}.")
    except Exception as e:
        print(f"Erreur lors de l'envoi du message Teams : {e}")

def update_service_status(service, status):
    """ Met à jour le statut du microservice et sauvegarde le JSON """
    try:
        microservices = load_json(MICROSERVICES_FILE)

        if service in microservices:
            microservices[service]["status"] = status

            with open(MICROSERVICES_FILE, "w", encoding="utf-8") as json_file:
                json.dump(microservices, json_file, indent=4)

            print(f"Statut mis à jour : {service} → {status}")
        else:
            print(f"Service {service} non trouvé.")

    except Exception as e:
        print(f"Erreur lors de la mise à jour du statut de {service} : {e}")

@app.route('/button_clicked/<service>', methods=['GET'])
def button_clicked(service):
    """ Gère le clic sur le bouton de résolution depuis Teams """
    print(f"Bouton cliqué pour : {service}")

    if not has_alert_been_actived(service):
        teams_message = pymsteams.connectorcard(WEBHOOK_URL)
        teams_message.text("Ce bouton a déjà été utilisé. Action refusée.")
        teams_message.send()
        print(f"Tentative de résolution répétée pour {service}.")
    else:
        send_teams_resolution_message(service)
        update_service_status(service, "Healthy")

    return Response('<script>window.close();</script>', mimetype='text/html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
