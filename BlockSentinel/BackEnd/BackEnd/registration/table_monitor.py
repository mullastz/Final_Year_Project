# registration/table_monitor.py
from datetime import datetime
import uuid
from blockchain.blockchain_client import store_table_data

class TableMonitor:
    def __init__(self, db_client, system_id, table_name):
        self.db_client = db_client
        self.system_id = system_id
        self.table_name = table_name
        self.last_seen_id = self._get_last_id()

    def _get_last_id(self):
        try:
            query = f"SELECT MAX(id) FROM {self.table_name}"
            result = self.db_client.cursor.execute(query)
            return self.db_client.cursor.fetchone()[0] or 0
        except Exception as e:
            print(f"[ERROR] Failed to get last ID for {self.table_name}: {e}")
            return 0

    def check_new_rows(self):
        try:
            query = f"SELECT * FROM {self.table_name} WHERE id > {self.last_seen_id} ORDER BY id ASC"
            self.db_client.cursor.execute(query)
            new_rows = self.db_client.cursor.fetchall()

            if not new_rows:
                return []

            # Update last seen ID
            self.last_seen_id = max(row[0] for row in new_rows)

            # Get column names
            col_names = [desc[0] for desc in self.db_client.cursor.description]

            # ✅ Prepare schema and rows in string[][] format
            schema = [[col] for col in col_names]
            rows = [[str(cell) for cell in row] for row in new_rows]

            # Generate IDs
            batch_id = str(uuid.uuid4())
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Call blockchain storage
            store_table_data(
                system_id=self.system_id,
                batch_id=batch_id,
                db_name='lecturer_evaluation_db',
                table_key=self.table_name,
                schema_name='public',
                table_name=self.table_name,
                schema=schema,
                rows=rows,
                timestamp=timestamp
            )

            print(f"[+] Synced {len(new_rows)} new rows from {self.table_name}")
            return new_rows

        except Exception as e:
            print(f"[ERROR] Failed to check new rows for {self.table_name}: {e}")
            return []
