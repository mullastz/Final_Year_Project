import json
import time
import hashlib

class SchemaTemperingDetector:
    def __init__(self, db_client, baseline_file='schema_baseline.json'):
        """
        db_client: Object with method get_schema() returning dict schema metadata:
            {
              'tables': {
                  'table1': {
                      'columns': {
                          'col1': {'type': 'varchar', 'nullable': False, 'default': None},
                          'col2': {...},
                      },
                      'indexes': [...],
                      'constraints': [...],
                  },
                  ...
              }
            }
        """
        self.db_client = db_client
        self.baseline_file = baseline_file
        self.baseline_schema = self.load_baseline()

    def load_baseline(self):
        try:
            with open(self.baseline_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    def save_baseline(self, schema):
        with open(self.baseline_file, 'w') as f:
            json.dump(schema, f, indent=4)

    def hash_schema_part(self, part):
        """Create a stable hash of part of schema for quick diff"""
        serialized = json.dumps(part, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()

    def detect_changes(self, old_schema, new_schema):
        alerts = []

        old_tables = old_schema.get('tables', {})
        new_tables = new_schema.get('tables', {})

        # Detect new tables
        for t in new_tables:
            if t not in old_tables:
                alerts.append({
                    'severity': 'CRITICAL',
                    'description': f"New table created: {t}",
                    'timestamp': time.time(),
                    'type': 'SchemaTempering',
                    'table': t,
                    'change': 'table_created'
                })

        # Detect dropped tables
        for t in old_tables:
            if t not in new_tables:
                alerts.append({
                    'severity': 'CRITICAL',
                    'description': f"Table dropped: {t}",
                    'timestamp': time.time(),
                    'type': 'SchemaTempering',
                    'table': t,
                    'change': 'table_dropped'
                })

        # Detect changes in existing tables
        for t in new_tables:
            if t in old_tables:
                old_table = old_tables[t]
                new_table = new_tables[t]

                # Compare columns
                old_cols = old_table.get('columns', {})
                new_cols = new_table.get('columns', {})

                # New columns
                for c in new_cols:
                    if c not in old_cols:
                        alerts.append({
                            'severity': 'WARNING',
                            'description': f"New column '{c}' added to table '{t}'",
                            'timestamp': time.time(),
                            'type': 'SchemaTempering',
                            'table': t,
                            'column': c,
                            'change': 'column_added'
                        })
                # Dropped columns
                for c in old_cols:
                    if c not in new_cols:
                        alerts.append({
                            'severity': 'CRITICAL',
                            'description': f"Column '{c}' dropped from table '{t}'",
                            'timestamp': time.time(),
                            'type': 'SchemaTempering',
                            'table': t,
                            'column': c,
                            'change': 'column_dropped'
                        })
                # Altered columns
                for c in new_cols:
                    if c in old_cols:
                        if self.hash_schema_part(new_cols[c]) != self.hash_schema_part(old_cols[c]):
                            alerts.append({
                                'severity': 'CRITICAL',
                                'description': f"Column '{c}' in table '{t}' modified",
                                'timestamp': time.time(),
                                'type': 'SchemaTempering',
                                'table': t,
                                'column': c,
                                'change': 'column_modified'
                            })

                # Compare indexes and constraints - simplified as hash comparison
                if self.hash_schema_part(new_table.get('indexes', [])) != self.hash_schema_part(old_table.get('indexes', [])):
                    alerts.append({
                        'severity': 'WARNING',
                        'description': f"Indexes changed in table '{t}'",
                        'timestamp': time.time(),
                        'type': 'SchemaTempering',
                        'table': t,
                        'change': 'indexes_changed'
                    })

                if self.hash_schema_part(new_table.get('constraints', [])) != self.hash_schema_part(old_table.get('constraints', [])):
                    alerts.append({
                        'severity': 'CRITICAL',
                        'description': f"Constraints changed in table '{t}'",
                        'timestamp': time.time(),
                        'type': 'SchemaTempering',
                        'table': t,
                        'change': 'constraints_changed'
                    })

        return alerts

    def run(self):
        # Get current schema from DB client
        current_schema = self.db_client.get_schema()

        if not self.baseline_schema:
            # First run - save baseline
            self.save_baseline(current_schema)
            return []

        alerts = self.detect_changes(self.baseline_schema, current_schema)

        # Update baseline if no critical alerts or according to policy
        if not any(a for a in alerts if a['severity'] == 'CRITICAL'):
            self.save_baseline(current_schema)

        return alerts


# Example dummy DB client for testing

class DummyDBClient:
    def get_schema(self):
        # Example schema snapshot for testing
        return {
            'tables': {
                'users': {
                    'columns': {
                        'id': {'type': 'int', 'nullable': False, 'default': None},
                        'email': {'type': 'varchar', 'nullable': False, 'default': None},
                        'name': {'type': 'varchar', 'nullable': True, 'default': None},
                    },
                    'indexes': ['PRIMARY KEY (id)'],
                    'constraints': [],
                },
                'orders': {
                    'columns': {
                        'order_id': {'type': 'int', 'nullable': False, 'default': None},
                        'user_id': {'type': 'int', 'nullable': False, 'default': None},
                        'amount': {'type': 'decimal', 'nullable': False, 'default': '0.0'},
                    },
                    'indexes': ['PRIMARY KEY (order_id)'],
                    'constraints': ['FOREIGN KEY (user_id) REFERENCES users(id)'],
                }
            }
        }


if __name__ == "__main__":
    detector = SchemaTemperingDetector(db_client=DummyDBClient())
    alerts = detector.run()
    for alert in alerts:
        print(alert)
