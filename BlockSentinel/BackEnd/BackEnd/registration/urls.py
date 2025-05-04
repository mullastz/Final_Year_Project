from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import RegisterSystemView, RegisteredSystemListView, RegisteredSystemDetailView

urlpatterns = [
    path('register-system/', RegisterSystemView.as_view(), name='register_system'),
    path('list-systems/', RegisteredSystemListView.as_view(), name='list-systems'),
    path('get-system/<str:display_id>/', RegisteredSystemDetailView.as_view(), name='get_system_by_display_id'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
