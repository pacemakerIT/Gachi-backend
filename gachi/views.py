from django.conf import settings
from supabase import create_client, Client
from django.http import JsonResponse
from rest_framework.decorators import api_view

# Use the settings to get the Supabase configuration
SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_API_KEY = settings.SUPABASE_API_KEY

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# Test view to fetch data from Supabase

@api_view(['GET'])
def test_supabase_connection(request):
    # Fetch all rows from a specific table
    response = supabase.table('Test').select('*').execute()
    data = response.data  # Get data from the response
    return JsonResponse(data, safe=False)  # Return data as JSON response