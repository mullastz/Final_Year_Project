import requests
from requests.exceptions import RequestException

def install_agent(system_url: str) -> bool:
    """
    Tries to contact the registered system and trigger the agent installation.
    Returns True if successful, False otherwise.
    """
    try:
        response = requests.post(f"{system_url}/install-agent/", timeout=5)
        response.raise_for_status()
        return True
    except RequestException as e:
        # You can log this error for debugging or store it in DB
        print(f"[ERROR] Failed to install agent at {system_url}: {e}")
        return False

def discover_databases(system_url: str) -> list:
    """
    Tries to fetch list of databases from the agent.
    Returns a list of databases if successful, else empty list.
    """
    try:
        response = requests.get(f"{system_url}/discover-databases", timeout=5)
        response.raise_for_status()
        data = response.json()
        databases = data.get('databases', [])
        print(f"[INFO] Discovered databases at {system_url}: {databases}")
        return databases
    except RequestException as e:
        print(f"[ERROR] Failed to discover databases at {system_url}: {e}")
        return []
