import time
from collections import defaultdict
from datetime import datetime, timedelta

class UnauthorizedAccessDetector:
    def __init__(self, event_source, allowed_users=None, max_failed_attempts=5, lockout_period_seconds=300, allowed_login_hours=(6, 22)):
        """
        event_source: iterable or method returning recent access events with fields:
          - user (str)
          - ip (str)
          - event_type (str): e.g., 'login_success', 'login_failed', 'access_resource'
          - timestamp (datetime)
          - resource (optional, str)

        allowed_users: set of usernames allowed to access the system
        max_failed_attempts: number of failed logins allowed before raising alert
        lockout_period_seconds: time window for counting failed attempts
        allowed_login_hours: tuple (start_hour, end_hour) in 24h format for allowed login times
        """
        self.event_source = event_source
        self.allowed_users = allowed_users or set()
        self.max_failed_attempts = max_failed_attempts
        self.lockout_period = timedelta(seconds=lockout_period_seconds)
        self.allowed_login_hours = allowed_login_hours

        # Internal state
        self.failed_attempts = defaultdict(list)  # key: user or ip, value: list of timestamps

    def detect(self):
        alerts = []
        now = datetime.now()

        for event in self.event_source():
            user = event.get('user')
            ip = event.get('ip')
            event_type = event.get('event_type')
            timestamp = event.get('timestamp')
            resource = event.get('resource', None)

            # Detect unknown users
            if user and user not in self.allowed_users and event_type == 'login_success':
                alerts.append({
                    'severity': 'CRITICAL',
                    'description': f'Unauthorized login by unknown user "{user}" from IP {ip}',
                    'timestamp': timestamp,
                    'type': 'UnauthorizedAccess',
                    'user': user,
                    'ip': ip
                })

            # Detect failed login attempts
            if event_type == 'login_failed':
                self.failed_attempts[user].append(timestamp)
                self.failed_attempts[ip].append(timestamp)

                # Clean up old attempts
                self.failed_attempts[user] = [t for t in self.failed_attempts[user] if now - t <= self.lockout_period]
                self.failed_attempts[ip] = [t for t in self.failed_attempts[ip] if now - t <= self.lockout_period]

                # Alert if too many failed attempts
                if len(self.failed_attempts[user]) > self.max_failed_attempts:
                    alerts.append({
                        'severity': 'CRITICAL',
                        'description': f'Brute force attack suspected: More than {self.max_failed_attempts} failed logins for user "{user}" within {self.lockout_period.seconds//60} minutes.',
                        'timestamp': timestamp,
                        'type': 'UnauthorizedAccess',
                        'user': user,
                        'ip': ip
                    })

                if len(self.failed_attempts[ip]) > self.max_failed_attempts:
                    alerts.append({
                        'severity': 'CRITICAL',
                        'description': f'Brute force attack suspected: More than {self.max_failed_attempts} failed logins from IP {ip} within {self.lockout_period.seconds//60} minutes.',
                        'timestamp': timestamp,
                        'type': 'UnauthorizedAccess',
                        'user': user,
                        'ip': ip
                    })

            # Detect login outside allowed hours
            if event_type == 'login_success' and timestamp:
                login_hour = timestamp.hour
                start, end = self.allowed_login_hours
                if login_hour < start or login_hour >= end:
                    alerts.append({
                        'severity': 'WARNING',
                        'description': f'Login outside allowed hours by user "{user}" at {timestamp.strftime("%H:%M")}',
                        'timestamp': timestamp,
                        'type': 'UnauthorizedAccess',
                        'user': user,
                        'ip': ip
                    })

            # Optionally, detect suspicious resource access
            # Example: unauthorized access to admin panel
            if event_type == 'access_resource' and resource:
                # You can add logic to check if user is authorized for the resource
                if user not in self.allowed_users:
                    alerts.append({
                        'severity': 'CRITICAL',
                        'description': f'Unauthorized resource access attempt by user "{user}" to resource "{resource}"',
                        'timestamp': timestamp,
                        'type': 'UnauthorizedAccess',
                        'user': user,
                        'ip': ip
                    })

        return alerts


# Example usage with dummy event source

def dummy_event_source():
    now = datetime.now()
    return [
        {'user': 'alice', 'ip': '192.168.1.10', 'event_type': 'login_failed', 'timestamp': now - timedelta(seconds=50)},
        {'user': 'alice', 'ip': '192.168.1.10', 'event_type': 'login_failed', 'timestamp': now - timedelta(seconds=40)},
        {'user': 'alice', 'ip': '192.168.1.10', 'event_type': 'login_failed', 'timestamp': now - timedelta(seconds=30)},
        {'user': 'alice', 'ip': '192.168.1.10', 'event_type': 'login_failed', 'timestamp': now - timedelta(seconds=20)},
        {'user': 'alice', 'ip': '192.168.1.10', 'event_type': 'login_failed', 'timestamp': now - timedelta(seconds=10)},
        {'user': 'unknown_user', 'ip': '192.168.1.20', 'event_type': 'login_success', 'timestamp': now},
        {'user': 'bob', 'ip': '192.168.1.15', 'event_type': 'login_success', 'timestamp': now.replace(hour=3)},  # login at 3 AM
    ]

if __name__ == "__main__":
    allowed_users = {'alice', 'bob', 'charlie'}
    detector = UnauthorizedAccessDetector(dummy_event_source, allowed_users=allowed_users)
    alerts = detector.detect()
    for alert in alerts:
        print(alert)
