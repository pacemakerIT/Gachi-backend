from django.urls import path
from .views import landing_page_supabase_connection

urlpatterns = [
    path('supabase/', landing_page_supabase_connection, name='landing_page_supabase'),
]