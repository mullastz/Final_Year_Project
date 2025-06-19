from django.urls import path
from .views import BlockchainTransactionLogListView, AuditSummaryView
from .monitoring import get_system_usage
from .views import system_health_view
from . import views 

urlpatterns = [
    path('transactions/', BlockchainTransactionLogListView.as_view(), name='transaction-list'),
    path('system-status/', AuditSummaryView.as_view(), name='system-status'),
    path('health-monitoring/', get_system_usage, name='system-usage'),
    path('system-health/', system_health_view, name='system-health'),
    path('system-health/retry/', views.retry_service, name='retry-service'),
    path('logs/<str:service_name>/', views.get_service_logs),
    path('stop-agent/<str:service_name>/', views.stop_agent),
]
