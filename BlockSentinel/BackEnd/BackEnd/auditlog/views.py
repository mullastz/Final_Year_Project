from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import BlockchainTransactionLog
from .serializers import BlockchainTransactionLogSerializer
from django.contrib.auth import get_user_model
from .health import SystemHealthMonitor
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse

class BlockchainTransactionLogListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = BlockchainTransactionLog.objects.all().order_by('-timestamp')
        serializer = BlockchainTransactionLogSerializer(logs, many=True)
        return Response(serializer.data)

class AuditSummaryView(APIView):
    def get(self, request):
        total = BlockchainTransactionLog.objects.count()
        success = BlockchainTransactionLog.objects.filter(status='Success').count()
        failed = BlockchainTransactionLog.objects.filter(status='Fail').count()
        active_users = get_user_model().objects.filter(is_active=True).count()
        failed_logins = 3  # mock or from a model
        
        return Response({
            "total_transactions": total,
            "success_transactions": success,
            "failed_transactions": failed,
            "active_users": active_users,
            "failed_logins": failed_logins,
            "uptime": 83.5  # you can mock this or compute dynamically
        })

@api_view(['GET'])
def system_health_view(request):
    monitor = SystemHealthMonitor()
    return Response(monitor.get_all_statuses())

@api_view(['POST'])
def retry_service(request):
    service_name = request.data.get('service')
    monitor = SystemHealthMonitor()

    if service_name not in monitor.services:
        return Response({'error': 'Unknown service'}, status=status.HTTP_400_BAD_REQUEST)

    result = monitor.services[service_name]()
    return Response({'service': service_name, 'newStatus': result})

@api_view(['GET'])
def get_service_logs(request, service_name):
    log_path = f'/var/log/blocksentinel/{service_name}.log'
    try:
        with open(log_path, 'r') as file:
            lines = file.readlines()[-50:]  # last 50 lines
        return Response({"logs": lines})
    except FileNotFoundError:
        return Response({"logs": [f"No logs found for {service_name}."]})

@api_view(['POST'])
def stop_agent(request):
    import subprocess
    try:
        subprocess.run(["pkill", "-f", "agent_script_name.py"])  # adjust to match your actual agent
        return Response({"message": "Agent stopped successfully."})
    except Exception as e:
        return Response({"error": str(e)}, status=500)    