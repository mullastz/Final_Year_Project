import time
from collections import defaultdict, deque
import re
import requests

def report_anomaly(system_id, user_or_ip, event_type, description, metadata):
    try:
        response = requests.post("http://127.0.0.1:8000/auditlog/anomalies/", json={
            "system_id": system_id,
            "user": user_or_ip,
            "event_type": event_type,
            "description": description,
            "severity": "CRITICAL",
            "metadata": metadata
        })
        response.raise_for_status()
        print(f"[✔] Anomaly reported: {event_type}")
    except Exception as e:
        print(f"[X] Failed to report anomaly: {e}")


class APIAbuseDetector:
    def __init__(self, max_requests_per_minute=60, max_burst=20):
        # Track user or IP request timestamps (for rate limiting and burst detection)
        self.request_logs = defaultdict(deque)  # {user_or_ip: deque[timestamp]}
        self.max_requests_per_minute = max_requests_per_minute
        self.max_burst = max_burst
        
        # Common suspicious user agents (bots, scanners)
        self.suspicious_user_agents = [
            re.compile(pattern, re.IGNORECASE) for pattern in [
                r"sqlmap", r"nikto", r"curl", r"wget", r"python-requests", r"libwww-perl",
                r"nmap", r"masscan", r"crawler", r"bot", r"scan", r"scanner"
            ]
        ]

        # Whitelist valid API keys/tokens (should be replaced with your real keys/tokens)
        self.valid_api_keys = {"valid_api_key_1", "valid_api_key_2"}

    def detect_rate_limit(self, user_or_ip):
        """Detect if requests exceed max_requests_per_minute."""
        now = time.time()
        logs = self.request_logs[user_or_ip]

        # Remove timestamps older than 60 seconds
        while logs and now - logs[0] > 60:
            logs.popleft()

        # Check current number of requests in last 60 seconds
        if len(logs) >= self.max_requests_per_minute:
            return True

        logs.append(now)
        return False

    def detect_burst(self, user_or_ip):
        """Detect if more than max_burst requests in last 5 seconds (burst attack)."""
        now = time.time()
        logs = self.request_logs[user_or_ip]

        # Remove timestamps older than 5 seconds
        while logs and now - logs[0] > 5:
            logs.popleft()

        if len(logs) >= self.max_burst:
            return True

        logs.append(now)
        return False

    def detect_suspicious_user_agent(self, user_agent):
        if not user_agent:
            return False
        for pattern in self.suspicious_user_agents:
            if pattern.search(user_agent):
                return True
        return False

    def detect_invalid_api_key(self, api_key):
        return api_key not in self.valid_api_keys

    def detect_anomalous_pattern(self, endpoints_accessed):
        """
        endpoints_accessed: list of endpoint paths accessed by the user/ip recently
        Detect if the user accesses too many different endpoints in a short period.
        """
        # Threshold for anomaly (e.g. more than 10 distinct endpoints in last N mins)
        MAX_DISTINCT_ENDPOINTS = 10
        if len(set(endpoints_accessed)) > MAX_DISTINCT_ENDPOINTS:
            return True
        return False

    def detect(self, user_or_ip, user_agent, api_key, endpoints_accessed, system_id="unknown-system"):
        alerts = {}

        alerts['rate_limit_exceeded'] = self.detect_rate_limit(user_or_ip)
        alerts['burst_detected'] = self.detect_burst(user_or_ip)
        alerts['suspicious_user_agent'] = self.detect_suspicious_user_agent(user_agent)
        alerts['invalid_api_key'] = self.detect_invalid_api_key(api_key)
        alerts['anomalous_endpoint_pattern'] = self.detect_anomalous_pattern(endpoints_accessed)

        alerts['is_abuse'] = any(alerts.values())

        if alerts['is_abuse']:
            triggered = [k for k, v in alerts.items() if v and k != 'is_abuse']
            report_anomaly(
                system_id=system_id,
                user_or_ip=user_or_ip,
                event_type="API Abuse",
                description=f"Triggered: {', '.join(triggered)}",
                metadata={
                    "user_agent": user_agent,
                    "api_key": api_key,
                    "endpoints": endpoints_accessed,
                    "triggers": triggered
                }
            )

        return alerts



# Example usage
if __name__ == "__main__":
    detector = APIAbuseDetector(max_requests_per_minute=100, max_burst=30)

    user_ip = "192.168.1.100"
    user_agent = "sqlmap/1.4"
    api_key = "invalid_key"
    endpoints = ["/api/login", "/api/data", "/api/admin", "/api/data", "/api/login", "/api/logout", "/api/config", "/api/stats", "/api/users", "/api/settings", "/api/logs"]

    # Simulate multiple calls to check rate limiting and bursts
    for _ in range(50):
        abuse_result = detector.detect(user_ip, user_agent, api_key, endpoints)
        print(abuse_result)
        if abuse_result['is_abuse']:
            print("API Abuse detected!")
            break

