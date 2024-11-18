from django.urls import path
from .views import signup, login
from .views import google_login

urlpatterns = [
    path('login/', login, name='login_supabase'),
    path('signup/', signup, name='signup_supabase'),
    path('auth/google/', google_login, name='google_login'),
]
