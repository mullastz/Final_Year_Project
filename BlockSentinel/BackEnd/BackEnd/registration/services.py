from typing import List
import mysql
import psycopg2
from pymongo import MongoClient
import requests
import socket
from requests.exceptions import RequestException
from .data_extraction_engine import extract_data
from blockchain.blockchain_client import   get_table_data_by_id, get_all_tables_for_system
import json
import uuid
import re
from datetime import datetime
from .ledger_helpers import find_ledger_entry



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
    try:
        response = requests.get(f"{system_url}/discover-databases", timeout=5)
        response.raise_for_status()
        data = response.json()
        databases = data.get('databases', [])
        # Normalize to list of strings (types only)
        if databases and isinstance(databases[0], dict):
            databases = [db.get("type") or db.get("name") for db in databases]
        print(f"[INFO] Discovered database types at {system_url}: {databases}")
        return databases
    except RequestException:
        print(f"[WARN] discover-databases endpoint not available, falling back to port scan.")
        ip = system_url.split("//")[-1].split(":")[0]
        fallback_dbs = scan_common_db_ports(ip)
        print(f"[INFO] Discovered via port scan: {fallback_dbs}")
        return fallback_dbs

def scan_common_db_ports(ip: str) -> list:
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
                discovered.append(db_type)  # Just the type
            except Exception:
                continue
    return discovered


def fetch_database_names(ip_address: str, db_type: str, credentials: dict) -> List[str]:
    try:
        if db_type == 'PostgreSQL':
            conn = psycopg2.connect(
                host=credentials['host'],
                port=credentials['port'],
                user=credentials['user'],
                password=credentials['password'],
                connect_timeout=5
            )
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
            dbs = [row[0] for row in cur.fetchall()]
            cur.close()
            conn.close()
            return dbs

        elif db_type == 'MySQL':
            conn = mysql.connector.connect(
                host=credentials['host'],
                port=credentials['port'],
                user=credentials['user'],
                password=credentials['password'],
                connection_timeout=5
            )
            cursor = conn.cursor()
            cursor.execute("SHOW DATABASES;")
            dbs = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return dbs

        elif db_type == 'MongoDB':
            client = MongoClient(
                host=credentials['host'],
                port=int(credentials['port']),
                username=credentials['user'],
                password=credentials['password'],
                serverSelectionTimeoutMS=5000
            )
            dbs = client.list_database_names()
            client.close()
            return dbs

        else:
            return []

    except Exception as e:
        print(f"Error fetching DBs: {e}")
        return []

def extract_data_from_system(system_url: str, databases: list, credentials_map: dict, system_id: str):
    all_data = {}

    for db in databases:
        db_name = db['name']
        db_type = db['type']

        if db_name not in credentials_map:
            print(f"[WARN] No credentials for {db_name}. Skipping.")
            continue

        try:
            print(f"[INFO] Extracting from {db_type} database: {db_name}")
            connection_info = credentials_map[db_name]

            result = extract_data(db_type, connection_info, system_id=system_id, db_name=db_name)

            for sys_id, sys_data in result.items():
                if sys_id not in all_data:
                    all_data[sys_id] = {}

                all_data[sys_id].update(sys_data)

        except Exception as e:
            print(f"[ERROR] Extraction failed for {db_name}: {e}")

    return all_data

def get_ledger_data(system_id: str):
    """
    Fetch stored ledger data from blockchain for a given system.
    Returns parsed list of table snapshots.
    """
    try:
        data = get_all_tables_for_system(system_id)
        return data
    except Exception as e:
        print(f"[ERROR] Failed to retrieve ledger data: {e}")
        return None


def generate_table_summaries(sys_id):
    """
    Converts raw ledger data into per-table summaries for frontend display.
    """
    all_ledger = get_all_tables_for_system(sys_id)
    if not all_ledger:
        return []

    table_summaries = []
    batch_table_counts = {}

    for ledger in all_ledger:
        batch_id = ledger["batch_id"]
        table_name = ledger["table_name"]
        timestamp = ledger["timestamp"]
        ledger_hash = ledger["ledger_hash"]
        total_rows = len(ledger.get("rows", []))

        # Create a unique table ID per batch
        count = batch_table_counts.get(batch_id, 0) + 1
        batch_table_counts[batch_id] = count
        table_id = f"{batch_id}-{count:03d}"

        table_summaries.append({
            "table_id": table_id,
            "description": table_name,
            "total_rows": total_rows,
            "timestamp": timestamp,
            "ledger_hash": ledger_hash
        })

    return table_summaries


def fetch_table_data(sys_id, table_id):
    """
    Fetch full ledger table data by querying blockchain_client after
    getting ledger metadata from local index.
    """
    ledger_entry = find_ledger_entry(sys_id, table_id)
    if not ledger_entry:
        print(f"[WARN] Ledger entry not found in local index: {table_id}")
        return None

    # Now fetch full data from blockchain
    return  get_table_data_by_id(sys_id, table_id)

def get_ledger_data(system_id: str, db_name: str, table_key: str):
    """
    Fetch stored ledger data from blockchain for a given system.
    """
    try:
        table_id = f"{db_name}.{table_key}"  # or however your table_id is constructed
        data =  get_table_data_by_id(system_id, table_id)
        return data
    except Exception as e:
        print(f"[ERROR] Failed to retrieve ledger data: {e}")
        return None


def get_table_data_by_table_id(sys_id, table_id):
    """
    Given a system ID and a specific table_id (like 'abc123-001'),
    returns the full data (columns + rows) for that table.
    """
    match = re.match(r"^(.*)-(\d{3})$", table_id)
    if not match:
        raise ValueError("Invalid table_id format")

    batch_id_prefix, table_index_str = match.groups()
    table_index = int(table_index_str) - 1  # index in 0-based list

    all_ledger = get_ledger_data(sys_id)
    target_ledger = next((l for l in all_ledger if l["batch_id"] == batch_id_prefix), None)

    if not target_ledger:
        raise ValueError(f"Batch ID {batch_id_prefix} not found")

    data = target_ledger["data"]
    table_names = list(data.keys())

    if table_index >= len(table_names):
        raise ValueError("Table index out of range")

    table_name = table_names[table_index]
    table_data = data[table_name]

    return {
        "table_name": table_name,
        "columns": table_data.get("columns", []),
        "rows": table_data.get("rows", [])
    }


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

