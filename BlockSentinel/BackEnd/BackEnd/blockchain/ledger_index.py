import json
from pathlib import Path

# 🔁 Path to store the ledger index persistently
LEDGER_INDEX_FILE = Path(__file__).parent / "ledger_index_store.json"

# 🔁 Load existing data from file if available
if LEDGER_INDEX_FILE.exists():
    with open(LEDGER_INDEX_FILE, "r") as f:
        LEDGER_INDEX = json.load(f)
else:
    LEDGER_INDEX = {}

# 🧠 Utility function to persist changes to disk
def save_ledger_index():
    with open(LEDGER_INDEX_FILE, "w") as f:
        json.dump(LEDGER_INDEX, f, indent=2)
