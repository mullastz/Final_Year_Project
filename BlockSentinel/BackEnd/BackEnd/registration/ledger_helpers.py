# registration/utils/ledger_helpers.py

from blockchain.ledger_index import LEDGER_INDEX

def find_ledger_entry(system_id, table_id):
    entries = LEDGER_INDEX.get(system_id, [])

    try:
        batch_part, index_part = table_id.rsplit("-", 1)
        index = int(index_part)
    except ValueError:
        print(f"[ERROR] Invalid table_id format: {table_id}")
        return None

    matching_entries = [
        entry for entry in entries if entry["batch_id"] == batch_part
    ]

    if index < 1 or index > len(matching_entries):
        print(f"[ERROR] Index {index} out of range for batch: {batch_part}")
        return None

    # Return the N-th entry in the batch (index is 1-based)
    return matching_entries[index - 1]

