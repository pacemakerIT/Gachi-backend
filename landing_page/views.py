from django.conf import settings
from supabase import create_client, Client
from django.http import JsonResponse
from rest_framework.decorators import api_view

from postgrest import APIError
import asyncio
from functools import wraps
from typing import Dict, Any, List

# Use the settings to get the Supabase configuration
SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_API_KEY = settings.SUPABASE_API_KEY

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

def async_view(f):
    @wraps(f)
    def wrapper(request, *args, **kwargs):
        return asyncio.run(f(request, *args, **kwargs))
    return wrapper

async def fetch_programs() -> List[Dict[str, Any]]:
    try:
        response = supabase.table('Program')\
            .select('title, cost, programId, thumbnailUrl, status')\
            .order('status')\
            .execute()
        return response.data
    except APIError as e:
        raise APIError(f"Failed to fetch programs: {str(e)}")

async def fetch_mentors() -> List[Dict[str, Any]]:
    try:
        response = supabase.table('User')\
            .select('photoUrl, firstName, lastName, userId, Industry!inner(title)')\
            .eq('userTypeId', '55181db3-e2e6-4561-9a4e-0387f6df0782')\
            .execute()
        
        flattened_mentors = []
        for mentor in response.data:
            industry_data = mentor.pop('Industry', {})
            industryTitle = industry_data.get('title', None)
            flattened_mentors.append({
                **mentor,
                'industryTitle': industryTitle
            })
        return flattened_mentors
    except APIError as e:
        raise APIError(f"Failed to fetch mentors: {str(e)}")

async def fetch_reviews() -> List[Dict[str, Any]]:
    try:
        response = supabase.table('Review')\
            .select("reviewId, content, User!inner(photoUrl, firstName, lastName, Industry!inner(title))")\
            .execute()
        
        flattened_reviews = []
        for review in response.data:
            user_data = review.pop('User', {})
            industry_data = user_data.pop('Industry', {})
            industryTitle = industry_data.get('title', None)
            flattened_reviews.append({
                **review,
                **user_data,
                'industryTitle': industryTitle
            })
        return flattened_reviews
    except APIError as e:
        raise APIError(f"Failed to fetch reviews: {str(e)}")

@api_view(['GET'])
@async_view
async def landing_page_supabase_connection(request):
    try:
        programs_task = asyncio.create_task(fetch_programs())
        mentors_task = asyncio.create_task(fetch_mentors())
        reviews_task = asyncio.create_task(fetch_reviews())
        
        programs, mentors, reviews = await asyncio.gather(
            programs_task,
            mentors_task,
            reviews_task
        )
        
        response = {
            'programs': programs,
            'mentors': mentors,
            'reviews': reviews,
        }
        return JsonResponse(response, status=200)
        
    except APIError as e:
        error_response = {
            'status': 'error',
            'message': str(e),
            'error_type': 'database_error'
        }
        return JsonResponse(error_response, status=500)
        
    except Exception as e:
        error_response = {
            'status': 'error',
            'message': f'Unexpected error occurred: {str(e)}',
            'error_type': 'server_error'
        }
        return JsonResponse(error_response, status=500)
    
