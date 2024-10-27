from django.urls import path
from .views import fetch_landig_page_data  

urlpatterns = [
    # 다른 URL 패턴들...

    # 새로운 URL 패턴 추가
    path('landig-page/', fetch_landig_page_data, name='landig-page'),
]
