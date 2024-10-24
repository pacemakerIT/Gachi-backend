import requests
from django.conf import settings
from django.utils.text import slugify


def fetch_supabase_data():
    # Get Supabase API URL and key
    supabase_url = settings.SUPABASE_URL
    supabase_key = settings.SUPABASE_API_KEY
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }
    
    # Importing Program, User, and ProgramParticipants data from Supabase
    program_response = requests.get(f'{supabase_url}/rest/v1/Program', headers=headers)
    user_response = requests.get(f'{supabase_url}/rest/v1/User', headers=headers)
    participants_response = requests.get(f'{supabase_url}/rest/v1/ProgramParticipants', headers=headers)

    # Check response status
    if program_response.status_code == 200 and user_response.status_code == 200 and participants_response.status_code == 200:
        program_data = program_response.json()
        user_data = user_response.json()
        participants_data = participants_response.json()

        # Processing required data
        combined_data = []
        for program in program_data:
            # 
            program_id = program['programId']
            title = program['title']
            coast = program['cost']
            status = program['status']
            thumbnail_url = program.get('thumbnailUrl', '')  

         
            host_id = next((p['hostId'] for p in participants_data if p['programId'] == program_id), None)
            host_name = next(
                (
                    f"{u['firstName']} {u['lastName']}" 
                    for u in user_data 
                    if u['userId'] == host_id
                ), 
                None
            )

            # Configuring response data
            combined_data.append({
                'programId': program_id,
                'title': title,
                'coast': coast,
                'status': status,
                'hostName': host_name,
                'thumbnailUrl': thumbnail_url, 
                'slug': slugify(title)
            })
        
        # Sort program data by status
        sorted_programs = sorted(combined_data, key=lambda p: (
            p['status'] != 'New',
            p['status'] != 'Sales'
        ))

        return sorted_programs
    
    # Returns None if the request fails.
    return None
