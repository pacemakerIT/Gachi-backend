from django.urls import path
from .views import landing_page_supabase_connection  

urlpatterns = [
    # 다른 URL 패턴들...

    # 새로운 URL 패턴 추가
    path('landig-page/', landing_page_supabase_connection, name='landig-page'),
]
