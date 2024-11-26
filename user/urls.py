from django.urls import path
from .views import signup, login, logout, verify_token

urlpatterns = [
    path('signup/', signup, name='signup_supabase'),
    path('login/', login, name='login_supabase'),
    path('logout/', logout, name='logout_supabase'),
    path('verify/', verify_token, name='verify'),
]
