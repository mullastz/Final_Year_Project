from datetime import datetime
import requests

# Import detectors
from detection_engine.ip_reputation_checker import IPReputationChecker
from detection_engine.malicious_payload_detector import MaliciousPayloadDetector
from detection_engine.api_abuse_detector import APIAbuseDetector
from detection_engine.unauthorized_access_detector import UnauthorizedAccessDetector
from detection_engine.schema_tampering_detector import SchemaTemperingDetector

class CombinedAnomalyDetector:
    def __init__(self, event_source, db_client, config=None):
        self.event_source = event_source
        self.config = config or {}

        # Init detectors
        self.ip_reputation = IPReputationChecker(**self.config.get("ip_reputation", {}))
        self.payload_detector = MaliciousPayloadDetector()
        self.api_abuse = APIAbuseDetector()
        self.unauth_access = UnauthorizedAccessDetector(event_source, **self.config.get("unauthorized", {}))
        self.schema_tempering_detector = SchemaTemperingDetector(db_client=db_client)

    def detect(self):
        alerts = []

        for event in self.event_source():
            ip = event.get("ip")
            user = event.get("user")
            system_id = event.get("system_id", "unknown")
            payload = event.get("payload", "")

            # 1. IP Reputation Check
            ip_result = self.ip_reputation.check_ip(ip, system_id=system_id, user=user)
            if ip_result["status"] == "blocked":
                alerts.append({
                    "type": "IP_REPUTATION",
                    "ip": ip,
                    "user": user,
                    "system_id": system_id,
                    "severity": "CRITICAL",
                    "description": f"IP Reputation block: {ip_result['reason']}",
                    "timestamp": datetime.now(),
                    "metadata": ip_result
                })

            # 2. Malicious Payload
            payload_result = self.payload_detector.detect(payload)
            if payload_result["is_malicious"]:
                alerts.append({
                    "type": "MALICIOUS_PAYLOAD",
                    "ip": ip,
                    "user": user,
                    "system_id": system_id,
                    "severity": "CRITICAL",
                    "description": f"Malicious payload detected: {', '.join(payload_result['detections'])}",
                    "timestamp": datetime.now(),
                    "metadata": payload_result
                })

            # 3. API Abuse (optional demo usage)
            abuse_result = self.api_abuse.detect(
                user_or_ip=ip,
                user_agent=event.get("user_agent", ""),
                api_key=event.get("api_key", ""),
                endpoints_accessed=event.get("endpoints", []),
                system_id=system_id
            )
            if abuse_result["is_abuse"]:
                alerts.append({
                    "type": "API_ABUSE",
                    "ip": ip,
                    "user": user,
                    "system_id": system_id,
                    "severity": "CRITICAL",
                    "description": f"API Abuse detected: {', '.join(k for k in abuse_result if abuse_result[k] and k != 'is_abuse')}",
                    "timestamp": datetime.now(),
                    "metadata": abuse_result
                })

        # 4. Schema Tampering
        alerts.extend(self.schema_tempering_detector.run())


        # 5. Unauthorized Access
        alerts.extend(self.unauth_access.detect())

        return self._deduplicate(alerts)

    def _deduplicate(self, alerts):
        seen = set()
        unique = []
        for alert in alerts:
            key = (alert["type"], alert["user"], alert["ip"], alert["description"])
            if key not in seen:
                seen.add(key)
                unique.append(alert)
        return unique


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

# Example usage with your event source
if __name__ == "__main__":
    # Replace with your actual event source function
    def example_event_source():
        # Yield events one by one or return a list of events
        yield from []

    detector = CombinedAnomalyDetector(example_event_source)
    results = detector.detect()
    for r in results:
        print(f"[{r['severity']}] {r['type']} - {r['description']} at {r['timestamp']}")
