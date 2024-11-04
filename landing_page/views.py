from django.conf import settings
from supabase import create_client, Client
from django.http import JsonResponse
from rest_framework.decorators import api_view

# Use the settings to get the Supabase configuration
SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_API_KEY = settings.SUPABASE_API_KEY

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

@api_view(['GET'])
def landing_page_supabase_connection(request):
    # Get data from Program table
    response_program = supabase.table('Program').select('*').order('status').execute()
    programs = response_program.data

    # Get Mentors data from User table
    response_mentor = supabase.table('User').select('*, Industry!inner(*)').eq('userTypeId', '74ae0cb7-e4bf-472e-a8a3-e94d895028e5').execute()
    mentors = response_mentor.data

    flattened_mentors = []
    for mentor in mentors:
        industry_data = mentor.pop('Industry', {})
        industryTitle = industry_data.get('title', None)

        flattened_mentor = {
            **mentor,
            'industryTitle': industryTitle
        }
        flattened_mentors.append(flattened_mentor)

    # Get data from Review table
    response_review = supabase.table('Review').select("*, User!inner(*, Industry!inner(title))").execute()
    reviews = response_review.data

    flattened_reviews = []
    for review in reviews:
        user_data = review.pop('User', {})
        industry_data = user_data.pop('Industry', {})
        industryTitle = industry_data.get('title', None)

        flattened_review = {
            **review,
            **user_data,
            'industryTitle': industryTitle
        }
        flattened_reviews.append(flattened_review)

    response = {
        'programs':programs,
        'mentors': flattened_mentors,
        'reviews': flattened_reviews,
    }

    return JsonResponse(response, safe=False)