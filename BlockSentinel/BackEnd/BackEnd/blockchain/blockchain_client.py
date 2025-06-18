from web3 import Web3
import json
import os
from datetime import datetime
from .ledger_index import LEDGER_INDEX, save_ledger_index
from registration.ledger_helpers import find_ledger_entry

# Blockchain setup
RPC_URL = "http://127.0.0.1:7545"
CONTRACT_ADDRESS = "0xFD5cE4c47cf4fCCCF4def46dd7E29E8f646bbFB2"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTRACT_ABI_PATH = os.path.join(BASE_DIR, "BlockSentinelLedgerABI.json")
SYSTEMS_FILE = os.path.join(BASE_DIR, "known_systems.json")

web3 = Web3(Web3.HTTPProvider(RPC_URL))
assert web3.is_connected(), "❌ Web3 connection failed"

with open(CONTRACT_ABI_PATH, "r") as f:
    abi = json.load(f)

contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
web3.eth.default_account = web3.eth.accounts[0]

# ---------------------------
# ✅ Save and List System IDs
# ---------------------------
def list_system_ids_from_disk():
    try:
        if os.path.exists(SYSTEMS_FILE):
            with open(SYSTEMS_FILE, "r") as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"[WARN] Could not load system IDs: {e}")
        return []

def save_system_id(system_id):
    ids = list_system_ids_from_disk()
    if system_id not in ids:
        ids.append(system_id)
        with open(SYSTEMS_FILE, "w") as f:
            json.dump(ids, f)

# ---------------------------
# ✅ Store table snapshot
# ---------------------------
def store_table_data(system_id, batch_id, db_name, table_key, schema_name, table_name, schema, rows, timestamp):
    try:
        tx = contract.functions.storeTableData(
            system_id,
            db_name,
            table_key,
            schema_name,
            table_name,
            schema,
            rows,
            batch_id,
            timestamp
        ).transact()

        receipt = web3.eth.wait_for_transaction_receipt(tx)
        ledger_hash = receipt.transactionHash.hex()

        LEDGER_INDEX.setdefault(system_id, []).append({
            "db_name": db_name,
            "table_key": table_key,
            "batch_id": batch_id,
            "timestamp": timestamp,
            "ledger_hash": ledger_hash
        })

        save_ledger_index()
        save_system_id(system_id)

        print(f"✅ Table data stored: {table_name} (tx hash: {ledger_hash})")
        return receipt

    except Exception as e:
        print(f"[ERROR] Failed to store table {table_name}: {e}")
        return None

# ---------------------------
# ✅ Rebuild local index
# ---------------------------
def rebuild_ledger_index():
    print("🔁 Rebuilding local ledger index from blockchain...")

    try:
        system_ids = list_system_ids_from_disk()
        for system_id in system_ids:
            table_keys = contract.functions.getSystemTableKeys(system_id).call()

            for table_key in table_keys:
                db_name, batch_id, timestamp = contract.functions.getLedgerMetadata(system_id, table_key).call()
                ledger_hash = "<hash unavailable post-restart>"

                LEDGER_INDEX.setdefault(system_id, []).append({
                    "db_name": db_name,
                    "table_key": table_key,
                    "batch_id": batch_id,
                    "timestamp": timestamp,
                    "ledger_hash": ledger_hash
                })

        save_ledger_index()
        print("✅ Ledger index rebuilt successfully.")

    except Exception as e:
        print(f"❌ Failed to rebuild ledger index: {e}")

# ---------------------------
# ✅ Fetch full ledger
# ---------------------------
def get_all_tables_for_system(sys_id):
    try:
        print(f"[DEBUG] Checking system ID in LEDGER_INDEX: {sys_id}")
        system_tables = LEDGER_INDEX.get(sys_id, [])
        print(f"[DEBUG] Found {len(system_tables)} tables for system: {system_tables}")

        all_entries = []
        for entry in system_tables:
            db_name = entry["db_name"]
            table_key = entry["table_key"]
            batch_id = entry["batch_id"]
            timestamp = entry["timestamp"]
            ledger_hash = entry["ledger_hash"]

            print(f"[DEBUG] Fetching table data for: {db_name}.{table_key}")
            table_data = get_table_data_by_parts(sys_id, db_name, table_key)  # ✅ fixed here

            if not table_data:
                print(f"[WARNING] No data found for {table_key}")
                continue

            all_entries.append({
                "batch_id": batch_id,
                "timestamp": timestamp,
                "db_name": db_name,
                "table_name": table_data.get("tableName"),
                "columns": table_data.get("schema", []),
                "rows": table_data.get("rows", []),
                "ledger_hash": ledger_hash
            })

        print(f"[DEBUG] Returning {len(all_entries)} table entries")
        return all_entries

    except Exception as e:
        print(f"[ERROR] Failed to retrieve all tables: {e}")
        return None

# ---------------------------
# ✅ Rebuild local index
# ---------------------------
def refresh_ledger_index_for_system(system_id: str):
    """
    Refresh the local in-memory ledger index for a specific system from blockchain.
    """
    print(f"🔄 Refreshing ledger index for system: {system_id}")

    try:
        table_keys = contract.functions.getSystemTableKeys(system_id).call()

        new_entries = []
        for table_key in table_keys:
            db_name, batch_id, timestamp = contract.functions.getLedgerMetadata(system_id, table_key).call()
            ledger_hash = "<hash unavailable post-restart>"

            new_entries.append({
                "db_name": db_name,
                "table_key": table_key,
                "batch_id": batch_id,
                "timestamp": timestamp,
                "ledger_hash": ledger_hash
            })

        LEDGER_INDEX[system_id] = new_entries
        save_ledger_index()
        print(f"✅ Index refreshed for system {system_id} with {len(new_entries)} entries.")

    except Exception as e:
        print(f"❌ Failed to refresh index for {system_id}: {e}")


# ---------------------------
# ✅ Fetch single table (by table_id)
# ---------------------------
def get_table_data_by_id(system_id: str, table_id: str):
    """
    Fetch the full table data using system_id and table_id.
    If the ledger entry is missing, refresh the index for that system.
    """
    try:
        ledger_entry = find_ledger_entry(system_id, table_id)

        if not ledger_entry:
            print(f"[WARN] Ledger entry not found for {table_id}. Refreshing index...")
            refresh_ledger_index_for_system(system_id)
            ledger_entry = find_ledger_entry(system_id, table_id)

            if not ledger_entry:
                print(f"[ERROR] Still missing ledger entry after refresh: {table_id}")
                return None

        db_name = ledger_entry['db_name']
        table_key = ledger_entry['table_key']
        print(f"[DEBUG] Fetching table data for: {db_name}.{table_key}")

        schemaName, tableName, schema, rows = contract.functions.getTableData(
            system_id, db_name, table_key
        ).call()

        return {
            "schemaName": schemaName,
            "tableName": tableName,
            "schema": schema,
            "rows": rows,
        }

    except Exception as e:
        print(f"[ERROR] Failed to get table data from blockchain: {e}")
        return None

# ---------------------------
# ✅ Fetch single table (by db_name + table_key)
# ---------------------------
def get_table_data_by_parts(system_id: str, db_name: str, table_key: str):
    try:
        schemaName, tableName, schema, rows = contract.functions.getTableData(
            system_id, db_name, table_key
        ).call()

        return {
            "schemaName": schemaName,
            "tableName": tableName,
            "schema": schema,
            "rows": rows,
        }

    except Exception as e:
        print(f"[ERROR] Failed to get table data from blockchain: {e}")
        return None

# ---------------------------
# ✅ Store activity logs
# ---------------------------
def store_activity_log(system_id, table_key, activity_type, timestamp, username, query, new_data):
    tx = contract.functions.storeActivityLog(
        system_id,
        table_key,
        activity_type,
        timestamp,
        username,
        query,
        new_data
    ).transact()

    receipt = web3.eth.wait_for_transaction_receipt(tx)
    print(f"✅ Activity log stored (tx hash: {receipt.transactionHash.hex()})")
    return receipt

# ---------------------------
# ✅ Fetch activity logs
# ---------------------------
def get_activity_logs(system_id, table_key):
    try:
        logs = contract.functions.getActivityLogs(system_id, table_key).call()
        result = []

        for log in logs:
            result.append({
                "activityType": log[0],
                "timestamp": log[1],
                "username": log[2],
                "query": log[3],
                "newData": log[4]
            })

        return result

    except Exception as e:
        print(f"❌ Error getting activity logs: {e}")
        return []

# Run on startup
rebuild_ledger_index()
