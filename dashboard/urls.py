from django.urls import path
from . import views  # views.py 파일을 가져옵니다.

urlpatterns = [
    path('dashboard_api_design/', views.dashboard_api_design, name='dashboard_api_design'),
    path('verify-admin/', views.verify_admin, name='verify-admin'),
]
