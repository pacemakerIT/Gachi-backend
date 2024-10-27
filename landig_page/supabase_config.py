from django.conf import settings

supabase_url = settings.SUPABASE_URL
supabase_key = settings.SUPABASE_API_KEY
headers = {
    'apikey': supabase_key,
    'Authorization': f'Bearer {supabase_key}',
    'Content-Type': 'application/json'
}