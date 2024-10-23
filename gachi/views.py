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
    # Get data from Program table
    response_program = supabase.table('Program').select('*').execute()
    programs = response_program.data

    # Get Mentors data from User table
    # Todo: get mentor data
    response_user = supabase.table('User').select('*').execute()
    users = response_user.data

    # Get data from Review table
    response_review = supabase.table('Review').select('*').execute()
    reviews = response_review.data

    response = {
        'programs':programs,
        'users': users,
        'reviews': reviews,
    }

    return JsonResponse(response, safe=False)
