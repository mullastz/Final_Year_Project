from django.urls import path
from .views import BlockchainTransactionLogListView, AuditSummaryView
from .monitoring import get_system_usage
from .views import system_health_view, receive_monitoring_events, get_monitored_events, AnomalyEventListCreateView, analyze_events
from . import views 

urlpatterns = [
    path('transactions/', BlockchainTransactionLogListView.as_view(), name='transaction-list'),
    path('system-status/', AuditSummaryView.as_view(), name='system-status'),
    path('health-monitoring/', get_system_usage, name='system-usage'),
    path('system-health/', system_health_view, name='system-health'),
    path('system-health/retry/', views.retry_service, name='retry-service'),
    path('logs/<str:service_name>/', views.get_service_logs),
    path('stop-agent/<str:service_name>/', views.stop_agent),
    path('monitoring/events/', receive_monitoring_events, name='receive_monitoring_events'),
    path('monitoring/activity/', get_monitored_events, name='get_monitored_events'),
    path('anomalies/', AnomalyEventListCreateView.as_view(), name='anomaly-events'),
    path('analyze/', analyze_events, name='analyze-events'),
]
