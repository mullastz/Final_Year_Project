import json
import threading
import requests
from django.utils.deprecation import MiddlewareMixin
from datetime import datetime

ANOMALY_ENGINE_URL = 'http://127.0.0.1:8000/auditlog/analyze/' 
SAFE_EVENT_URL = 'http://127.0.0.1:8000/auditlog/monitoring/events/'  
REGISTERED_SYSTEM_ID = 'SYS-XXXXXX' 

ALLOWED_SERVER_PORT = '8001'  

class HookAgentMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            server_port = request.META.get('SERVER_PORT', '')
            if server_port != ALLOWED_SERVER_PORT:
                return  

            request_data = {
                "system_id": REGISTERED_SYSTEM_ID,
                "timestamp": datetime.utcnow().isoformat(),
                "method": request.method,
                "path": request.path,
                "user_agent": request.META.get('HTTP_USER_AGENT', ''),
                "ip_address": self._get_client_ip(request),
                "query_params": request.GET.dict(),
                "post_data": request.POST.dict(),
                "raw_body": self._get_raw_body(request),
            }

            threading.Thread(target=self._handle_event, args=(request_data,), daemon=True).start()
        except Exception as e:
            print(f"[HookAgentMiddleware] Error processing request: {e}")

    def _handle_event(self, data):
        try:
            event_payload = {
                "system_id": data["system_id"],
                "user": None,
                "event_type": "HTTP_REQUEST",
                "description": f"Request to {data['path']}",
                "source": "AGENT",
                "severity": "INFO",
                "timestamp": data["timestamp"],
                "metadata": {
                    "method": data["method"],
                    "path": data["path"],
                    "user_agent": data["user_agent"],
                    "ip": data["ip_address"],
                    "query_params": data["query_params"],
                    "post_data": data["post_data"],
                    "raw_body": data["raw_body"]
                }
            }

            headers = {'Content-Type': 'application/json'}
            resp = requests.post(ANOMALY_ENGINE_URL, headers=headers, json=event_payload, timeout=10)

            if resp.status_code == 200:
                result = resp.json()
                if result.get("anomaly", False):
                    print(f"[HookAgent] 🚨 Anomaly detected: {result.get('message', '')}")
                else:
                    self._save_safe_event(event_payload)
            else:
                print(f"[HookAgent] Unexpected analyzer response code: {resp.status_code}")
        except Exception as e:
            print(f"[HookAgent] Analyzer communication failed: {e}")

    def _save_safe_event(self, data):
        safe_event = {
            "system_id": data["system_id"],
            "user": None,
            "event_type": "HTTP_REQUEST",
            "description": f"Safe request to {data['path']} from {data['ip_address']}",
            "source": "AGENT",
            "severity": "INFO",
            "timestamp": data["timestamp"],
            "metadata": {
                "method": data["method"],
                "user_agent": data["user_agent"],
                "query_params": data["query_params"],
                "post_data": data["post_data"],
                "raw_body": data["raw_body"],
            }
        }

        try:
            headers = {'Content-Type': 'application/json'}
            requests.post(SAFE_EVENT_URL, headers=headers, data=json.dumps(safe_event), timeout=5)
        except Exception as e:
            print(f"[HookAgent] Failed to save safe event: {e}")

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    def _get_raw_body(self, request):
        try:
            if request.body:
                body = request.body.decode('utf-8')
                return body if len(body) < 1000 else '[TRUNCATED]'
        except Exception:
            return '[UNREADABLE]'
        return ''
