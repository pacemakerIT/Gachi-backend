from django.urls import path
from .views import test_supabase_connection

urlpatterns = [
    path('test-supabase/', test_supabase_connection, name='test_supabase'),
]