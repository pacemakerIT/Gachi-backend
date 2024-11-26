from django.http import JsonResponse
import jwt
from django.conf import settings

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of public endpoints
        public_paths = [
            '/user/login/', 
            '/user/signup/',
            '/landing_page/supabase/',
        ]
        
        # Skip authentication check for public paths
        if any(request.path.startswith(path) for path in public_paths):
            return self.get_response(request)

        access_token = request.COOKIES.get('access_token')
        
        if not access_token:
            return JsonResponse({'error': 'Authentication is required.'}, status=401)

        try:
            payload = jwt.decode(
                access_token,
                settings.JWT_SECRET_KEY,
                algorithms=['HS256']
            )
            request.user_id = payload.get('user_id')
            request.user_email = payload.get('email')
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expired'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)

        return self.get_response(request)