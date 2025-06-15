import requests
import socket
from requests.exceptions import RequestException
from .data_extraction_engine import extract_data

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
        print(f"[WARN] discover-databases endpoint not available, falling back to port scan.")
        # Extract IP from system_url (strip http:// and port)
        ip = system_url.split("//")[-1].split(":")[0]
        fallback_dbs = scan_common_db_ports(ip)
        print(f"[INFO] Discovered via port scan: {fallback_dbs}")
        return fallback_dbs

def scan_common_db_ports(ip: str):
    known_ports = {
        3306: 'MySQL',
        5432: 'PostgreSQL',
        27017: 'MongoDB',
        1433: 'MSSQL',
    }
    discovered = []
    for port, db_type in known_ports.items():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            try:
                s.connect((ip, port))
                discovered.append({"name": f"unknown_{db_type.lower()}_{port}", "type": db_type})
            except Exception:
                continue
    return discovered

def fetch_db_names(db_type: str, credentials: dict) -> list:
    """
    Connects using provided credentials and fetches actual DB names.
    """
    try:
        if db_type == "PostgreSQL":
            import psycopg2
            conn = psycopg2.connect(**credentials)
            cur = conn.cursor()
            cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
            return [row[0] for row in cur.fetchall()]
        elif db_type == "MySQL":
            import mysql.connector
            conn = mysql.connector.connect(**credentials)
            cur = conn.cursor()
            cur.execute("SHOW DATABASES")
            return [db[0] for db in cur.fetchall()]
        elif db_type == "MongoDB":
            from pymongo import MongoClient
            client = MongoClient(credentials['uri'])
            return client.list_database_names()
        elif db_type == "Oracle":
            import cx_Oracle
            dsn = cx_Oracle.makedsn(credentials['host'], credentials['port'], sid=credentials['sid'])
            conn = cx_Oracle.connect(credentials['user'], credentials['password'], dsn)
            cur = conn.cursor()
            cur.execute("SELECT username FROM all_users")
            return [row[0] for row in cur.fetchall()]
        elif db_type == "SQLite":
            # Single DB in SQLite
            return ["default"]
        else:
            raise ValueError("Unsupported DB type")
    except Exception as e:
        print(f"[ERROR] Failed to fetch DB names: {e}")
        return []


def extract_data_from_system(system_url: str, databases: list, credentials_map: dict):
    """
    For each discovered database, extract schema and data using correct extractor.
    Returns a dict of { db_name: { table_name: [data], ... }, ... }
    
    - `databases`: list of dicts like {name: 'employees_db', type: 'PostgreSQL'}
    - `credentials_map`: dict mapping db_name -> connection_info (username, password, host, etc.)
    """
    all_data = {}

    for db in databases:
        db_name = db['name']
        db_type = db['type']

        if db_name not in credentials_map:
            print(f"[WARN] No credentials provided for {db_name}. Skipping.")
            continue

        try:
            print(f"[INFO] Extracting from {db_type} database: {db_name}")
            connection_info = credentials_map[db_name]
            extracted = extract_data(db_type, connection_info)
            all_data[db_name] = extracted
        except Exception as e:
            print(f"[ERROR] Failed extracting from {db_name}: {e}")

    return all_data

def install_agent(system_url):
    # Logic to SSH or make HTTP request to remote system
    # Possibly run an install script
    print(f"Installing agent on {system_url}")
    return True  # Or False if something fails

def scan_for_databases(system_url):
    # Use port scanning or agent API to list databases
    return [
        { "name": "main_db", "type": "PostgreSQL" },
        { "name": "users_db", "type": "MySQL" }
    ]

def get_extractor_instance(db_name, credentials):
    db_type = credentials.get("type")
    
    if db_type == "PostgreSQL":
        from .extractors.postgres import PostgresExtractor # type: ignore
        return PostgresExtractor(credentials)
    elif db_type == "MySQL":
        from .extractors.mysql import MySQLExtractor # type: ignore
        return MySQLExtractor(credentials)
    # Add more database types as needed

    raise Exception("Unsupported database type")

