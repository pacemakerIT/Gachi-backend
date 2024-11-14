from django.urls import path
from .views import signup, login

urlpatterns = [
    path('login/', login, name='login_supabase'),
    path('signup/', signup, name='signup_supabase'),
]
