from web3 import Web3
import json
import os
from datetime import datetime


# Blockchain setup
RPC_URL = "http://127.0.0.1:7545"
CONTRACT_ADDRESS = "0x7BA78Cf65e400A6F39E12A2fe7bAdD2783a72876"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTRACT_ABI_PATH = os.path.join(BASE_DIR, "BlockSentinelLedgerABI.json")

# Initialize Web3
web3 = Web3(Web3.HTTPProvider(RPC_URL))
assert web3.is_connected(), "❌ Web3 connection failed"

# Load ABI
with open(CONTRACT_ABI_PATH, "r") as f:
    abi = json.load(f)

# Load contract
contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
web3.eth.default_account = web3.eth.accounts[0]  # For local testing with Ganache


# -----------------------------------------
# ✅ Store full table snapshot to blockchain + track locally
# -----------------------------------------

# Global ledger index (used by backend only)
LEDGER_INDEX = {}

def store_table_data(system_id, batch_id, db_name, table_key, schema_name, table_name, schema, rows):
    """
    Store a single table snapshot to the blockchain and log metadata in local index.
    """
    try:
        tx = contract.functions.storeTableData(
            system_id,
            db_name,
            table_key,
            schema_name,
            table_name,
            schema,
            rows
        ).transact()

        receipt = web3.eth.wait_for_transaction_receipt(tx)
        ledger_hash = receipt.transactionHash.hex()

        # 🧠 Track saved entry in local index
        LEDGER_INDEX.setdefault(system_id, []).append({
            "db_name": db_name,
            "table_key": table_key,
            "batch_id": batch_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ledger_hash": ledger_hash
        })

        print(f"✅ Table data stored: {table_name} (tx hash: {ledger_hash})")
        return receipt

    except Exception as e:
        print(f"❌ Failed to store table {table_name}: {e}")
        return None



def get_all_tables_for_system(sys_id):
    """
    Retrieves all stored tables for a system from the blockchain.
    Returns a list of table snapshots.
    """
    try:
        system_tables = LEDGER_INDEX.get(sys_id, [])

        all_entries = []
        for entry in system_tables:
            db_name = entry["db_name"]
            table_key = entry["table_key"]
            batch_id = entry["batch_id"]
            timestamp = entry["timestamp"]
            ledger_hash = entry["ledger_hash"]

            table_data = get_table_data(sys_id, db_name, table_key)
            if not table_data:
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

        return all_entries

    except Exception as e:
        print(f"[ERROR] Failed to retrieve all tables: {e}")
        return None


# ------------------------------------------------------
# ✅ Retrieve full table snapshot from blockchain
# ------------------------------------------------------
def get_table_data(system_id, db_name, table_key):
    """
    Get the table snapshot as stored by store_table_data().
    Returns: dict with keys schemaName, tableName, schema, rows
    """
    try:
        schema_name, table_name, schema, rows = contract.functions.getTableData(
            system_id, db_name, table_key
        ).call()

        return {
            "schemaName": schema_name,
            "tableName": table_name,
            "schema": schema,
            "rows": rows
        }

    except Exception as e:
        print(f"❌ Error getting table data: {e}")
        return None


# -----------------------------------------------
# ✅ Store activity log (INSERT, UPDATE, DELETE)
# -----------------------------------------------
def store_activity_log(system_id, table_key, activity_type, timestamp, username, query, new_data):
    """
    Stores a single row activity log entry
    new_data should be like: [["1", "John"]] or [["2", "Jane", "Manager"]]
    """
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


# ------------------------------------------------
# ✅ Retrieve activity logs for given system+table
# ------------------------------------------------
def get_activity_logs(system_id, table_key):
    """
    Returns: list of activity log dicts with keys:
        activityType, timestamp, username, query, newData
    """
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
