from django.http import JsonResponse
from rest_framework.views import APIView
from .supabase_service import fetch_supabase_data  
from .serializers import ProgramSerializer  

class ProgramAPIView(APIView):
    def get(self, request):
        # Fetching data from Supabase
        combined_data = fetch_supabase_data()  # Call without request object
        
        if combined_data is not None:
            serializer = ProgramSerializer(combined_data, many=True)
            return JsonResponse(serializer.data, safe=False)
        
        return JsonResponse({'error': 'Data fetch failed'}, status=500)