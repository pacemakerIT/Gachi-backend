# views.py
import json
import jwt
import calendar
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Count, F,Sum
from django.db.models.functions import TruncMonth
from postgrest import APIError
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework.decorators import api_view
from supabase import Client, create_client
from uuid import UUID
from datetime import datetime, timedelta
from collections import defaultdict
from gachi_backend.models import User, Industry, Mentormatching, Feedback, Program, Programtopic, Programparticipants, Topic

SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_API_KEY = settings.SUPABASE_API_KEY

JWT_SECRET_KEY = settings.JWT_SECRET_KEY

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

@api_view(['GET'])
def verify_admin(request):
    access_token = request.COOKIES.get('access_token')
    if not access_token:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        # Verify the token
        payload = jwt.decode(
            access_token,
            JWT_SECRET_KEY,
            algorithms=['HS256']
        )   
        user_email = payload.get('email')
        if not user_email:
            return JsonResponse({'error': 'Invalid token payload'}, status=401)

        response = supabase.table('User').select('*').eq('email', user_email).single().execute()
        if not response:
            return JsonResponse({'error': 'User not found'}, status=404)

        user_data = response.data
        if user_data['userTypeId'] == '8c1355cf-b334-40fd-9076-890c52be159b':
            return JsonResponse({'message': 'Authorized'}, status=200)
        else:
            return JsonResponse({'message': 'Forbidden'}, status=403)

    except jwt.ExpiredSignatureError:
        return JsonResponse({'error': 'Token has expired'}, status=401)
    except jwt.InvalidTokenError:
        return JsonResponse({'error': 'Invalid token'}, status=401)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def dashboard_api_design(request):
    # 1. 이번 주 신규 회원 수
    today = timezone.now()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    weekly_new_users = User.objects.filter(dateofregistration__range=(start_of_week, end_of_week)).count()
    
    # 2. 이번 달 신규 회원 수
    start_of_month = timezone.datetime(today.year, today.month, 1, tzinfo=timezone.get_current_timezone())
    end_of_month = timezone.datetime(today.year, today.month, calendar.monthrange(today.year, today.month)[1], tzinfo=timezone.get_current_timezone())
    current_monthly_new_users = User.objects.filter(dateofregistration__range=(start_of_month, end_of_month)).count()
    
    # 3. 지난 달 신규 회원 수
    last_month = today.month - 1 if today.month > 1 else 12
    last_month_year = today.year if today.month > 1 else today.year - 1
    start_of_last_month = timezone.datetime(last_month_year, last_month, 1, tzinfo=timezone.get_current_timezone())
    end_of_last_month = timezone.datetime(last_month_year, last_month, calendar.monthrange(last_month_year, last_month)[1], tzinfo=timezone.get_current_timezone())
    last_month_new_users = User.objects.filter(dateofregistration__range=(start_of_last_month, end_of_last_month)).count()
    
    # 4. 총 회원 수
    total_users = User.objects.count()
    
    # 5. 회원 수 증감률
    growth_rate = ((current_monthly_new_users - last_month_new_users) / last_month_new_users * 100) if last_month_new_users > 0 else 0
    
    dashboard_stats = {
        "weeklyNewUsers": weekly_new_users,
        "currentMonthlyNewUsers": current_monthly_new_users,
        "totalUsers": total_users,
        "growthRate": f"{growth_rate:.1f}%",
    }
        
    # 인기 멘토 목록
    mentor_usertypeid = UUID('55181db3-e2e6-4561-9a4e-0387f6df0782')
    mentors = User.objects.filter(usertypeid=mentor_usertypeid)
    
    popular_mentors = []
    for mentor in mentors:
        industry_title = mentor.industryid.title if mentor.industryid else "미정"
        matching_count = Mentormatching.objects.filter(hostid=mentor).count()
        feedback_count = Feedback.objects.filter(mentorid=mentor).count()
        
        mentor_info = {
            "userid": str(mentor.userid),
            "photourl": mentor.photourl,
            "fullname": f"{mentor.firstname} {mentor.lastname}",
            "industry": industry_title,
            "matching_count": matching_count,
            "feedback_count": feedback_count
        }
        popular_mentors.append(mentor_info)

    popular_mentors = sorted(popular_mentors, key=lambda x: x['matching_count'], reverse=True)
    
    # 인기 프로그램 목록
    popular_programs = []
    programs = Program.objects.all()
    for program in programs:
        mentor_participants = Programparticipants.objects.filter(programid=program, hostid__usertypeid=mentor_usertypeid)
        
        if not mentor_participants.exists():
            continue
        
        mentor = mentor_participants.first().hostid
        mentor_name = f"{mentor.firstname} {mentor.lastname}"
        
        # 토픽 정보 가져오기
        program_topic = Programtopic.objects.filter(programid=program).first()
        topic_description = program_topic.topicid.description if program_topic else "미정"
        
        accumulated_sales_count = Programparticipants.objects.filter(programid=program).count()
        accumulated_sales_amount = accumulated_sales_count * program.cost if program.cost else 0
        
        program_info = {
            "programid": str(program.programid),
            "program_title": program.title,
            "topic": topic_description,  # 토픽 정보
            "mentor": mentor_name,
            "mentor_photo": mentor.photourl,
            "cost": program.cost,
            "accumulated_sales_count": accumulated_sales_count,
            "accumulated_sales_amount": f"${accumulated_sales_amount:,.2f}"
        }
        popular_programs.append(program_info)
    
    # 누적 판매수 기준으로 내림차순 정렬
    popular_programs = sorted(popular_programs, key=lambda x: x['accumulated_sales_count'], reverse=True)
    
    # 분야별 참여 프로그램 및 사용자 수 계산
    topic_participation_data = []
    total_participation_count = 0  # 총 프로그램 참여자 수 계산용

    # 모든 토픽을 가져와서 처리
    topics = Topic.objects.all()
    for topic in topics:
        # 각 토픽에 연결된 프로그램들
        topic_programs = Programtopic.objects.filter(topicid=topic)
        
        # 분야 참여 수 계산 (중복 허용)
        topic_participation_count = 0
        
        for program_topic in topic_programs:
            programid = program_topic.programid
            participants = Programparticipants.objects.filter(programid=programid)
            
            # 각 프로그램별 참여 인원 추가
            topic_participation_count += participants.count()
        
        # 총 참여 횟수에 추가
        total_participation_count += topic_participation_count

    # 전체 참여 횟수를 기준으로 다시 비율을 계산
    for topic in topics:
        topic_programs = Programtopic.objects.filter(topicid=topic)
        topic_participation_count = 0
        
        for program_topic in topic_programs:
            programid = program_topic.programid
            participants = Programparticipants.objects.filter(programid=programid)
            topic_participation_count += participants.count()
        
        # 전체 참여 횟수를 기반으로 비율 계산
        participation_rate = (topic_participation_count / total_participation_count * 100) if total_participation_count > 0 else 0

        # 분야별 데이터 추가
        topic_participation_data.append({
            "topic": topic.description,
            "participation_count": topic_participation_count,
            "participation_rate": f"{participation_rate:.2f}%",  # 비율로 표시
        })

    # 상위 5개의 데이터만 포함하도록 슬라이싱
    topic_participation_data = sorted(topic_participation_data, key=lambda x: x["participation_count"], reverse=True)[:3]



    
    # 분야별 참여자 비율 계산
    industry_data = []

    # 중복된 참여까지 포함하여 총 참여자 수 계산
    total_participants = total_participation_count 

    # 분야별 참여 횟수를 중복 포함하여 계산
    industry_counts = (
        Programparticipants.objects
        .filter(guestid__isnull=False)
        .values(industry_name=F('guestid__industryid__title'))
        .annotate(participation_count=Count('programid'))  # 각 참여를 개별로 카운트 (guestid가 중복되더라도 모든 참여를 포함)
        .order_by('-participation_count')[:5]  # 상위 5개만 선택
    )

    # 비율 계산
    for entry in industry_counts:
        participation_rate = (entry['participation_count'] / total_participants) * 100 if total_participants > 0 else 0
        industry_data.append({
            "industry": entry['industry_name'],
            "participation_count": entry['participation_count'],
            "participation_rate": f"{participation_rate:.2f}%"
        })
    
    # 현재 연도
    current_year = timezone.now().year

    # 1. 매월 신규 회원 수
    yearly_monthly_new_users = (
        User.objects.filter(dateofregistration__year=current_year)
        .annotate(month=TruncMonth('dateofregistration'))
        .values('month')
        .annotate(new_users=Count('userid'))
        .order_by('month')
    )

    # 2. 매월 신규 프로그램 수
    monthly_new_programs = (
        Program.objects.filter(createdate__year=current_year)
        .annotate(month=TruncMonth('createdate'))
        .values('month')
        .annotate(new_programs=Count('programid'))
        .order_by('month')
    )

    # 3. 매월 멘토링 세션 수
    monthly_mentoring_sessions = (
        Mentormatching.objects.filter(datetime__year=current_year)
        .annotate(month=TruncMonth('datetime'))
        .values('month')
        .annotate(new_sessions=Count('matchingid'))
        .order_by('month')
    )

    # 데이터를 defaultdict을 사용해 월별 데이터를 쉽게 저장
    monthly_data_dict = defaultdict(lambda: {"new_users": 0, "new_programs": 0, "new_sessions": 0})

    # 쿼리 결과를 monthly_data_dict에 채워넣기
    for item in yearly_monthly_new_users:
        monthly_data_dict[item['month'].strftime("%Y-%m")]["new_users"] = item["new_users"]

    for item in monthly_new_programs:
        monthly_data_dict[item['month'].strftime("%Y-%m")]["new_programs"] = item["new_programs"]

    for item in monthly_mentoring_sessions:
        monthly_data_dict[item['month'].strftime("%Y-%m")]["new_sessions"] = item["new_sessions"]

    # 1월부터 12월까지의 월별 데이터를 monthly_data로 변환
    inflow_months = [datetime(current_year, month, 1) for month in range(1, 13)]
    
    monthly_inflow_data = [
        {
            "month": month.strftime("%Y-%m"),
            "new_users": monthly_data_dict[month.strftime("%Y-%m")]["new_users"],
            "new_programs": monthly_data_dict[month.strftime("%Y-%m")]["new_programs"],
            "new_sessions": monthly_data_dict[month.strftime("%Y-%m")]["new_sessions"],
        }
        for month in inflow_months
    ]    
    # 1. 매월 매출 (총 프로그램 판매 수익)
    monthly_sales = (
        Programparticipants.objects
        .filter(dateofparticipant__year=current_year)  # 참여 날짜 기준으로 필터링
        .annotate(month=TruncMonth('dateofparticipant'))  # 참여 날짜의 월 단위로 그룹화
        .values('month')
        .annotate(total_sales=Sum('programid__cost'))  # 프로그램의 비용 합산
        .order_by('month')
    )
    # 2. 매월 무료 프로그램 참여 횟수
    monthly_free_participation = (
        Programparticipants.objects
        .filter(programid__cost=0, dateofparticipant__year=current_year)  # 참여 날짜 기준, 무료 프로그램만 필터링
        .annotate(month=TruncMonth('dateofparticipant'))  # 참여 날짜의 월 단위로 그룹화
        .values('month')
        .annotate(free_count=Count('programid'))  # 참여 횟수 집계
        .order_by('month')
    )
    # 데이터를 효율적으로 매칭하기 위해 dict 변환
    sales_dict = {item['month']: item['total_sales'] for item in monthly_sales}
    free_participation_dict = {item['month']: item['free_count'] for item in monthly_free_participation}


    # 1월부터 12월까지 월 데이터 생성
    sales_months = [datetime(current_year, month, 1, tzinfo=timezone.get_current_timezone()) for month in range(1, 13)]
    monthly_sales_data = []
    
    for month in sales_months:
        month_str = month.strftime("%Y-%m")

        # 매출, 무료 참여 데이터 조회
        total_sales = sales_dict.get(month, 0) or 0  # 매출 데이터 조회, 없으면 0
        company_profit = total_sales * 0.2  # 회사 수익 20%
        free_count = free_participation_dict.get(month, 0) or 0  # 무료 참여 데이터 조회, 없으면 0

        # 월별 데이터 추가
        monthly_sales_data.append({
            "month": month_str,
            "totalSales": total_sales,
            "companyProfit": company_profit,
            "freeParticipationCount": free_count
        })
    
    # 최종 응답 데이터 포맷
    data = {
        "stats": dashboard_stats,
        "popularMentors": popular_mentors,
        "popularPrograms": popular_programs,
        "total_participation_count": total_participation_count,
        "topicParticipation": topic_participation_data,
        "industryParticipation": industry_data,
        "year": current_year,
        "monthlyInflowData": monthly_inflow_data,
        "monthlySalesData": monthly_sales_data,
    }

    return JsonResponse(data) 

def admin_user_api(request):
    try:
        response = supabase.table('User') \
            .select('firstName, lastName, email, linkedInUrl, userId, userTypeId, UserType(typeName), memo, Industry(title)') \
            .execute()
        users = []
        for user in response.data:
            user_id = user.get('userId', 'None')
            linkedInUrl = user.pop('linkedInUrl', 'None') or 'None'
            industry_data = user.pop('Industry', {})
            industryTitle = industry_data.get('title', 'None') if industry_data else 'None'
            user_type_data = user.pop('UserType', {})
            user_type = user_type_data.get('typeName', 'None') if user_type_data else 'None'

            match_response = supabase.table('MentorMatching').select('*')\
                .or_(f'hostId.eq.{user_id},guestId.eq.{user_id}').execute()
            if match_response.data: matchStatus = 'Matched'
            else: matchStatus = 'Unmatched'

            users.append({
                **user,
                'linkedInUrl': linkedInUrl,
                'location': 'None',
                'industryTitle': industryTitle,
                'userType': user_type,
                'matchStatus': matchStatus,
            })
        return JsonResponse({"data": users}, status=200)

    except APIError as api_err:
        return JsonResponse({"error": f"API Error: {str(api_err)}"}, status=500)

    except Exception as ex:
        return JsonResponse({"error": "An unexpected error occurred.", "details": str(ex)}, status=500)

@csrf_exempt
def edit_user(request):
    if request.method == 'PUT':
        user_id = request.GET.get('user_id')
        body = json.loads(request.body)
        
        try:
            # Get industry id to update user in database
            industry_title = body.get('industryTitle')
            industry_response = supabase.table('Industry').select('industryId').eq('title', industry_title).execute()
            if industry_response.data and len(industry_response.data) > 0:
                industry_id = industry_response.data[0]['industryId']
                
            response = supabase.table('User').update({
                'firstName': body.get('firstName'),
                'lastName': body.get('lastName'),
                'email': body.get('email'),
                'linkedInUrl': body.get('linkedInUrl'),
                # 'region': body.get('region'),
                'industryId': industry_id,
            }).eq('userId', user_id).execute()

            if response.data:
                return JsonResponse({"message": "User successfully updated."}, status=200)
            else:
                return JsonResponse({"error": "Failed to update user from Supabase."}, status=400)

        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

@csrf_exempt
def delete_user(request):
    if request.method == 'DELETE':
        user_id = request.GET.get('user_id')
        try:
            print('userid', user_id)
            response = supabase.table('User').delete().eq('userId', user_id).execute()
            print('respons', response)
            if response.data:
                return JsonResponse({"message": "User successfully deleted."}, status=200)
            else:
                return JsonResponse({"error": "Failed to delete user from Supabase."}, status=400)

        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

@csrf_exempt
def edit_user_type(request):
    if request.method == 'PUT':
        user_id = request.GET.get('user_id')
        body = json.loads(request.body)
        
        try:
            if (body == '멘토'):
                userTypeId = '55181db3-e2e6-4561-9a4e-0387f6df0782'
            elif (body == '멘티'):
                userTypeId = '292d2be9-5ce5-4a7b-b5e2-cd412bed268b'

            response = supabase.table('User').update({
                'userTypeId': userTypeId,
            }).eq('userId', user_id).execute()

            if response.data:
                return JsonResponse({"message": "User successfully updated."}, status=200)
            else:
                return JsonResponse({"error": "Failed to update user from Supabase."}, status=400)

        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)


@csrf_exempt
def edit_memo(request):
    if request.method == 'PUT':
        user_id = request.GET.get('user_id')
        body = json.loads(request.body)

        print('body', body)        
        try:
            response = supabase.table('User').update({
                'memo': body,
            }).eq('userId', user_id).execute()

            if response.data:
                return JsonResponse({"message": "Memo successfully updated."}, status=200)
            else:
                return JsonResponse({"error": "Failed to update memo from Supabase."}, status=400)

        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)
