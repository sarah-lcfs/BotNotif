# V1.0 initial version

import sys
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Env urls
ENVIRONMENTS = {
    "prod": "https://api.porsche-experience-center.fr",
    "preprod": "https://api-porsche-fr-preprod.cat-amania.com",
    "dev": "https://api-porsche-dev-oci.cat-amania.com"
}

# Check arguments
if len(sys.argv) != 2 or sys.argv[1] not in ENVIRONMENTS:
    print("Usage: python check_ms.py <environment>")
    print("Possible values for <environment>: prod, preprod, dev")
    sys.exit(1)

BASE_ADDRESS = ENVIRONMENTS[sys.argv[1]]

# List of microservice names
microservices = [
    "mail",
    "template",
    "pdf",
    "file",  
    "auth",
    "admin",
    "bill",
    "btob",
    "car",
    "client",
    "event",
    "payment",
    "pte",
    "registry",
    "reservation",
    "resource",
    "stats",
    "accounting",
    # Add more microservice names as needed
]

# Actuator health endpoint path template
HEALTH_ENDPOINT_TEMPLATE = "/{}/actuator/health"

def check_health():
    environment_broken = False
    
    for service in microservices:
        health_url = BASE_ADDRESS + HEALTH_ENDPOINT_TEMPLATE.format(service)
        try:
            response = requests.get(health_url, verify=False)
            if response.status_code == 200 and response.text == "{\"status\":\"UP\"}":
                status = "Healthy"
            else:
                status = f"Unhealthy ({response.status_code})"
                environment_broken = True
        except requests.exceptions.RequestException as e:
            status = f"Error ({str(e)})"
            environment_broken = True
        print(f"{service}: {status}")
    
    if environment_broken:
        print("\033[91mEnvironment is BROKEN!\033[0m")  # Red message
    else:
        print("\033[92mEnvironment is WORKING fine!\033[0m")  # Green message

if __name__ == "__main__":
    check_health()
