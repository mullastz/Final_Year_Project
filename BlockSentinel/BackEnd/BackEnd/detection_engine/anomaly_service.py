import logging
from datetime import datetime

from .sql_injection_detector import SQLInjectionDetector
from .unusual_login_detector import UnusualLoginDetector
from .ip_reputation_checker import IPReputationChecker
from .malicious_payload_detector import MaliciousPayloadDetector
from .api_abuse_detector import APIAbuseDetector
from .unauthorized_system_change_detector import UnauthorizedSystemChangeDetector
from .schema_tampering_detector import SchemaTemperingDetector
from .unauthorized_access_detector import UnauthorizedAccessDetector
from .combined_anomaly_checker import CombinedAnomalyDetector
from auditlog.models import MonitoredEvent 

logger = logging.getLogger("anomaly_service")

def default_event_source():
        """
        Return latest events for anomaly analysis.
        """
        return MonitoredEvent.objects.order_by("-timestamp")[:50].values()


class AnomalyDetectionService:
    def __init__(self, db_client=None, event_source=None):

        if db_client is None:
            raise ValueError("db_client is required for SchemaTemperingDetector")

        if event_source is None:
            event_source = default_event_source  # ✅ Use callable
 

        self.sql_detector = SQLInjectionDetector()
        self.login_detector = UnusualLoginDetector()
        self.ip_checker = IPReputationChecker()
        self.payload_detector = MaliciousPayloadDetector()
        self.api_abuse = APIAbuseDetector()
        self.sys_change = UnauthorizedSystemChangeDetector()
        self.schema_tamper = SchemaTemperingDetector(db_client=db_client)
        self.unauth_access = UnauthorizedAccessDetector(event_source=event_source)
        self.combined = CombinedAnomalyDetector(
        db_client=db_client,
        event_source=event_source
        )
  
   
    def detect_all(self, system_id: str, user: str, payload: str, user_agent: str, ip: str,
                   login_time: str, api_path: str, action: str,
                   schema_snapshot: dict = None, os_snapshot: dict = None) -> list:
        """
        Run all detectors and return a list of detected anomalies.
        """
        anomalies = []

        # Individual detectors
        if self.sql_detector.detect(payload, user_agent, system_id, user)['sql_injection_detected']:
            anomalies.append({
                "system_id": system_id,
                "user": user,
                "event_type": "SQLInjection",
                "description": "SQL injection detected in request payload.",
                "severity": "CRITICAL",
                "source": "AnomalyEngine",
                "metadata": {
                    "payload": payload,
                    "user_agent": user_agent
                }
            })

        if self.login_detector.detect(user, ip, datetime.strptime(login_time, "%H:%M"))['unusual_login']:
            anomalies.append({
                "system_id": system_id,
                "user": user,
                "event_type": "UnusualLoginTime",
                "description": f"Unusual login time: {login_time} from {ip}",
                "severity": "WARNING",
                "source": "AnomalyEngine",
                "metadata": {"login_time": login_time, "ip": ip}
            })

        ip_result = self.ip_checker.check_ip(ip, system_id, user)
        if ip_result.get('status') == 'blocked':
            anomalies.append({
                "system_id": system_id,
                "user": user,
                "event_type": "BadIPReputation",
                "description": f"Suspicious IP address: {ip}",
                "severity": "CRITICAL",
                "source": "AnomalyEngine",
                "metadata": ip_result
            })

        payload_result = self.payload_detector.detect(payload)
        if payload_result.get('is_malicious'):
            anomalies.append({
                "system_id": system_id,
                "user": user,
                "event_type": "MaliciousPayload",
                "description": "Malicious content detected in request payload.",
                "severity": "CRITICAL",
                "source": "AnomalyEngine",
                "metadata": payload_result
            })

        abuse_result = self.api_abuse.detect(
            user_or_ip=ip,
            user_agent=user_agent,
            api_key="unknown",
            endpoints_accessed=[api_path],
            system_id=system_id
        )
        if abuse_result.get("is_abuse"):
            anomalies.append({
                "system_id": system_id,
                "user": user,
                "event_type": "APIAbuse",
                "description": "Abnormal API usage pattern detected.",
                "severity": "WARNING",
                "source": "AnomalyEngine",
                "metadata": abuse_result
            })

        # System change detection
        for alert in self.sys_change.detect_unauthorized_changes():
            anomalies.append({
                "system_id": system_id,
                "user": user,
                "event_type": alert['type'],
                "description": alert['description'],
                "severity": alert['severity'],
                "source": "AnomalyEngine",
                "metadata": {
                    "file": alert['file'],
                    "timestamp": alert['timestamp']
                }
            })

        # Schema tampering detection
        for alert in self.schema_tamper.run():
            anomalies.append({
                "system_id": system_id,
                "user": user,
                "event_type": alert['type'],
                "description": alert['description'],
                "severity": alert['severity'],
                "source": "AnomalyEngine",
                "metadata": {
                    "table": alert.get('table'),
                    "column": alert.get('column'),
                    "change": alert['change'],
                    "timestamp": alert['timestamp']
                }
            })

        # Unauthorized access
        for alert in self.unauth_access.detect():
            anomalies.append({
                "system_id": system_id,
                "user": alert.get("user"),
                "event_type": alert['type'],
                "description": alert['description'],
                "severity": alert['severity'],
                "source": "AnomalyEngine",
                "metadata": alert.get("metadata", {})
            })

        # Combined anomaly analysis
        combined_alerts = self.combined.detect()
        for alert in combined_alerts:
            anomalies.append({
                "system_id": system_id,
                "user": alert.get("user"),
                "event_type": alert.get("type"),
                "description": alert.get("description"),
                "severity": alert.get("severity"),
                "source": "AnomalyEngine",
                "metadata": alert.get("metadata", {})
            })

        return anomalies
