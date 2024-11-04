from django.urls import path
from .views import sign_up_user

urlpatterns = [
    path('sign-up-user/', sign_up_user, name='sign_up_user_supabase'),
]