import json
import pymsteams
import os
from dotenv import load_dotenv

load_dotenv()
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


with open(os.path.join(BASE_DIR, "microservices.json"), "r") as json_file:
    microservices = json.load(json_file)

with open(os.path.join(BASE_DIR, "simulation.json"), "r") as json_file:
    simulation = json.load(json_file)

def sendTeamsMessage(service, item):
    try:
        response = pymsteams.connectorcard(WEBHOOK_URL)
        response.title("Notification d'alerte")

        if has_alert_been_actived(service):
            response.text("Action déjà en cours")
        else:
            response.text(f"Micro service : {service} <br>"
                          f"Message d'erreur : {item["message_error"]} <br>"
                          f"Code : {item["status_code"]}")
            response.addLinkButton("Marquer comme résolu", f"http://localhost:5000/button_clicked/{service}")
            changeStatus(service, "Unhealthy")

        assert response.send()

        print("Message envoyé avec succès sur Teams !")

    except Exception as e:
        print(f"Une erreur est survenue : {e}")

def changeStatus(service, status):

    microservices[service]["status"] = status

    with open("microservices.json", "w") as json_file:
        json.dump(microservices, json_file, indent=4)

    print("Changement de l'alerte")


def checkCondition():
    index = 0
    for service in microservices:
        if simulation[index]['status_code'] == 200 :
            status = "Healthy"
            index+=1
        else:
            status = "Unhealthy"
            print("Service : " + service + " || status : " + status + " || message : " + simulation[index]['message_error'])
            item = simulation[index]
            sendTeamsMessage(service, item)
            index+=1
        print(f"{service}: {status}")

def has_alert_been_actived(service):
    if microservices[service]["status"] == "Unhealthy":
        print("true")
        return True
    else:
        print("false")
        return False

if __name__ == '__main__':
    checkCondition()
