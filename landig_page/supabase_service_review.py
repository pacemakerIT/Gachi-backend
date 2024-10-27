import requests
from django.conf import settings
from .supabase_config import supabase_url, headers


def fetch_supabase_review_data():
    
    # Importing Program, User, and ProgramParticipants data from Supabase
    review_response = requests.get(f'{supabase_url}/rest/v1/Review', headers=headers)
    user_response = requests.get(f'{supabase_url}/rest/v1/User', headers=headers)
    program_response = requests.get(f'{supabase_url}/rest/v1/Program', headers=headers)
    industry_response = requests.get(f'{supabase_url}/rest/v1/Industry', headers=headers)
    # Check response status
    if review_response.status_code == 200 and user_response.status_code == 200 and program_response.status_code == 200 and review_response.status_code == 200  :
        review_data = review_response.json()
        user_data = user_response.json()
        program_data = program_response.json()
        industry_data = industry_response.json()
        

        # Processing required data
        combined_data = []
        for review in review_data:

            review_id = review['reviewId']
            content = review['content']
            rating = review['rating']
            program_id = review['programId']
            reviewer_id = review['reviewerId']
    
            reviewer_info = next(
                (
                    u for u in user_data 
                    if u['userId'] == reviewer_id
                ), 
                None
            )
            
            reviewer_name = f"{reviewer_info['firstName']} {reviewer_info['lastName']}" if reviewer_info else None
            photo_url = reviewer_info['photoUrl'] if reviewer_info else None

            industry_name = next(
                (
                    ind['title'] for ind in industry_data 
                    if ind['industryId'] == reviewer_info['industryId']
                ), 
                None
            )           

            # Configuring response data
            combined_data.append({
                'reviewId': review_id,
                'content': content,
                'rating': rating,
                'programId': program_id,
                'reviewerName': reviewer_name,
                'photoUrl': photo_url,
                'industry': industry_name, 
            })

        return combined_data
    
    # Returns None if the request fails.
    return None
