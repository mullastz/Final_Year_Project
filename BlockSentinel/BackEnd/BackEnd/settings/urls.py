from django.urls import path
from .views import get_admin_profile, update_admin_profile, change_password, create_admin_user, get_csrf_token
from . import views

urlpatterns = [
    path('admin/profile/', get_admin_profile, name='get_admin_profile'),
    path('admin/profile/update/', update_admin_profile, name='update_admin_profile'),
    path('admin/change-password/', change_password, name='change-password'),
    path('admins/', views.list_admins),
    path('admins/<int:id>/', views.update_admin),
    path('admins/<int:id>/', views.delete_admin),
    path('admin/create/', create_admin_user, name='create_admin_user'),
    path('settings/csrf-token/', get_csrf_token, name='get-csrf-token'),
]
