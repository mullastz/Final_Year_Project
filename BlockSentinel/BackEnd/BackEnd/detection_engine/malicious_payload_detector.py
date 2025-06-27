import re
import requests

class MaliciousPayloadDetector:
    def __init__(self):
        # Patterns to detect common attack payloads (SQLi, XSS, Command Injection, etc.)
        self.patterns = {
            'sql_injection': re.compile(
                r"(\b(select|update|delete|insert|drop|union|create|alter|cast|exec|execute)\b|--|;|/\*|\*/|xp_)",
                re.IGNORECASE
            ),
            'xss': re.compile(
                r"(<script.*?>.*?</script.*?>|<.*?on\w+=['\"].*?['\"].*?>|javascript:|<iframe.*?>|<img.*?src=)",
                re.IGNORECASE | re.DOTALL
            ),
            'command_injection': re.compile(
                r"(\b(ls|cat|wget|curl|rm|touch|chmod|chown|ping|netcat|nc|bash|sh|powershell|cmd)\b|`|\$\(.*?\)|\|)",
                re.IGNORECASE
            ),
            'path_traversal': re.compile(
                r"(\.\./|\.\.\\|/etc/passwd|/etc/shadow|boot.ini|/proc/self/environ)",
                re.IGNORECASE
            ),
            'rce': re.compile(
                r"(base64_decode|eval\(|system\(|shell_exec\(|passthru\(|popen\(|proc_open\()",
                re.IGNORECASE
            ),
            'xml_external_entity': re.compile(
                r"(<!DOCTYPE\s+[^>]+>|<!ENTITY\s+[^>]+>)",
                re.IGNORECASE
            ),
            'sqlmap_fingerprint': re.compile(
                r"(sqlmap|sqlmap tamper|sqlmap fingerprint|sqlmap injection)",
                re.IGNORECASE
            ),
            'common_webshell': re.compile(
                r"(c99shell|r57shell|webshell|cmdshell)",
                re.IGNORECASE
            ),
        }

        # Suspicious keywords often used in payloads
        self.suspicious_keywords = [
            "sleep", "benchmark", "union select", "load_file", "outfile", "into dumpfile",
            "exec xp_", "information_schema", "waitfor delay", "or 1=1", "or true"
        ]

    def detect(self, input_data: str) -> dict:
        """
        Detect malicious payload in input string.
        Returns:
            dict: {
                'is_malicious': bool,
                'detections': list of detected patterns or keywords,
                'payload': original input_data
            }
        """
        if not input_data:
            return {'is_malicious': False, 'detections': [], 'payload': input_data}

        detections = []

        # Check regex patterns
        for name, pattern in self.patterns.items():
            if pattern.search(input_data):
                detections.append(name)

        # Check suspicious keywords (case insensitive)
        lowered = input_data.lower()
        for keyword in self.suspicious_keywords:
            if keyword in lowered:
                detections.append(f"keyword:{keyword}")

        is_malicious = len(detections) > 0
        return {
            'is_malicious': is_malicious,
            'detections': list(set(detections)),  # unique detections
            'payload': input_data
        }

def report_anomaly(event: dict):
    try:
        res = requests.post("http://127.0.0.1:8000/auditlog/anomalies/", json=event)
        res.raise_for_status()
        print(f"[✔] Anomaly saved: {event['event_type']} from IP {event['metadata'].get('ip')}")
    except Exception as e:
        print(f"[X] Failed to save anomaly: {e}")


# Example usage
if __name__ == "__main__":
    detector = MaliciousPayloadDetector()
    test_payloads = [
        "1 OR 1=1; --",
        "<script>alert('XSS')</script>",
        "`rm -rf /`",
        "../etc/passwd",
        "sleep(10)",
        "union select username, password from users",
        "normal harmless text"
    ]

    for payload in test_payloads:
        result = detector.detect(payload)
        print(f"Payload: {payload}\nDetected: {result['is_malicious']}\nDetections: {result['detections']}\n")
