import bcrypt
import jwt
import json
import requests
import logging

from django.conf import settings
from supabase import create_client, Client
from django.http import JsonResponse
from rest_framework.decorators import api_view
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from google.auth.transport import requests
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()

# Use the settings to get the Supabase configuration
SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_API_KEY = settings.SUPABASE_API_KEY
SUPABASE_KEY = settings.SUPABASE_KEY

# Initialize Supabase client
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_REFRESH_SECRET_KEY = settings.JWT_REFRESH_SECRET_KEY

GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET

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

@csrf_exempt
@require_http_methods(["POST"])
def google_login(request):
    try:
        data = json.loads(request.body)
        token_response = data.get('tokenResponse', {})
        
        # Get auth code
        auth_code = token_response.get('code')
        
        if not auth_code:
            return JsonResponse({
                'error': 'Authorization code not found'
            }, status=400)

        # Get access_token exchanging auth code to Google OAuth2 token endpoint
        token_url = 'https://oauth2.googleapis.com/token'
        token_data = {
            'code': auth_code,
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'redirect_uri': 'http://localhost:3000',
            'grant_type': 'authorization_code'
        }

        token_response = requests.post(token_url, data=token_data)
        
        if token_response.status_code != 200:
            logger.error(f"Token exchange failed: {token_response.text}")
            return JsonResponse({
                'error': 'Failed to exchange authorization code'
            }, status=400)
            
        tokens = token_response.json()
        access_token = tokens.get('access_token')
        refresh_token = tokens.get('refresh_token')

        # Get user info using Google UserInfo API
        user_info_response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if user_info_response.status_code != 200:
            logger.error(f"Failed to get user info: {user_info_response.text}")
            return JsonResponse({
                'error': 'Failed to get user info from Google'
            }, status=400)
            
        user_info = user_info_response.json()
        email = user_info.get('email')
        
        if not email:
            return JsonResponse({
                'error': 'Email not provided by Google'
            }, status=400)
        
        try:
            user_query = supabase.table('User').select('*').eq('email', email).execute()
            
            if not user_query.data:
                new_user = {
                    'email': email,
                    'firstName': user_info.get('given_name', ''),
                    'lastName': user_info.get('family_name', ''),
                    'photoUrl': user_info.get('picture', ''),
                    'userTypeId': '292d2be9-5ce5-4a7b-b5e2-cd412bed268b',
                }
                
                supabase.table('User').insert(new_user).execute()
                
                return JsonResponse({
                    'message': 'User created successfully',
                    'access_token': access_token,
                    'refresh_token':refresh_token,
                }, status=201)
            
            return JsonResponse({
                'message': 'Login successful',
                'access_token': access_token
            }, status=200)
            
        except Exception as e:
            logger.error(f"Supabase Error: {str(e)}")
            return JsonResponse({
                'error': 'Database operation failed',
                'details': str(e)
            }, status=500)
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON Decode Error: {str(e)}")
        return JsonResponse({
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Unexpected Error: {str(e)}")
        return JsonResponse({
            'error': 'Server error',
            'details': str(e)
        }, status=500)
