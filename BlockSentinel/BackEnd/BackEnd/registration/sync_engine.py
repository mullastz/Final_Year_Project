# registration/sync_engine.py
import threading
import time
from detection_engine.db_clients import PostgreSQLClient
from .table_monitor import TableMonitor

def start_sync(system_id, table_list):
    db = PostgreSQLClient(
        host='localhost', port=5432, user='postgres',
        password='grace2002', dbname='lecturer_evaluation_db'
    )

    monitors = [TableMonitor(db, system_id, tbl) for tbl in table_list]

    def poll_loop():
        while True:
            for monitor in monitors:
                new_rows = monitor.check_new_rows()
                if new_rows:
                    print(f"[+] Synced {len(new_rows)} new rows from {monitor.table_name}")
            time.sleep(10)  # Poll every 10 seconds

    thread = threading.Thread(target=poll_loop, daemon=True)
    thread.start()
