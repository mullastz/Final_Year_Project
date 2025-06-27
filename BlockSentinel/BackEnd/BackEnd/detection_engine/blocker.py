import logging
from datetime import datetime
import requests
from datetime import timedelta

logger = logging.getLogger(__name__)

class AnomalyBlocker:
    def __init__(self):
        self.blocked_ips = {}
        self.locked_users = {}
        self.cooldown = timedelta(minutes=5)

    def block(self, alerts):
        for alert in alerts:
            timestamp = alert["timestamp"]
            ip = alert.get("ip")
            user = alert.get("user")
            action = None


            if alert["type"] == "SQL_INJECTION":
                action_taken = self._block_ip(alert["ip"])
                self._log_block("SQL Injection", alert, action_taken)

            elif alert["type"] == "UNUSUAL_LOGIN":
                action_taken = self._lock_user(alert["user"])
                self._log_block("Unusual Login", alert, action_taken)

            elif alert["type"] == "IP_REPUTATION":
                action_taken = self._block_ip(alert["ip"])
                self._log_block("Malicious IP", alert, action_taken)

            elif alert["type"] == "MALICIOUS_PAYLOAD":
                action_taken = self._block_request_signature(alert["metadata"].get("payload_hash"))
                self._log_block("Payload Attack", alert, action_taken)

            elif alert["type"] == "API_ABUSE":
                action_taken = self._rate_limit_ip(alert["ip"])
                self._log_block("API Abuse", alert, action_taken)

            elif alert["type"] == "UNAUTHORIZED_ACCESS":
                action_taken = self._lock_user(alert["user"])
                self._log_block("Unauthorized Access", alert, action_taken)

            elif alert["type"] == "SCHEMA_TAMPERING":
                action_taken = self._isolate_db(alert["system_id"])
                self._log_block("Schema Tampering", alert, action_taken)

            else:
                self._log_block("Unknown Threat", alert, "No action")

    def _block_ip(self, ip, now):
        if not ip:
            return "No IP provided"
        last_block = self.blocked_ips.get(ip)
        if not last_block or now - last_block > self.cooldown:
            self.blocked_ips[ip] = now
            return f"Blocked IP {ip}"
        return f"IP {ip} already blocked recently"

    def _lock_user(self, user, now):
        if not user:
            return "No user provided"
        last_lock = self.locked_users.get(user)
        if not last_lock or now - last_lock > self.cooldown:
            self.locked_users[user] = now
            return f"User {user} locked"
        return f"User {user} already locked recently"

    def _rate_limit(self, ip):
        return f"Rate-limiting IP {ip}"

    def _isolate_system(self, system_id):
        return f"System {system_id} isolated"

    def _log_action(self, alert, action):
        print(f"[BLOCKED] [{alert['severity']}] {alert['type']} - {alert['description']} => {action}")
        self._report_anomaly(alert)

    def _report_anomaly(self, alert):
        try:
            res = requests.post("http://127.0.0.1:8000/auditlog/anomalies/", json={
                "system_id": alert.get("system_id", "unknown"),
                "user": alert.get("user"),
                "event_type": alert.get("type"),
                "description": alert.get("description"),
                "severity": alert.get("severity", "CRITICAL"),
                "metadata": alert.get("metadata", {}),
            })
            res.raise_for_status()
            print(f"[✔] Saved anomaly: {alert['type']}")
        except Exception as e:
            print(f"[✘] Failed to save anomaly: {e}")


if __name__ == "__main__":
    from combined_anomaly_checker import CombinedAnomalyDetector

    def example_event_source():
        yield {
            "type": "SQL_INJECTION",
            "ip": "192.168.1.66",
            "user": "hacker",
            "description": "Detected SQL injection payload in /login route",
            "timestamp": datetime.now().isoformat(),
            "severity": "CRITICAL",
            "metadata": {}
        }

    detector = CombinedAnomalyDetector(example_event_source)
    alerts = detector.detect()

    # Run blocker
    blocker = AnomalyBlocker()
    blocker.block(alerts)

