from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, generics
from django.contrib.auth import get_user_model
from .models import BlockchainTransactionLog, MonitoredEvent, AnomalyEvent
from .serializers import BlockchainTransactionLogSerializer, MonitoredEventSerializer, AnomalyEventSerializer
from .health import SystemHealthMonitor
import subprocess
import logging
from detection_engine.anomaly_service import AnomalyDetectionService
from registration.models import RegisteredSystem
from detection_engine.db_clients import PostgreSQLClient, MySQLClient

logger = logging.getLogger(__name__)

# Inline helper (move to utils.py if you like)
def get_db_client(system_id=None):
    """
    Returns the appropriate DB client (PostgreSQL or MySQL) using hardcoded credentials for the demo.
    """
    try:
        # Hardcoded credentials for external system
        creds = {
            'type': 'PostgreSQL',  # or 'MySQL'
            'host': 'localhost',
            'port': 5432,
            'user': 'postgres',
            'password': 'grace2002',
            'dbname': 'lecturer_evaluation_db'
        }

        db_type = creds.get('type')

        if db_type == "PostgreSQL":
            return PostgreSQLClient(**creds)
        elif db_type == "MySQL":
            return MySQLClient(**creds)
        else:
            raise Exception(f"Unsupported DB type: {db_type}")

    except Exception as e:
        logger.error(f"Error getting DB client: {e}")
        raise


class BlockchainTransactionLogListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = BlockchainTransactionLog.objects.all().order_by('-timestamp')
        serializer = BlockchainTransactionLogSerializer(logs, many=True)
        return Response(serializer.data)

class AuditSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total = BlockchainTransactionLog.objects.count()
        success = BlockchainTransactionLog.objects.filter(status='Success').count()
        failed = BlockchainTransactionLog.objects.filter(status='Fail').count()
        active_users = get_user_model().objects.filter(is_active=True).count()
        failed_logins = 3  # Placeholder

        uptime = 83.5  # Placeholder

        return Response({
            "total_transactions": total,
            "success_transactions": success,
            "failed_transactions": failed,
            "active_users": active_users,
            "failed_logins": failed_logins,
            "uptime": uptime,
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def system_health_view(request):
    monitor = SystemHealthMonitor()
    return Response(monitor.get_all_statuses())

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def retry_service(request):
    service_name = request.data.get('service')
    monitor = SystemHealthMonitor()

    if service_name not in monitor.services:
        return Response({'error': 'Unknown service'}, status=status.HTTP_400_BAD_REQUEST)

    result = monitor.services[service_name]()
    return Response({'service': service_name, 'newStatus': result})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_service_logs(request, service_name):
    log_path = f'/var/log/blocksentinel/{service_name}.log'
    try:
        with open(log_path, 'r') as file:
            lines = file.readlines()[-50:]
        return Response({"logs": lines})
    except FileNotFoundError:
        return Response({"logs": [f"No logs found for {service_name}."]}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_agent(request):
    try:
        subprocess.run(["pkill", "-f", "agent_script_name.py"], check=True)
        return Response({"message": "Agent stopped successfully."})
    except subprocess.CalledProcessError as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def receive_monitoring_events(request):
    data = request.data
    many = isinstance(data, list)
    serializer = MonitoredEventSerializer(data=data, many=many)

    if serializer.is_valid():
        serializer.save()
        return Response({'success': f'{len(serializer.data) if many else 1} event(s) saved.'}, status=status.HTTP_201_CREATED)
    else:
        logger.error(f"MonitoredEventSerializer errors: {serializer.errors}")
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_monitored_events(request):
    events = MonitoredEvent.objects.all()
    serializer = MonitoredEventSerializer(events, many=True)
    return Response(serializer.data)

class AnomalyEventListCreateView(generics.ListCreateAPIView):
    queryset = AnomalyEvent.objects.all()
    serializer_class = AnomalyEventSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def analyze_events(request):
    """
    Receives monitoring events, runs anomaly detection,
    saves anomalies and normal events accordingly.
    """
    data = request.data
    events = data if isinstance(data, list) else [data]

    try:
        system_id = events[0].get('system_id') if events else None
        db_client = get_db_client(system_id=system_id)
        anomaly_service = AnomalyDetectionService(db_client=db_client)
    except Exception as e:
        logger.error(f"Anomaly service setup failed: {e}")
        return Response({"error": "Internal error during anomaly detection setup."}, status=500)

    anomalies_to_save = []
    normal_events_to_save = []

    for event in events:
        system_id = event.get('system_id')
        user = event.get('user')
        payload = event.get('description', '')
        metadata = event.get('metadata', {}) or {}
        user_agent = metadata.get('user_agent', '')
        ip = metadata.get('ip_address') or metadata.get('ip') or ''
        login_time = metadata.get('login_time', '00:00')
        api_path = metadata.get('path', '')
        action = event.get('event_type', '')
        schema_snapshot = metadata.get('schema_snapshot', {})
        os_snapshot = metadata.get('os_snapshot', {})

        try:
            alerts = anomaly_service.detect_all(
                system_id=system_id,
                user=user,
                payload=payload,
                user_agent=user_agent,
                ip=ip,
                login_time=login_time,
                api_path=api_path,
                action=action,
                schema_snapshot=schema_snapshot,
                os_snapshot=os_snapshot
            )
            if alerts:
                anomalies_to_save.extend(alerts)
            else:
                normal_events_to_save.append(event)

        except Exception as e:
            logger.warning(f"Anomaly detection failed for event: {e}")
            normal_events_to_save.append(event)

    if anomalies_to_save:
        anomaly_serializer = AnomalyEventSerializer(data=anomalies_to_save, many=True)
        if anomaly_serializer.is_valid():
            anomaly_serializer.save()
        else:
            logger.error(f"Anomaly serializer errors: {anomaly_serializer.errors}")

    if normal_events_to_save:
        normal_serializer = MonitoredEventSerializer(data=normal_events_to_save, many=True)
        if normal_serializer.is_valid():
            normal_serializer.save()
        else:
            logger.error(f"Monitored event serializer errors: {normal_serializer.errors}")

    return Response({
        "anomalies_saved": len(anomalies_to_save),
        "normal_events_saved": len(normal_events_to_save),
    }, status=status.HTTP_201_CREATED)
