import bcrypt
import jwt
from django.conf import settings
from django.http import JsonResponse
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.decorators import api_view
from supabase import create_client, Client
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
                "password": hashed_password,
                "userTypeId": '292d2be9-5ce5-4a7b-b5e2-cd412bed268b', # set user as mentee for default
                # "dateofregistration": timezone.now(),
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
    if not request.data.get('email'):
        return JsonResponse({'error': '이메일을 입력해주세요.'}, status=400)
    
    if not request.data.get('password'):
        return JsonResponse({'error': '비밀번호를 입력해주세요.'}, status=400)

    email = request.data.get('email')
    password = request.data.get('password').encode('utf-8')

    try:
        user_data = supabase.table('User').select('*').eq('email', email).execute()

        if not user_data.data:
            return JsonResponse({'error': '사용자를 찾을 수 없습니다.'}, status=400)
        
        user = user_data.data[0]
        stored_password = user['password'].encode('utf-8')

        if not bcrypt.checkpw(password, stored_password):
            return JsonResponse({'error': '비밀번호가 잘못되었습니다.'}, status=400)

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
        
        response = JsonResponse({
            'message': 'Successfully logged in',
            'user': {
                'id': user.get('id'),
                'email': email
            }
        }, status=200)
        
        # Set HTTP-only cookies
        response.set_cookie(
            'access_token',
            access_token,
            max_age=86400,  # 1 day in seconds
            httponly=True,
            samesite='Lax',
            secure=True  # Set to True in production with HTTPS
        )
        
        response.set_cookie(
            'refresh_token',
            refresh_token,
            max_age=604800,  # 7 days in seconds
            httponly=True,
            samesite='Lax',
            secure=True  # Set to True in production with HTTPS
        )
        
        return response
    
    except Exception as e:
        print(f"Login error: {str(e)}")
        return JsonResponse({
            "error": "Server error",
            "details": str(e)
        }, status=500)

@api_view(['POST'])
def logout(request):
    response = JsonResponse({'message': 'Successfully logged out'})
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response


@api_view(['GET'])
def verify_token(request):
    access_token = request.COOKIES.get('access_token')
    
    if not access_token:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        # Verify the token
        payload = jwt.decode(
            access_token,
            JWT_SECRET_KEY,
            algorithms=['HS256']
        )   
        return JsonResponse({
            'verified': True,
            'user': {
                'id': payload.get('user_id'),
                'email': payload.get('email')
            }
        })
    
    except jwt.ExpiredSignatureError:
        return JsonResponse({'error': 'Token has expired'}, status=401)
    except jwt.InvalidTokenError:
        return JsonResponse({'error': 'Invalid token'}, status=401)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)