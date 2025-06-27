import requests
import time
import ipaddress
from geolite2 import geolite2

class IPReputationChecker:
    def __init__(self, local_blacklist=None, tor_exit_nodes_file=None):
        # Local blacklist (set of IP strings)
        self.local_blacklist = set(local_blacklist or [])
        self.geo_reader = geolite2.reader()
        self.tor_exit_nodes = set()
        if tor_exit_nodes_file:
            self.load_tor_exit_nodes(tor_exit_nodes_file)
        self.cache = {}

    def load_tor_exit_nodes(self, filepath):
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    ip = line.strip()
                    if ip and not ip.startswith('#'):
                        self.tor_exit_nodes.add(ip)
        except Exception as e:
            print(f"Failed to load Tor exit nodes file: {e}")

    def is_ip_valid(self, ip):
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    def is_blacklisted_locally(self, ip):
        return ip in self.local_blacklist

    def is_tor_exit_node(self, ip):
        return ip in self.tor_exit_nodes

    def check_threat_intelligence_api(self, ip):
        # Placeholder for external API call to check IP reputation
        # Use free services like AbuseIPDB, VirusTotal, or commercial APIs
        # Example (fake): return True if IP is malicious else False

        # To avoid rate limits, cache results for 1 hour
        if ip in self.cache and (time.time() - self.cache[ip]['timestamp']) < 3600:
            return self.cache[ip]['malicious']

        # Here you should implement your actual API request
        # response = requests.get(f"https://api.abuseipdb.com/api/v2/check?ipAddress={ip}", headers={...})
        # parse response to decide if malicious

        # For demo, we fake:
        malicious = False

        # Cache the result
        self.cache[ip] = {'timestamp': time.time(), 'malicious': malicious}
        return malicious

    def get_geo_info(self, ip):
        try:
            geo = self.geo_reader.get(ip)
            if geo:
                country = geo.get('country', {}).get('names', {}).get('en', 'Unknown')
                city = geo.get('city', {}).get('names', {}).get('en', 'Unknown')
                return {'country': country, 'city': city}
            return {'country': 'Unknown', 'city': 'Unknown'}
        except Exception:
            return {'country': 'Unknown', 'city': 'Unknown'}

    def check_ip(self, ip, system_id=None, user=None):
        if not self.is_ip_valid(ip):
            return {'status': 'invalid', 'reason': 'Invalid IP format'}

        reason = None

        if self.is_blacklisted_locally(ip):
            reason = 'IP is blacklisted locally'
        elif self.is_tor_exit_node(ip):
            reason = 'IP is a Tor exit node'
        elif self.check_threat_intelligence_api(ip):
            reason = 'IP flagged by threat intelligence API'

        if reason:
            # Save anomaly
            report_anomaly({
                "system_id": system_id or "unknown_system",
                "user": user or "unknown_user",
                "event_type": "Malicious IP Detected",
                "description": reason,
                "severity": "CRITICAL",
                "source": "IP_REPUTATION",
                "metadata": {
                    "ip": ip,
                    "reason": reason
                }
            })
            return {'status': 'blocked', 'reason': reason}

        geo_info = self.get_geo_info(ip)
        return {'status': 'clean', 'geo': geo_info}

def report_anomaly(event: dict):
    try:
        res = requests.post("http://127.0.0.1:8000/auditlog/anomalies/", json=event)
        res.raise_for_status()
        print(f"[✔] Anomaly saved: {event['event_type']} from IP {event['metadata'].get('ip')}")
    except Exception as e:
        print(f"[X] Failed to save anomaly: {e}")
