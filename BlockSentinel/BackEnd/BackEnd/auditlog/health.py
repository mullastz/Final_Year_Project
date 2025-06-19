import psutil
import socket
import requests
from datetime import datetime

class SystemHealthMonitor:

    def __init__(self):
        self.services = {
            'Core Engine': self.check_backend,
            'PostgreSQL Database': self.check_postgres,
            'Blockchain Node': self.check_blockchain_node,
            'Frontend': self.check_frontend,
            'Scheduler/Agent': self.check_scheduler,
        }

    def check_backend(self):
        return self.simple_check('http://localhost:8000/')

    def check_postgres(self):
        try:
            import psycopg2
            conn = psycopg2.connect(
                dbname='your_db',
                user='your_user',
                password='your_password',
                host='localhost',
                port='5432'
            )
            conn.close()
            return 'Running'
        except Exception:
            return 'Down'

    def check_blockchain_node(self):
        try:
            sock = socket.create_connection(('127.0.0.1', 7545), timeout=2)
            sock.close()
            return 'Running'
        except Exception:
            return 'Down'

    def check_frontend(self):
        return self.simple_check('http://localhost:4200/')

    def check_scheduler(self):
        # You can improve this based on how your scheduler runs (e.g., cron job, celery beat, etc.)
        return 'Running'

    def simple_check(self, url):
        try:
            res = requests.get(url, timeout=2)
            return 'Running' if res.status_code == 200 else 'Slow Sync'
        except:
            return 'Down'

    def get_all_statuses(self):
        results = []
        now = datetime.now().isoformat()
        for service, checker in self.services.items():
            status = checker()
            results.append({
                'service': service,
                'status': status,
                'lastChecked': now
            })
        return results
