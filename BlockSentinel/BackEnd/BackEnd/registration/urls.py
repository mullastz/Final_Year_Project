from django.conf import settings # type: ignore
from django.conf.urls.static import static # type: ignore
from django.urls import path # type: ignore
from .views import RegisterSystemView, RegisteredSystemListView, RegisteredSystemDetailView, AgentInstallView, DiscoverDatabasesView, FetchDatabaseNamesView, ExtractDataView

urlpatterns = [
    path('register-system/', RegisterSystemView.as_view(), name='register_system'),
    path('list-systems/', RegisteredSystemListView.as_view(), name='list-systems'),
    path('get-system/<str:display_id>/', RegisteredSystemDetailView.as_view(), name='get_system_by_display_id'),
    path('install-agent/', AgentInstallView.as_view(), name='install_agent'),
    path('discover-databases/', DiscoverDatabasesView.as_view(), name='discover_databases'),
    path('fetch-db-names/', FetchDatabaseNamesView.as_view(), name='fetch_db_names'),
    path('extract-data/', ExtractDataView.as_view(), name='extract_data'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
