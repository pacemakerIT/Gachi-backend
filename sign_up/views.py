from django.conf import settings
from supabase import create_client, Client
from django.http import JsonResponse
from rest_framework.decorators import api_view
import json
import bcrypt
from django.shortcuts import render

# Use the settings to get the Supabase configuration
SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_API_KEY = settings.SUPABASE_API_KEY

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

@api_view(['POST'])
def sign_up_user(request):
    if request.method == 'POST':
        try:
            data = request.data
            
            required_fields = ["firstName", "lastName", "email", "password"]
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({
                        "error": f"Missing required field: {field}"
                    }, status=400)
            
            # Check if email is unique
            existing_user = supabase.table('User').select('email').eq('email', data['email']).execute()
            if existing_user.data:
                return JsonResponse({
                    "error": "Email already exists"
                }, status=400)
            
            hashed_password = bcrypt.hashpw(
                data['password'].encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
            
            user_data = {
                "firstName": data['firstName'],
                "lastName": data['lastName'],
                "email": data['email'],
                "password": hashed_password
            }
            
            response = supabase.table('User').insert(user_data).execute()
            
            if response.data:
                return JsonResponse({
                    "message": "User created successfully",
                }, status=201)
            
            return JsonResponse({
                "error": "Failed to create user"
            }, status=500)
            
        except Exception as e:
            print("Error:", str(e))
            return JsonResponse({
                "error": "Server error",
                "details": str(e)
            }, status=500)
    
    return JsonResponse({"error": "Invalid request method"}, status=400)