# V1.1 initial version

import json
import os
import pymsteams
from dotenv import load_dotenv
import sys
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Loading environment variables
load_dotenv()
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Env urls
ENVIRONMENTS = {
    "prod": "https://api.porsche-experience-center.fr",
    "preprod": "https://api-porsche-fr-preprod.cat-amania.com",
    "dev": "https://api-porsche-dev-oci.cat-amania.com"
}

# Check arguments
#if len(sys.argv) != 2 or sys.argv[1] not in ENVIRONMENTS:
#    print("Usage: python check_ms.py <environment>")
 #   print("Possible values for <environment>: prod, preprod, dev")
 #   sys.exit(1)

#BASE_ADDRESS = ENVIRONMENTS[sys.argv[1]]

# Actuator health endpoint path template
HEALTH_ENDPOINT_TEMPLATE = "/{}/actuator/health"

# JSON file paths
MICROSERVICES_FILE = os.path.join(BASE_DIR, "microservices.json")
SIMULATION_FILE = os.path.join(BASE_DIR, "simulation.json")

# Checking and loading JSON files
def load_json(file_path):
    """ Loads a JSON file and checks for its existence """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Le fichier {file_path} est introuvable.")

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

# Loading data
microservices = load_json(MICROSERVICES_FILE)
response = load_json(SIMULATION_FILE)

def send_teams_message(service, response_code, response_text, status):
    """ Sends an alert to Teams based on the microservice status """
    try:
        response = pymsteams.connectorcard(WEBHOOK_URL)
        response.title("<b>⚠️ Alert notification ⚠️</b>")

        if is_alert_active(service, status):
            return

        response.text(
            f"<u>MicroService</u> : {service} <br>"
            f"{format_message(status, response_text)} <br>"
            f"<u>Code</u> : <span style='color:{get_status_color(status)}'>{response_code}</span>"
        )
        change_status(service, status)

        assert response.send()
        print(f"Message successfully sent on Teams for {service}.")

    except Exception as e:
        print(f"An error occurred while sending the Teams message : {e}")

def get_status_color(status):
    """ Returns the color associated with the status """
    return "green" if status == "Healthy" else "red"

def change_status(service, status):
    """ Updates the microservice status and saves the JSON """
    microservices[service]["status"] = status

    with open(MICROSERVICES_FILE, "w", encoding="utf-8") as json_file:
        json.dump(microservices, json_file, indent=4)

    print(f"Status updated : {service} -> {status}")

def format_message(status, response_text):
    """ Generates the message to be displayed depending on the state of the microservice """
    if status == "Healthy":
        return "<u>Message</u> : Service is WORKING fine !"
    return f"<u>Error message</u> : Service is BROKEN ! ({response_text})"

def check_health():
    """ Checks the status of microservices and triggers an alert if necessary """

    environment_broken = False
    index=0

    for service in microservices:
        #health_url = BASE_ADDRESS + HEALTH_ENDPOINT_TEMPLATE.format(service)
        current_status = microservices[service]["status"]
        index += 1
        try:
            #response = requests.get(health_url, verify=False)
            if response[index]['status_code'] == 200 and response[index]['text'] == "-":
                status = "Healthy"
            else:
                status = "Unhealthy"
                environment_broken = True
            response_code = response[index]['status_code']
            response_text = response[index]['text']
            if current_status != status:
                print(f"{service}: Change detected → {status}")
                send_teams_message(service, response_code, response_text, status)
        except requests.exceptions.RequestException as e:
            status = f"Error ({str(e)})"
            environment_broken = True
        print(f"{service}: {status}")

    if environment_broken:
        print("\033[91mEnvironment is BROKEN!\033[0m")  # Red message
    else:
        print("\033[92mEnvironment is WORKING fine!\033[0m")  # Green message

def is_alert_active(service, status):
    """ Checks if an alert is already active to avoid duplicates """
    return microservices[service]["status"] == status

if __name__ == '__main__':
    check_health()
