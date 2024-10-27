import requests
from .supabase_config import supabase_url, headers
def fetch_supabase_mentor_data():

    # Fetch User, Industry, and UserType data from Supabase
    user_response = requests.get(f'{supabase_url}/rest/v1/User', headers=headers)
    industry_response = requests.get(f'{supabase_url}/rest/v1/Industry', headers=headers)
    user_type_response = requests.get(f'{supabase_url}/rest/v1/UserType', headers=headers)
  
    # Check response status
    if user_response.status_code == 200 and industry_response.status_code == 200 and user_type_response.status_code == 200:
        user_data = user_response.json()
        industry_data = industry_response.json()
        user_type_data = user_type_response.json()

        # Check for the UserType ID of the mentor
        mentor_type_id = next((ut['userTypeId'] for ut in user_type_data if ut['typeName'] == 'Mentor'), None)
        
        if not mentor_type_id:
            return None  

        # Process required data
        combined_data = []
        for user in user_data:
            if user['userTypeId'] == mentor_type_id:  # Filter users who are mentors
                # Get the industry name
                industry_name = next((ind['title'] for ind in industry_data if ind['industryId'] == user['industryId']), None)
                
                # Construct full name (firstName + lastName)
                mentor_name = f"{user['firstName']} {user['lastName']}"
                
                user_type = next((ut['typeName'] for ut in user_type_data if ut['userTypeId'] == user['userTypeId']), None)
                
                # Configure response data
                combined_data.append({
                    'userId': user['userId'],
                    'mentorName': mentor_name,  # Full name field
                    'photoUrl': user.get('photoUrl', ''),
                    'industry': industry_name,
                    'userType': user_type,
                })

        return combined_data
    
    # Returns None if the request fails
    return None
