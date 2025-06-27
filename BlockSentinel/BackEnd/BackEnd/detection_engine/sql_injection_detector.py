import re
import math
import requests
import datetime

class SQLInjectionDetector:
    # Common SQLi patterns & keywords to detect
    SQLI_PATTERNS = [
        r"(\bUNION\b.*\bSELECT\b)",            # UNION SELECT pattern
        r"(\bSELECT\b.+\bFROM\b)",             # SELECT ... FROM
        r"(\bINSERT\b.+\bINTO\b)",             # INSERT INTO
        r"(\bUPDATE\b.+\bSET\b)",              # UPDATE ... SET
        r"(\bDELETE\b.+\bFROM\b)",             # DELETE FROM
        r"(\bDROP\b.+\bTABLE\b)",              # DROP TABLE
        r"(\bOR\b.+=)",                        # OR something =
        r"(--|#|;)",                           # SQL comment or statement terminator
        r"(\bEXEC\b|\bEXECUTE\b)",             # EXEC EXECUTE commands
        r"(\bSLEEP\b\()",                      # SLEEP() used in time-based blind SQLi
        r"(/\*.*\*/)",                        # SQL comment block
        r"(?i)union(\s+all)?(\s*select)?",    # union select with optional all
        r"(?i)benchmark\((\s*\w+\s*,)",       # benchmark function (MySQL)
        r"(?i)load_file\(",                    # load_file function
        r"(?i)information_schema",             # information_schema queries
    ]

    # Known suspicious User-Agent signatures (commonly SQLmap etc)
    SQLI_USER_AGENTS = [
        r"sqlmap", r"sqlmap\slabs", r"sqlmap\stool", r"sqlninja", r"havij", r"acunetix",
        r"nmap", r"nikto", r"curl", r"wget", r"python-requests"
    ]

    def __init__(self):
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.SQLI_PATTERNS]
        self.compiled_agents = [re.compile(p, re.IGNORECASE) for p in self.SQLI_USER_AGENTS]

    def check_payload(self, input_str: str) -> bool:
        if not input_str:
            return False
        
        # Check for known SQLi pattern matches
        for pattern in self.compiled_patterns:
            if pattern.search(input_str):
                return True
        
        # Check for suspicious characters and keywords frequency
        suspicious_chars = ['\'', '"', ';', '--', '#', '/*', '*/', '=']
        count = sum(input_str.count(c) for c in suspicious_chars)
        if count > 3:
            return True
        
        # Check entropy - higher entropy means random payload
        if self._entropy(input_str) > 4.0:
            return True
        
        return False

    def check_user_agent(self, user_agent: str) -> bool:
        if not user_agent:
            return False
        for pattern in self.compiled_agents:
            if pattern.search(user_agent):
                return True
        return False

    def _entropy(self, data: str) -> float:
        # Calculate Shannon entropy to find randomness
        if not data:
            return 0
        entropy = 0
        length = len(data)
        frequencies = {}
        for c in data:
            frequencies[c] = frequencies.get(c, 0) + 1
        for freq in frequencies.values():
            p = freq / length
            entropy -= p * math.log2(p)
        return entropy

    def detect(self, payload: str, user_agent: str = None, system_id: str = "unknown", user: str = "unknown") -> dict:
        """Detect SQLi in payload + optionally user_agent string and save if found."""
        alert = {
            'sql_injection_detected': False,
            'reason': '',
        }

        # Check user agent
        if user_agent and self.check_user_agent(user_agent):
            alert['sql_injection_detected'] = True
            alert['reason'] = "Suspicious User-Agent detected"
            self._report_anomaly(system_id, user, "SQL Injection", alert['reason'], payload, user_agent)
            return alert

        # Check payload
        if self.check_payload(payload):
            alert['sql_injection_detected'] = True
            alert['reason'] = "Suspicious payload detected"
            self._report_anomaly(system_id, user, "SQL Injection", alert['reason'], payload, user_agent)
            return alert

        return alert

    def _report_anomaly(self, system_id, user, event_type, description, payload, user_agent):
        anomaly_data = {
            "system_id": system_id,
            "user": user,
            "event_type": event_type,
            "description": description,
            "severity": "CRITICAL",
            "source": "AnomalyEngine",
            "metadata": {
                "payload": payload,
                "user_agent": user_agent
            }
        }

        try:
            response = requests.post("http://127.0.0.1:8000/auditlog/anomalies/", json=anomaly_data)
            response.raise_for_status()
            print(f"[✔] Anomaly saved: {event_type} on {system_id}")
        except Exception as e:
            print(f"[X] Failed to report anomaly: {e}")