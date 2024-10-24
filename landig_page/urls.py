from django.urls import path
from .views import ProgramAPIView  

urlpatterns = [
    path('programs/', ProgramAPIView.as_view(), name='program-list'), 
]
