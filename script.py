import json
import os
import pymsteams
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Chemins des fichiers JSON
MICROSERVICES_FILE = os.path.join(BASE_DIR, "microservices.json")
SIMULATION_FILE = os.path.join(BASE_DIR, "simulation.json")

# Vérification et chargement des fichiers JSON
def load_json(file_path):
    """ Charge un fichier JSON et vérifie son existence """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Le fichier {file_path} est introuvable.")

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

# Chargement des données
microservices = load_json(MICROSERVICES_FILE)
simulation = load_json(SIMULATION_FILE)

def send_teams_message(service, item, status):
    """ Envoie une alerte sur Teams en fonction de l'état du microservice """
    try:
        response = pymsteams.connectorcard(WEBHOOK_URL)
        response.title("<b>⚠️ Notification d'alerte ⚠️</b>")

        if is_alert_active(service, status):
            return

        response.text(
            f"<u>Micro service</u> : {service} <br>"
            f"{format_message(status, item)} <br>"
            f"<u>Code</u> : <span style='color:{get_status_color(status)}'>{item['status_code']}</span>"
        )
        change_status(service, status)

        assert response.send()
        print(f"Message envoyé avec succès sur Teams pour {service}.")

    except Exception as e:
        print(f"Une erreur est survenue lors de l'envoi du message Teams : {e}")

def get_status_color(status):
    """ Retourne la couleur associée au statut """
    return "green" if status == "Healthy" else "red"

def change_status(service, status):
    """ Met à jour le statut du microservice et sauvegarde le JSON """
    microservices[service]["status"] = status

    with open(MICROSERVICES_FILE, "w", encoding="utf-8") as json_file:
        json.dump(microservices, json_file, indent=4)

    print(f"Statut mis à jour : {service} -> {status}")

def format_message(status, item):
    """ Génère le message à afficher selon l'état du microservice """
    if status == "Healthy":
        return "<u>Message</u> : Le microservice est de nouveau fonctionnel."
    return f"<u>Message d'erreur</u> : {item['message_error']}"

def check_condition():
    """ Vérifie l'état des microservices et déclenche une alerte si nécessaire """
    for index, service in enumerate(microservices):
        current_status = microservices[service]["status"]
        new_status = "Healthy" if simulation[index]['status_code'] == 200 else "Unhealthy"

        if current_status == new_status:
            print(f"{service}: Aucun changement")
            continue

        print(f"{service}: Changement détecté → {new_status}")
        send_teams_message(service, simulation[index], new_status)

def is_alert_active(service, status):
    """ Vérifie si une alerte est déjà active pour éviter les doublons """
    return microservices[service]["status"] == status

if __name__ == '__main__':
    check_condition()
