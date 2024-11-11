import bcrypt
import jwt
from django.conf import settings
from supabase import create_client, Client
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime, timedelta

# Use the settings to get the Supabase configuration
SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_API_KEY = settings.SUPABASE_API_KEY

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_REFRESH_SECRET_KEY = settings.JWT_REFRESH_SECRET_KEY

@api_view(['POST'])
def signup(request):
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

@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password').encode('utf-8')

    try:
        user = supabase.table('User').select('*').eq('email', email).execute().data[0]
        
        stored_password = user['password'].encode('utf-8')
        print("stord pw:", stored_password)


        if not bcrypt.checkpw(password, stored_password):
            return JsonResponse({'error': '이메일 또는 비밀번호가 잘못되었습니다.'}, status=401)

        # Create JWT Token
        payload = {
            'user_id': user.get('id'),
            'email': email,
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        
        access_token = jwt.encode(
            payload,
            JWT_SECRET_KEY,
            algorithm='HS256'
        )
        
        refresh_payload = {
            'user_id': user.get('id'),
            'exp': datetime.utcnow() + timedelta(days=7)
        }
        
        refresh_token = jwt.encode(
            refresh_payload,
            JWT_REFRESH_SECRET_KEY,
            algorithm='HS256'
        )
        
        return JsonResponse({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.get('id'),
                'email': email
            }
        }, status=200)
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return JsonResponse({
            "error": "Server error",
            "details": str(e)
        }, status=500)
    