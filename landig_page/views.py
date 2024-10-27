from django.http import JsonResponse
from rest_framework.decorators import api_view
from .supabase_service_mentor import fetch_supabase_mentor_data
from .supabase_service_program import fetch_supabase_program_data
from .supabase_service_review import fetch_supabase_review_data
from .serializers import ProgramSerializer, MentorSerializer, ReviewSerializer

@api_view(['GET'])
def fetch_landig_page_data(request):
    # Fetch programs data
    programs = fetch_supabase_program_data()
    
    # Fetch mentors data
    mentors = fetch_supabase_mentor_data()
    
    reviews = fetch_supabase_review_data()

    # Check if the data was fetched successfully
    if programs is not None and mentors is not None:
        # Serialize the programs data
        serialized_programs = ProgramSerializer(programs, many=True).data

        # Serialize the mentors data
        serialized_mentors = MentorSerializer(mentors, many=True).data
        
        serialized_reviews = ReviewSerializer(reviews, many=True).data


        # Create the combined response
        response = {
            'programs': serialized_programs,
            'mentors': serialized_mentors,
            'reviews': serialized_reviews        
            }
        return JsonResponse(response, safe=False)
    
    # Return an error response if any data fetching failed
    return JsonResponse({'error': 'Failed to fetch data from Supabase'}, status=500)
