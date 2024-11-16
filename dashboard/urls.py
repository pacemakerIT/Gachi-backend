# dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_api_design, name='user_statistics'),
]