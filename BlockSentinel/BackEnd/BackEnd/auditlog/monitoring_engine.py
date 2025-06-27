import psycopg2
import mysql.connector
from pymongo import MongoClient
import threading
import time
import logging
import requests
from datetime import datetime

logging.basicConfig(
    format='[%(asctime)s] %(levelname)s - %(message)s',
    level=logging.INFO
)

class MongoDBConnector:
    def __init__(self, config):
        self.config = config
        self.client = MongoClient(**config)
        self.db = self.client[config['database']]

    def list_tables(self, db_name):
        return self.db.list_collection_names()

    def list_users(self):
        admin_db = self.client['admin']
        users_info = admin_db.command("usersInfo")
        return [user['user'] for user in users_info.get('users', [])]

class PostgresConnector:
    def __init__(self, config):
        self.config = config
        self.conn = psycopg2.connect(**config)

    def list_tables(self, db_name):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            return [row[0] for row in cur.fetchall()]

    def list_users(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT usename FROM pg_user")
            return [row[0] for row in cur.fetchall()]

class MySQLConnector:
    def __init__(self, config):
        self.config = config
        self.conn = mysql.connector.connect(**config)

    def list_tables(self, db_name):
        with self.conn.cursor() as cur:
            cur.execute("SHOW TABLES")
            return [row[0] for row in cur.fetchall()]

    def list_users(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT User FROM mysql.user")
            return [row[0] for row in cur.fetchall()]

class MonitoringAgent:
    def __init__(self, system_id, backend_url, db_configs: dict, poll_interval=60):
        self.system_id = system_id
        self.backend_url = backend_url.rstrip('/')
        self.db_configs = db_configs
        self.poll_interval = poll_interval
        self.running = True

        self.db_connectors = {}
        for db_type, cfg in db_configs.items():
            if db_type == 'PostgreSQL':
                self.db_connectors[db_type] = PostgresConnector(cfg)
            elif db_type == 'MySQL':
                self.db_connectors[db_type] = MySQLConnector(cfg)
            elif db_type == 'MongoDB':
                self.db_connectors[db_type] = MongoDBConnector(cfg)
            elif db_type == 'MSSQL':
                self.db_connectors[db_type] = MySQLConnector(cfg)  # or create MSSQLConnector

        self.known_tables = {}
        self.known_users = {}

    def _send_events(self, events):
        if not events:
            return
        headers = {
            'Content-Type': 'application/json',
        }
        try:
            # Send to anomaly analysis endpoint
            url = f"{self.backend_url}/auditlog/analyze/"
            resp = requests.post(url, headers=headers, json=events, timeout=10)
            resp.raise_for_status()
            logging.info(f"Sent {len(events)} events for anomaly analysis successfully")
        except Exception as e:
            logging.error(f"Failed to send events for anomaly analysis: {e}")

    def _build_event(self, event_type, description, user=None, severity='INFO', metadata=None, db_type=None, table=None):
        event = {
            'system_id': self.system_id,
            'user': user,
            'event_type': event_type,
            'description': description,
            'source': 'MONITOR_AGENT',
            'severity': severity,
            'timestamp': datetime.utcnow().isoformat(),
            'metadata': metadata or {},
        }
        if db_type:
            event['metadata']['db_type'] = db_type
        if table:
            event['metadata']['table'] = table
        return event

    def _monitor_db(self, db_type, connector):
        target_db = self.db_configs[db_type].get('database')
        self.known_tables[db_type] = set()
        self.known_users[db_type] = set()

        while self.running:
            try:
                current_tables = set(connector.list_tables(target_db))
                known_tables = self.known_tables[db_type]
                added_tables = current_tables - known_tables
                removed_tables = known_tables - current_tables

                events = []

                for tbl in added_tables:
                    events.append(self._build_event('NewTableCreated', f"Table '{tbl}' created in database '{target_db}'", db_type=db_type, table=tbl))
                for tbl in removed_tables:
                    events.append(self._build_event('TableDeleted', f"Table '{tbl}' deleted from database '{target_db}'", db_type=db_type, table=tbl))

                current_users = set(connector.list_users())
                known_users = self.known_users[db_type]
                added_users = current_users - known_users
                removed_users = known_users - current_users

                for user in added_users:
                    events.append(self._build_event('DBUserCreated', f"Database user '{user}' created", db_type=db_type))
                for user in removed_users:
                    events.append(self._build_event('DBUserDeleted', f"Database user '{user}' deleted", db_type=db_type))

                self.known_tables[db_type] = current_tables
                self.known_users[db_type] = current_users

                if events:
                    self._send_events(events)

            except Exception as e:
                logging.error(f"Error monitoring {db_type} DB: {e}")

            time.sleep(self.poll_interval)

    def _run_monitor_db(self):
        threads = []
        for db_type, connector in self.db_connectors.items():
            t = threading.Thread(target=self._monitor_db, args=(db_type, connector), daemon=True)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

    def run(self):
        logging.info(f"Starting MonitoringAgent for system {self.system_id}")
        threading.Thread(target=self._run_monitor_db, daemon=True).start()

        while self.running:
            try:
                resp = requests.get(f"{self.backend_url}/health-check/{self.system_id}/", timeout=5)
                if resp.status_code == 200:
                    logging.info(f"System {self.system_id} is alive")
                else:
                    logging.warning(f"Health check returned {resp.status_code}")
            except Exception as e:
                logging.error(f"Health check failed: {e}")
            time.sleep(300)

def start_monitoring_agent(system_id, backend_url, db_configs, poll_interval=60):
    agent = MonitoringAgent(system_id, backend_url, db_configs, poll_interval)
    thread = threading.Thread(target=agent.run, daemon=True)
    thread.start()
    return agent
