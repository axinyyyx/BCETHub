from django.http import request
import os
import datetime
from django.conf import settings
from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
from .models import (
    Branch, AcademicYear, Pooling, Faculty, InductionProgram, RoutineSlot, 
    MessTiming, DailyMessMenu, Feedback, Section, Notes, Course, Subject, 
    PYQ, Assignment, Notice, Community, CommunityGroupType, 
    CommunityPost, CommunityPostImage
)
from .routine_utils import (
    read_routine_csv, get_routine_file_version, get_filtered_routine_csv,
    evaluate_slot_status
)
from urllib.parse import urlparse
from django.contrib.auth.decorators import login_required

# Greeting Function
def get_greeting(request):
    now = timezone.localtime()
    current_hour = now.hour

    if 4 <= current_hour < 12:
        greeting = "Good Morning"
    elif 12 <= current_hour < 17:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"

    username = request.user.username

    return HttpResponse(f"<strong>{greeting}, <span>@{username}</span></strong>")

DAYS_MAP = {
    0: ('MON', 'Monday'),
    1: ('TUE', 'Tuesday'),
    2: ('WED', 'Wednesday'),
    3: ('THU', 'Thursday'),
    4: ('FRI', 'Friday'),
    5: ('SAT', 'Saturday'),
    6: ('SUN', 'Sunday'),
}

DAY_LOOKUP = {
    'monday': 'MON', 'mon': 'MON',
    'tuesday': 'TUE', 'tue': 'TUE',
    'wednesday': 'WED', 'wed': 'WED',
    'thursday': 'THU', 'thu': 'THU',
    'friday': 'FRI', 'fri': 'FRI',
    'saturday': 'SAT', 'sat': 'SAT',
    'sunday': 'SUN', 'sun': 'SUN',
}

DAYS_LIST = [
    ('MON', 'Monday'),
    ('TUE', 'Tuesday'),
    ('WED', 'Wednesday'),
    ('THU', 'Thursday'),
    ('FRI', 'Friday'),
    ('SAT', 'Saturday'),
    ('SUN', 'Sunday'),
]

# current time in IST timezone
def get_ist_now():
    return timezone.localtime()

def service_worker(request):
    sw_path = os.path.join(settings.BASE_DIR, 'static', 'js', 'serviceworker.js')
    if os.path.exists(sw_path):
        with open(sw_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type='application/javascript')
    return HttpResponse('', content_type='application/javascript')

def group_evaluated_csv_slots(slots, target_day, target_time, current_day):
    evaluated = []
    for s in slots:
        status = evaluate_slot_status(s, target_day, target_time, current_day)
        fac_code = (s.get('faculty_code') or '').strip()
        if not fac_code or fac_code.upper() in ['LIB', 'FACULTY', '--']:
            fac_code_clean = '--'
            fac_ref = None
        else:
            fac_code_clean = fac_code
            fac_ref = Faculty.objects.filter(short_code__iexact=fac_code_clean).first()

        st_obj = None
        et_obj = None
        if s.get('start_time'):
            try:
                parts = s['start_time'].split(':')
                st_obj = datetime.time(int(parts[0]), int(parts[1]))
            except Exception:
                pass
        if s.get('end_time'):
            try:
                parts = s['end_time'].split(':')
                et_obj = datetime.time(int(parts[0]), int(parts[1]))
            except Exception:
                pass

        evaluated.append({
            'start_slot_number': s['slot_number'],
            'end_slot_number': s['slot_number'],
            'slot_number_display': f"Slot {s['slot_number']}",
            'start_time': st_obj or s['start_time'],
            'end_time': et_obj or s['end_time'],
            'subject_code': s['subject_code'],
            'subject_name': s['subject_name'],
            'faculty_code': fac_code_clean,
            'faculty_ref': fac_ref,
            'lh_room': s['lh_room'],
            'section_name': s['section'],
            'status': status,
        })
    return evaluated

def group_evaluated_slots(slots_qs, target_day, target_time, current_day):
    return group_evaluated_csv_slots(slots_qs, target_day, target_time, current_day)

# Sync API endpoint for instant offline sync and notice check
def sync_check(request):
    routine_data = read_routine_csv()
    r_ver = get_routine_file_version()
    
    notices_qs = Notice.objects.filter(is_active=True)
    n_list = []
    latest_n_time = 0
    for n in notices_qs:
        n_list.append({
            'id': n.id,
            'notice': n.notice,
            'icon': n.icon or '',
            'n_url': n.n_url or '',
            'n_url_name': n.n_url_name or '',
            'n_url_icon': n.n_url_icon or ''
        })
        if hasattr(n, 'updated_at') and n.updated_at:
            ts = int(n.updated_at.timestamp())
            if ts > latest_n_time:
                latest_n_time = ts
                
    n_ver = f"{latest_n_time}_{len(n_list)}"
    
    unique_sections = sorted(list(set(row['section'] for row in routine_data if row.get('section'))))
    unique_years = sorted(list(set(str(row['year']) for row in routine_data if row.get('year'))))

    return JsonResponse({
        'status': 'success',
        'routine_version': str(r_ver),
        'notice_version': str(n_ver),
        'routine_data': routine_data,
        'notices': n_list,
        'sections': unique_sections,
        'years': unique_years,
    })

# Home View
def home(request):
    now = get_ist_now()
    today_date = now.date()
    today_time = now.time()
    today_day_code, today_day_name = DAYS_MAP[now.weekday()]

    # Fetch Mess Menu
    today_mess = DailyMessMenu.objects.filter(day_of_week=today_day_code).first()

    # Calculate Displayed Meal
    current_mins = today_time.hour * 60 + today_time.minute

    if current_mins < 10 * 60:
        meal_type_code = 'Breakfast'
        meal_title = "Today's Breakfast Menu"
        meal_food = today_mess.breakfast if today_mess else None
        meal_icon = 'coffee'
        time_1_2 = '07:45 AM - 08:45 AM'
        time_3_4 = '08:45 AM - 09:45 AM'
        is_serving = (7 * 60 + 45) <= current_mins <= (9 * 60 + 45)
    elif current_mins < 14 * 60 + 30:
        meal_type_code = 'Lunch'
        meal_title = "Today's Lunch Menu"
        meal_food = today_mess.lunch if today_mess else None
        meal_icon = 'soup'
        time_1_2 = '12:00 PM - 01:00 PM'
        time_3_4 = '01:00 PM - 02:00 PM'
        is_serving = (12 * 60) <= current_mins <= (14 * 60)
    elif current_mins < 18 * 60 + 30:
        meal_type_code = 'Evening Hi-Tea'
        meal_title = "Today's Evening Hi-Tea"
        meal_food = today_mess.hi_tea if today_mess else None
        meal_icon = 'cup-soda'
        time_1_2 = '05:00 PM - 05:30 PM'
        time_3_4 = '05:30 PM - 06:00 PM'
        is_serving = (17 * 60) <= current_mins <= (18 * 60)
    else:
        meal_type_code = 'Dinner'
        meal_title = "Today's Dinner Menu"
        meal_food = today_mess.dinner if today_mess else None
        meal_icon = 'utensils'
        time_1_2 = '08:00 PM - 09:00 PM'
        time_3_4 = '09:00 PM - 10:00 PM'
        is_serving = (20 * 60) <= current_mins <= (22 * 60)

    displayed_meal = {
        'type': meal_type_code,
        'title': meal_title,
        'food': meal_food,
        'icon': meal_icon,
        'time_1_2': time_1_2,
        'time_3_4': time_3_4,
        'is_serving': is_serving
    }

    # Fetch Active Meal
    active_meal = None
    all_timings = MessTiming.objects.all()
    for mt in all_timings:
        if mt.start_time <= today_time <= mt.end_time:
            active_meal = mt
            break

    # Fetch Today Induction
    today_induction = InductionProgram.objects.filter(date=today_date).first()

    # Fetch Today Routine from CSV
    all_sections = Section.objects.all()
    all_years = AcademicYear.objects.all()
    selected_sec = request.GET.get('sec', 'CSE - A')
    selected_year = request.GET.get('year', '1')
        
    csv_slots = get_filtered_routine_csv(year_filter=selected_year, sec_filter=selected_sec, day_filter=today_day_code)
    evaluated_routine = group_evaluated_csv_slots(csv_slots, today_day_code, today_time, today_day_code)
    live_slot = next((item for item in evaluated_routine if item['status'] == 'LIVE'), None)

    # Calculate Layout Priorities
    p_meal = 2
    p_induction = 3
    p_routine = 4

    is_induction_live = (today_induction and today_induction.status(today_date, today_time) == 'LIVE')
    is_routine_live = (live_slot is not None)
    is_meal_live = displayed_meal['is_serving']

    if is_induction_live:
        p_induction = 1
        p_routine = 2
        p_meal = 3
    elif is_routine_live:
        p_routine = 1
        p_meal = 2
        p_induction = 3
    elif is_meal_live:
        p_meal = 1
        p_induction = 2
        p_routine = 3
    else:
        if today_day_code in ['SUN', 'MON']:
            p_meal = 1
            p_induction = 2
            p_routine = 3
        elif current_mins < 10 * 60:
            p_meal = 1
            p_induction = 2
            p_routine = 3
        elif 10 * 60 <= current_mins < 12 * 60:
            p_induction = 1
            p_routine = 2
            p_meal = 3
        elif 12 * 60 <= current_mins < 14 * 60:
            p_meal = 1
            p_routine = 2
            p_induction = 3
        elif 14 * 60 <= current_mins < 17 * 60:
            p_routine = 1
            p_meal = 2
            p_induction = 3
        else:
            p_meal = 1
            p_routine = 2
            p_induction = 3

    if not evaluated_routine:
        p_routine = 99
    if not today_induction:
        p_induction = 99

    notice = Notice.objects.all()

    # fetch active events
    active_club_events = CommunityPost.objects.filter(
        status='PUBLISHED'
    ).filter(
        Q(event_status='CANCELLED') |
        Q(event_status='UPCOMING') |
        Q(event_date__gte=now) |
        Q(post_type='EVENT')
    ).select_related('community').order_by('event_date', '-created_at')[:4]

    # recent club posts
    recent_club_posts = CommunityPost.objects.filter(
        status='PUBLISHED'
    ).select_related('community').order_by('-created_at')[:6]

    context = {
        'now': now,
        'today_date_str': now.strftime('%A, %d %B %Y'),
        'today_time_str': now.strftime('%I:%M %p'),
        'today_day_code': today_day_code,
        'today_day_name': today_day_name,
        'today_mess': today_mess,
        'displayed_meal': displayed_meal,
        'active_meal': active_meal,
        'today_induction': today_induction,
        'live_slot': live_slot,
        'evaluated_routine': evaluated_routine,
        'selected_sec': selected_sec,
        'selected_year': selected_year,
        'all_sections': all_sections,
        'all_years': all_years,
        'p_meal': p_meal,
        'p_induction': p_induction,
        'p_routine': p_routine,
        'notice': notice,
        'active_club_events': active_club_events,
        'recent_club_posts': recent_club_posts,
    }
    return render(request, 'blog/home.html', context)

# Fetch search results
def get_search_data(query):
    query = (query or '').strip()
    query_lower = query.lower()
    terms = [t for t in query.split() if t]

    mess_results = None
    routine_results = None
    induction_results = None
    faculty_results = None
    branch_results = None
    notes_results = None
    assignments_results = None
    pyqs_results = None
    community_results = None
    post_results = None

    if query:
        day_code = DAY_LOOKUP.get(query_lower)
        if day_code:
            mess_results = DailyMessMenu.objects.filter(day_of_week=day_code)
            routine_results = RoutineSlot.objects.filter(day=day_code)

        if any(w in query_lower for w in ['1st', 'first', '1']):
            r_1st = RoutineSlot.objects.filter(section_name__name__icontains='1st')
            routine_results = (routine_results | r_1st).distinct() if routine_results else r_1st
        elif any(w in query_lower for w in ['2nd', 'second', '2']):
            r_2nd = RoutineSlot.objects.filter(section_name__name__icontains='2nd')
            routine_results = (routine_results | r_2nd).distinct() if routine_results else r_2nd

        fac_q = Q(name__icontains=query) | Q(short_code__icontains=query) | Q(designation__icontains=query)
        for w in terms:
            fac_q |= Q(name__icontains=w) | Q(short_code__icontains=w)
        faculty_results = Faculty.objects.filter(fac_q).select_related('branch').distinct()[:15]

        routine_q = (
            Q(subject_code__icontains=query) |
            Q(subject_name__icontains=query) |
            Q(faculty_code__icontains=query) |
            Q(lh_room__icontains=query) |
            Q(section_name__name__icontains=query)
        )
        for w in terms:
            routine_q |= Q(subject_code__icontains=w) | Q(subject_name__icontains=w) | Q(faculty_code__icontains=w)
        routine_matches = RoutineSlot.objects.filter(routine_q)
        routine_results = (routine_results | routine_matches).distinct() if routine_results else routine_matches

        ind_q = (
            Q(topic_programme__icontains=query) |
            Q(venue__icontains=query) |
            Q(assigned_persons_text__icontains=query) |
            Q(external_guest__icontains=query)
        )
        for w in terms:
            ind_q |= Q(topic_programme__icontains=w) | Q(assigned_persons_text__icontains=w)
        induction_results = InductionProgram.objects.filter(ind_q).distinct()[:10]

        mess_q = (
            Q(breakfast__icontains=query) |
            Q(lunch__icontains=query) |
            Q(hi_tea__icontains=query) |
            Q(dinner__icontains=query)
        )
        for w in terms:
            mess_q |= (
                Q(breakfast__icontains=w) |
                Q(lunch__icontains=w) |
                Q(hi_tea__icontains=w) |
                Q(dinner__icontains=w)
            )
        mess_matches = DailyMessMenu.objects.filter(mess_q)
        mess_results = (mess_results | mess_matches).distinct() if mess_results else mess_matches

        branch_results = Branch.objects.filter(
            Q(name__icontains=query) | Q(code__icontains=query)
        )[:10]

        notes_q = (
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(subject__name__icontains=query) |
            Q(subject__code__icontains=query) |
            Q(module__name__icontains=query) |
            Q(cr_name__icontains=query) |
            Q(cr__name__icontains=query)
        )
        for w in terms:
            notes_q |= (
                Q(title__icontains=w) |
                Q(description__icontains=w) |
                Q(subject__name__icontains=w) |
                Q(subject__code__icontains=w)
            )
        notes_results = Notes.objects.filter(notes_q).select_related('course', 'branch', 'year', 'section', 'subject').distinct()[:15]

        assign_q = (
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(subject__name__icontains=query) |
            Q(subject__code__icontains=query) |
            Q(author__icontains=query)
        )
        for w in terms:
            assign_q |= (
                Q(title__icontains=w) |
                Q(description__icontains=w) |
                Q(subject__name__icontains=w) |
                Q(subject__code__icontains=w)
            )
        assignments_results = Assignment.objects.filter(assign_q).select_related('course', 'branch', 'year', 'subject').distinct()[:15]

        pyqs_q = (
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(subject__name__icontains=query) |
            Q(subject__code__icontains=query) |
            Q(cr_name__icontains=query)
        )
        for w in terms:
            pyqs_q |= (
                Q(title__icontains=w) |
                Q(description__icontains=w) |
                Q(subject__name__icontains=w) |
                Q(subject__code__icontains=w)
            )
        pyqs_results = PYQ.objects.filter(pyqs_q).select_related('course', 'branch', 'year', 'subject').distinct()[:15]

        comm_q = (
            Q(group_name__icontains=query) |
            Q(group_dec__icontains=query) |
            Q(group_type__name__icontains=query) |
            Q(user__username__icontains=query)
        )
        for w in terms:
            comm_q |= (
                Q(group_name__icontains=w) |
                Q(group_dec__icontains=w) |
                Q(group_type__name__icontains=w)
            )
        community_results = Community.objects.filter(Q(is_active=True) & comm_q).select_related('group_type', 'user').distinct()[:15]

        post_q = (
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(venue__icontains=query) |
            Q(post_type__icontains=query) |
            Q(community__group_name__icontains=query) |
            Q(community__user__username__icontains=query)
        )
        for w in terms:
            post_q |= (
                Q(title__icontains=w) |
                Q(description__icontains=w) |
                Q(community__group_name__icontains=w)
            )
        post_results = CommunityPost.objects.filter(Q(status='PUBLISHED') & post_q).select_related('community', 'community__user').distinct()[:20]

    return {
        'mess_results': mess_results,
        'routine_results': routine_results,
        'induction_results': induction_results,
        'faculty_results': faculty_results,
        'branch_results': branch_results,
        'notes_results': notes_results,
        'assignments_results': assignments_results,
        'pyqs_results': pyqs_results,
        'community_results': community_results,
        'post_results': post_results,
    }

# Live search view
def live_search(request):
    query = request.GET.get('q', '').strip()
    data = get_search_data(query)
    data['query'] = query
    return render(request, 'blog/includes/live_search_results.html', data)

# Search page view
def search(request):
    query = request.GET.get('q', '').strip()
    data = get_search_data(query)
    data['query'] = query
    data['now'] = get_ist_now()
    return render(request, 'blog/search.html', data)

# Routine View
def routine(request):
    now = get_ist_now()
    today_time = now.time()
    today_day_code = DAYS_MAP[now.weekday()][0]

    all_sections = Section.objects.all()
    all_years = AcademicYear.objects.all()
    
    sec_filter = request.GET.get('sec', 'CSE - A')
    day_filter = request.GET.get('day', today_day_code)
    year_filter = request.GET.get('year', '1')

    slots = get_filtered_routine_csv(year_filter=year_filter, sec_filter=sec_filter, day_filter=day_filter)
    evaluated_slots = group_evaluated_csv_slots(slots, day_filter, today_time, today_day_code)

    context = {
        'sec_filter': sec_filter,
        'day_filter': day_filter,
        'year_filter': year_filter,
        'all_sections': all_sections,
        'all_years': all_years,
        'days_list': DAYS_LIST,
        'evaluated_slots': evaluated_slots,
        'today_day_code': today_day_code,
        'now': now,
    }
    return render(request, 'blog/routine.html', context)

# Induction Program View
def induction(request):
    now = get_ist_now()
    today_date = now.date()
    today_time = now.time()

    filter_tab = request.GET.get('tab', 'all')

    all_sessions = InductionProgram.objects.all().order_by('day_number', 'start_time')

    evaluated_list = []
    for sess in all_sessions:
        st = sess.status(today_date, today_time)

        if filter_tab == 'today' and sess.date != today_date:
            continue
        elif filter_tab == 'live' and st != 'LIVE':
            continue
        elif filter_tab == 'upcoming' and st != 'UPCOMING':
            continue
        elif filter_tab == 'past' and st != 'PAST':
            continue

        evaluated_list.append({
            'session': sess,
            'status': st
        })

    context = {
        'filter_tab': filter_tab,
        'evaluated_list': evaluated_list,
        'today_date': today_date,
        'now': now,
    }
    return render(request, 'blog/induction.html', context)

# Mess Menu View
def mess_menu(request):
    now = get_ist_now()
    today_time = now.time()
    today_day_code = DAYS_MAP[now.weekday()][0]

    all_menus = DailyMessMenu.objects.all()
    mess_timings_1_2 = MessTiming.objects.filter(academic_years__year='1').distinct()
    mess_timings_3_4 = MessTiming.objects.filter(academic_years__year='3').distinct()

    active_meal = None
    for mt in MessTiming.objects.all():
        if mt.start_time <= today_time <= mt.end_time:
            active_meal = mt
            break

    context = {
        'all_menus': all_menus,
        'today_day_code': today_day_code,
        'mess_timings_1_2': mess_timings_1_2,
        'mess_timings_3_4': mess_timings_3_4,
        'active_meal': active_meal,
        'now': now,
    }
    return render(request, 'blog/mess_menu.html', context)


def about(request):
    faculties = Faculty.objects.filter(is_active=True).select_related('branch')
    branches = Branch.objects.all()
    return render(request, 'blog/about.html', {'faculties': faculties, 'branches': branches})

# show 403 page
def custom_403(request, exception=None):
    return render(request, 'errors/403.html', status=403)

def custom_404(request, exception=None):
    return render(request, 'errors/404.html', status=404)

def custom_500(request):
    return render(request, 'errors/500.html', status=500)


# Testing Function's Broooooo Wait

# Main Page View
def pooling_page(request):
    # Get the latest pool object or create one if it doesn't exist
    obj, created = Pooling.objects.get_or_create(id=1)
    
    # Check if user already voted today using cookies
    already_voted = 'today_attendance' in request.COOKIES
    
    context = {
        'pool_count': f"{((obj.pool)/50)*100}%",
        'already_voted': already_voted
    }
    return render(request, 'blog/pooling.html', context)

# HTMX Live Update View (Handles Click)
def mark_attendance(request):
    obj, created = Pooling.objects.get_or_create(id=1)
    
    # Increment count only if cookie is not present
    if 'today_attendance' not in request.COOKIES:
        obj.pool += 1
        obj.save()
    
    # Prepare HTML chunk to return to HTMX
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = f'<span id="live-count">{((obj.pool)/50)*100}%</span>'
    
    response = HttpResponse(html)
    
    # Save current date-time in cookie named 'today_attendance' (expires in 1 day)
    response.set_cookie('today_attendance', current_time, max_age=86400)
    return response

# HTMX Live Counter View (For polling/auto-refreshing globally)
def live_counter(request):
    obj, created = Pooling.objects.get_or_create(id=1)
    return HttpResponse(f'<span id="live-count">{((obj.pool)/50)*100}%</span>')

# Submit User Feedback / Bug Report
def submit_feedback(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        category = request.POST.get('category', 'BUG')
        contact = request.POST.get('contact', '').strip()
        message_text = request.POST.get('message', '').strip()

        if name and message_text:
            Feedback.objects.create(
                name=name,
                category=category,
                contact=contact,
                message=message_text
            )
            messages.success(request, 'Thank you! Your feedback has been sent to the developer.')
        else:
            messages.error(request, 'Please provide both your name and feedback message.')

    return redirect(request.META.get('HTTP_REFERER', 'home'))

# Qr-Code
def qr_code(request):
    return render(request, 'blog/qr.html')

# Study View
def study(request):
    return render(request, 'blog/study.html')

# Notes View
def notes(request):
    course_id = request.GET.get('course', '').strip()
    branch_id = request.GET.get('branch', '').strip()
    year_id = request.GET.get('year', '').strip()
    section_id = request.GET.get('section', '').strip()
    subject_id = request.GET.get('subject', '').strip()
    search_query = request.GET.get('q', '').strip()

    notes_qs = Notes.objects.select_related('course', 'branch', 'year', 'section', 'subject', 'module', 'cr').prefetch_related('images').all()

    if course_id:
        notes_qs = notes_qs.filter(course_id=course_id)
    if branch_id:
        notes_qs = notes_qs.filter(branch_id=branch_id)
    if year_id:
        notes_qs = notes_qs.filter(year_id=year_id)
    if section_id:
        notes_qs = notes_qs.filter(section_id=section_id)
    if subject_id:
        notes_qs = notes_qs.filter(subject_id=subject_id)
    if search_query:
        notes_qs = notes_qs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(subject__name__icontains=search_query) |
            Q(subject__code__icontains=search_query) |
            Q(module__name__icontains=search_query) |
            Q(cr_name__icontains=search_query) |
            Q(cr__name__icontains=search_query)
        )

    all_courses = Course.objects.all()
    all_branches = Branch.objects.all()
    all_years = AcademicYear.objects.all()
    all_sections = Section.objects.all()
    all_subjects = Subject.objects.all()

    context = {
        'notes': notes_qs,
        'all_courses': all_courses,
        'all_branches': all_branches,
        'all_years': all_years,
        'all_sections': all_sections,
        'all_subjects': all_subjects,
        'selected_course': course_id,
        'selected_branch': branch_id,
        'selected_year': year_id,
        'selected_section': section_id,
        'selected_subject': subject_id,
        'search_query': search_query,
    }
    return render(request, 'blog/notes.html', context)


# Previous Year Questions View
def pyqs(request):
    course_id = request.GET.get('course', '').strip()
    branch_id = request.GET.get('branch', '').strip()
    year_id = request.GET.get('year', '').strip()
    semester = request.GET.get('semester', '').strip()
    subject_id = request.GET.get('subject', '').strip()
    exam_year = request.GET.get('exam_year', '').strip()
    search_query = request.GET.get('q', '').strip()

    pyqs_qs = PYQ.objects.select_related('course', 'branch', 'year', 'subject').prefetch_related('images').all()

    if course_id:
        pyqs_qs = pyqs_qs.filter(course_id=course_id)
    if branch_id:
        pyqs_qs = pyqs_qs.filter(branch_id=branch_id)
    if year_id:
        pyqs_qs = pyqs_qs.filter(year_id=year_id)
    if semester:
        pyqs_qs = pyqs_qs.filter(semester=semester)
    if subject_id:
        pyqs_qs = pyqs_qs.filter(subject_id=subject_id)
    if exam_year:
        pyqs_qs = pyqs_qs.filter(exam_year=exam_year)
    if search_query:
        pyqs_qs = pyqs_qs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(subject__name__icontains=search_query) |
            Q(subject__code__icontains=search_query) |
            Q(cr_name__icontains=search_query)
        )

    all_courses = Course.objects.all()
    all_branches = Branch.objects.all()
    all_years = AcademicYear.objects.all()
    all_subjects = Subject.objects.all()
    semesters_list = PYQ.SEMESTER_CHOICES

    context = {
        'pyqs': pyqs_qs,
        'all_courses': all_courses,
        'all_branches': all_branches,
        'all_years': all_years,
        'all_subjects': all_subjects,
        'semesters_list': semesters_list,
        'selected_course': course_id,
        'selected_branch': branch_id,
        'selected_year': year_id,
        'selected_semester': semester,
        'selected_subject': subject_id,
        'selected_exam_year': exam_year,
        'search_query': search_query,
    }
    return render(request, 'blog/pyqs.html', context)


def assignments(request):
    course_id = request.GET.get('course', '').strip()
    branch_id = request.GET.get('branch', '').strip()
    year_id = request.GET.get('year', '').strip()
    semester = request.GET.get('semester', '').strip()
    subject_id = request.GET.get('subject', '').strip()
    search_query = request.GET.get('q', '').strip()

    assignments = Assignment.objects.select_related('course', 'branch', 'year', 'subject')

    if course_id:
        assignments = assignments.filter(course_id=course_id)
    if branch_id:
        assignments = assignments.filter(branch_id=branch_id)
    if year_id:
        assignments = assignments.filter(year_id=year_id)
    if semester:
        assignments = assignments.filter(semester=semester)
    if subject_id:
        assignments = assignments.filter(subject_id=subject_id)
    if search_query:
        assignments = assignments.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(subject__name__icontains=search_query) |
            Q(subject__code__icontains=search_query) |
            Q(author__icontains=search_query)
        )

    all_courses = Course.objects.all()
    all_branches = Branch.objects.all()
    all_years = AcademicYear.objects.all()
    all_subjects = Subject.objects.all()
    semesters_list = PYQ.SEMESTER_CHOICES

    context = {
        'assignments': assignments,
        'all_courses': all_courses,
        'all_branches': all_branches,
        'all_years': all_years,
        'all_subjects': all_subjects,
        'semesters_list': semesters_list,
        'selected_course': course_id,
        'selected_branch': branch_id,
        'selected_year': year_id,
        'selected_semester': semester,
        'selected_subject': subject_id,
        'search_query': search_query,
    }
    return render(request, 'blog/assignments.html', context)

# show community list
def community(request):
    community = Community.objects.filter(is_active=True).select_related('group_type', 'user').order_by('group_type__name', 'id')
    context = {
        "community": community,
        "coming_soon": "Community features are rolling out step by step. Stay tuned as new tools arrive!"
    }
    return render(request, 'blog/community.html', context)

# single community profile
def community_page(request, username):
    community = Community.objects.filter(user__username__iexact=username, is_active=True).select_related('group_type', 'user').first()
    if not community:
        return render(request, 'errors/404.html', status=404)

    is_owner = request.user.is_authenticated and (request.user == community.user or request.user.is_superuser)
    
    # get club posts
    if is_owner:
        posts = community.posts.all().prefetch_related('images').order_by('-created_at')
    else:
        posts = community.posts.filter(status='PUBLISHED').prefetch_related('images').order_by('-created_at')

    context = {
        "community": community,
        "is_owner": is_owner,
        "posts": posts,
    }
    return render(request, 'blog/includes/community_page.html', context)

# View post detail
def community_post_detail(request, username, slug):
    community = Community.objects.filter(user__username__iexact=username, is_active=True).select_related('group_type', 'user').first()
    if not community:
        return render(request, 'errors/404.html', status=404)

    is_owner = request.user.is_authenticated and (request.user == community.user or request.user.is_superuser)

    # Fetch post item
    post_qs = community.posts.prefetch_related('images')
    if not is_owner:
        post_qs = post_qs.filter(status='PUBLISHED')

    post = post_qs.filter(slug=slug).first()
    if not post and slug.isdigit():
        post = post_qs.filter(id=int(slug)).first()

    if not post:
        return render(request, 'errors/404.html', status=404)

    context = {
        "community": community,
        "post": post,
        "is_owner": is_owner,
    }
    return render(request, 'blog/community_post_detail.html', context)

# user login page
def community_login(request):
    # check user login
    if request.user.is_authenticated:
        if hasattr(request.user, 'community_profile') and request.user.community_profile:
            return redirect('community_page', username=request.user.username)
        return redirect('home')

    next_url = request.GET.get('next') or request.POST.get('next') or ''

    # Extract username from next URL
    parts = urlparse(next_url).path.strip('/').split('/')
    username_url = parts[1] if len(parts) > 1 and parts[0] == 'community' else False
    print(username_url)

    # check form post
    if request.method == 'POST':
        uname = request.POST.get('username', '').strip().lower()
        pwd = request.POST.get('password', '').strip()

        # check user pass
        user = authenticate(request, username=uname, password=pwd)

        if user is not None:
            auth_login(request, user)
            messages.success(request, f"Welcome back, @{user.username}!")

            if next_url:
                return redirect(next_url)

            if hasattr(user, 'community_profile') and user.community_profile:
                return redirect('community_page', username=user.username)

            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'blog/community_login.html', {
        'next': next_url,
        'username_url': username_url
    })

# user logout view
def community_logout(request):
    auth_logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('community')

# add post view
@login_required(login_url='community_login')
def community_post_create(request, username):
    # check login user
    if not request.user.is_authenticated:
        messages.warning(request, "Please login first to create posts.")
        return redirect(f"/login?next=/community/{username}/post/")

    community = Community.objects.filter(user__username__iexact=username, is_active=True).select_related('group_type', 'user').first()
    if not community:
        return render(request, 'errors/404.html', status=404)

    # check owner access
    if request.user != community.user and not request.user.is_superuser:
        return render(request, 'errors/403.html', status=403)

    # save form data
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        post_type = request.POST.get('post_type', 'BLOG')
        status = request.POST.get('status', 'PUBLISHED')
        venue = request.POST.get('venue', '').strip()
        event_status = request.POST.get('event_status', '')
        link_title = request.POST.get('link_title', '').strip()
        link_url = request.POST.get('link_url', '').strip()
        cover_image = request.FILES.get('cover_image')
        event_date = request.POST.get('event_date') or None

        # validate title text
        if not title or not description:
            messages.error(request, "Title and description are required.")
            return render(request, 'blog/community_post_create.html', {
                'community': community,
                'post_types': CommunityPost.POST_TYPES,
                'status_choices': CommunityPost.STATUS_CHOICES,
            })

        # create new post
        post = CommunityPost.objects.create(
            community=community,
            title=title,
            description=description,
            post_type=post_type,
            status=status,
            venue=venue,
            event_status=event_status,
            link_title=link_title,
            link_url=link_url,
            cover_image=cover_image,
            event_date=event_date,
            published_at=timezone.now() if status == 'PUBLISHED' else None
        )

        # save gallery images
        gallery_images = request.FILES.getlist('gallery_images')
        for idx, img in enumerate(gallery_images):
            CommunityPostImage.objects.create(post=post, image=img, order=idx)

        messages.success(request, "Post created successfully!")
        return redirect('community_page', username=community.username)

    return render(request, 'blog/community_post_create.html', {
        'community': community,
        'post_types': CommunityPost.POST_TYPES,
        'status_choices': CommunityPost.STATUS_CHOICES,
    })

# edit post view
@login_required(login_url='community_login')
def community_post_edit(request, username, post_id):
    # check login user
    if not request.user.is_authenticated:
        messages.warning(request, "Please login first to edit posts.")
        return redirect('community_login')

    community = Community.objects.filter(user__username__iexact=username, is_active=True).first()
    if not community:
        return render(request, 'errors/404.html', status=404)

    # check owner access
    if request.user != community.user and not request.user.is_superuser:
        return render(request, 'errors/403.html', status=403)

    post = CommunityPost.objects.filter(community=community, id=post_id).first()
    if not post:
        return render(request, 'errors/404.html', status=404)

    # update post data
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        post_type = request.POST.get('post_type', 'BLOG')
        status = request.POST.get('status', 'PUBLISHED')
        venue = request.POST.get('venue', '').strip()
        event_status = request.POST.get('event_status', '')
        link_title = request.POST.get('link_title', '').strip()
        link_url = request.POST.get('link_url', '').strip()
        cover_image = request.FILES.get('cover_image')
        event_date = request.POST.get('event_date') or None

        # validate title text
        if not title or not description:
            messages.error(request, "Title and description are required.")
            return render(request, 'blog/community_post_create.html', {
                'community': community,
                'post': post,
                'is_edit': True,
                'post_types': CommunityPost.POST_TYPES,
                'status_choices': CommunityPost.STATUS_CHOICES,
            })

        post.title = title
        post.description = description
        post.post_type = post_type
        post.status = status
        post.venue = venue
        post.event_status = event_status
        post.link_title = link_title
        post.link_url = link_url
        post.event_date = event_date

        if cover_image:
            post.cover_image = cover_image

        if status == 'PUBLISHED' and not post.published_at:
            post.published_at = timezone.now()

        post.save()

        # save gallery images
        gallery_images = request.FILES.getlist('gallery_images')
        for idx, img in enumerate(gallery_images):
            CommunityPostImage.objects.create(post=post, image=img, order=idx)

        messages.success(request, "Post updated successfully!")
        return redirect('community_post_detail', username=community.username, slug=post.slug)

    return render(request, 'blog/community_post_create.html', {
        'community': community,
        'post': post,
        'is_edit': True,
        'post_types': CommunityPost.POST_TYPES,
        'status_choices': CommunityPost.STATUS_CHOICES,
    })

# delete post item
@login_required(login_url='community_login')
def community_post_delete(request, username, post_id):
    # check login user
    if not request.user.is_authenticated:
        return redirect('community_login')

    community = Community.objects.filter(user__username__iexact=username).first()
    if not community or (request.user != community.user and not request.user.is_superuser):
        return render(request, 'errors/403.html', status=403)

    post = CommunityPost.objects.filter(community=community, id=post_id).first()
    if post:
        post.delete()
        messages.success(request, "Post deleted successfully.")
    return redirect('community_page', username=username)

# community edit
def community_edit(request, username):
    community = Community.objects.filter(
        user__username__iexact=username
    ).first()

    # Check profile ownership
    if not community or (
        request.user != community.user
        and not request.user.is_superuser
    ):
        return render(
            request,
            'errors/403.html',
            status=403
        )

    if request.method == 'POST':
        group_name = request.POST.get('group_name', '').strip()
        group_dec = request.POST.get('group_dec', '').strip()

        if not group_name:
            messages.error(request, 'Club name is required.')
        else:
            community.group_name = group_name
            community.group_dec = group_dec

            # Update group type
            group_type_id = request.POST.get('group_type')
            if group_type_id:
                community.group_type = CommunityGroupType.objects.filter(
                    pk=group_type_id
                ).first()
            else:
                community.group_type = None

            # Update social links
            for field in [
                'instagram', 'facebook', 'linkedin',
                'discord', 'other', 'other_title', 'join'
            ]:
                setattr(
                    community,
                    field,
                    request.POST.get(field, '').strip()
                )

            # Update logo only if a new file is uploaded
            if request.FILES.get('group_logo'):
                community.group_logo = request.FILES['group_logo']

            community.save()
            messages.success(request, 'Profile updated successfully!')

            return redirect(
                'community_page',
                username=community.username
            )

    context = {
        'community': community,
        'group_types': CommunityGroupType.objects.all().order_by('name'),
    }

    return render(
        request,
        'blog/community_edit.html',
        context
    )