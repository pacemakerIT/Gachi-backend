from django.urls import path
from . import views  # views.py 파일을 가져옵니다.

urlpatterns = [
    path('dashboard_api_design/', views.dashboard_api_design, name='dashboard_api_design'),
    path('verify-admin/', views.verify_admin, name='verify-admin'),
    path('admin_user_api/', views.admin_user_api, name='admin_user_api'),
    path('edit_user/', views.edit_user, name='edit_user'),
    path('edit_user_type/', views.edit_user_type, name='edit_user_type'),
    path('delete_user/', views.delete_user, name='delete_user'),
    path('edit_memo/', views.edit_memo, name='edit_memo'),
]
