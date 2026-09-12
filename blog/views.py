import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Branch, AcademicYear, Pooling, Faculty, InductionProgram, RoutineSlot, MessTiming, DailyMessMenu, Feedback
from django.http import HttpResponse
from datetime import datetime

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

UNIQUE_SECTIONS = [
    'CSE 1st SEM (A)',
    'CSE 1st SEM (B)',
    'CSE 1st SEM (C)',
    'CSE (AIML) 1st SEM',
    '(ECE + EE) 1st SEM',
    '(CSE(DS)+IT+ME+CE) 1st SEM',
]

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

    # Fetch Today Routine
    selected_sec = request.GET.get('sec', 'CSE 1st SEM (A)')
    routine_slots = RoutineSlot.objects.filter(section_name=selected_sec, day=today_day_code).order_by('slot_number')
    
    evaluated_routine = []
    live_slot = None
    for slot in routine_slots:
        st = slot.status(today_day_code, today_time)
        if st == 'LIVE':
            live_slot = slot
        evaluated_routine.append({
            'slot': slot,
            'status': st
        })

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
        'all_sections': UNIQUE_SECTIONS,
        'p_meal': p_meal,
        'p_induction': p_induction,
        'p_routine': p_routine,
    }
    return render(request, 'blog/home.html', context)

# Live Search View
def live_search(request):
    query = request.GET.get('q', '').strip()
    query_lower = query.lower()

    mess_results = None
    routine_results = None
    induction_results = None
    faculty_results = None
    branch_results = None

    if query:
        day_code = DAY_LOOKUP.get(query_lower)
        if day_code:
            mess_results = DailyMessMenu.objects.filter(day_of_week=day_code)
            routine_results = RoutineSlot.objects.filter(day=day_code)

        faculty_results = Faculty.objects.filter(
            Q(name__icontains=query) |
            Q(short_code__icontains=query) |
            Q(designation__icontains=query)
        )

        routine_matches = RoutineSlot.objects.filter(
            Q(subject_code__icontains=query) |
            Q(subject_name__icontains=query) |
            Q(faculty_code__icontains=query) |
            Q(lh_room__icontains=query) |
            Q(section_name__icontains=query)
        )
        routine_results = (routine_results | routine_matches).distinct() if routine_results else routine_matches

        induction_results = InductionProgram.objects.filter(
            Q(topic_programme__icontains=query) |
            Q(venue__icontains=query) |
            Q(assigned_persons_text__icontains=query)
        )

        mess_matches = DailyMessMenu.objects.filter(
            Q(breakfast__icontains=query) |
            Q(lunch__icontains=query) |
            Q(hi_tea__icontains=query) |
            Q(dinner__icontains=query)
        )
        mess_results = (mess_results | mess_matches).distinct() if mess_results else mess_matches

        branch_results = Branch.objects.filter(
            Q(name__icontains=query) | Q(code__icontains=query)
        )

    context = {
        'query': query,
        'faculty_results': faculty_results,
        'routine_results': routine_results,
        'mess_results': mess_results,
        'induction_results': induction_results,
        'branch_results': branch_results,
    }
    return render(request, 'blog/includes/live_search_results.html', context)

# Search View
def search(request):
    query = request.GET.get('q', '').strip()
    query_lower = query.lower()

    mess_results = None
    routine_results = None
    induction_results = None
    faculty_results = None
    branch_results = None

    now = get_ist_now()

    if query:
        day_code = DAY_LOOKUP.get(query_lower)
        if day_code:
            mess_results = DailyMessMenu.objects.filter(day_of_week=day_code)
            routine_results = RoutineSlot.objects.filter(day=day_code)

        if '1st' in query_lower or '1' in query_lower or 'first' in query_lower:
            routine_results = (routine_results | RoutineSlot.objects.filter(section_name__icontains='1st')).distinct() if routine_results else RoutineSlot.objects.filter(section_name__icontains='1st')
        elif '2nd' in query_lower or '2' in query_lower or 'second' in query_lower:
            routine_results = RoutineSlot.objects.filter(section_name__icontains='2nd')
        
        faculty_results = Faculty.objects.filter(
            Q(name__icontains=query) |
            Q(short_code__icontains=query) |
            Q(designation__icontains=query)
        )

        induction_results = InductionProgram.objects.filter(
            Q(topic_programme__icontains=query) |
            Q(venue__icontains=query) |
            Q(assigned_persons_text__icontains=query) |
            Q(external_guest__icontains=query)
        )

        routine_matches = RoutineSlot.objects.filter(
            Q(subject_code__icontains=query) |
            Q(subject_name__icontains=query) |
            Q(faculty_code__icontains=query) |
            Q(lh_room__icontains=query) |
            Q(section_name__icontains=query)
        )
        routine_results = (routine_results | routine_matches).distinct() if routine_results else routine_matches

        mess_matches = DailyMessMenu.objects.filter(
            Q(breakfast__icontains=query) |
            Q(lunch__icontains=query) |
            Q(hi_tea__icontains=query) |
            Q(dinner__icontains=query)
        )
        mess_results = (mess_results | mess_matches).distinct() if mess_results else mess_matches

        branch_results = Branch.objects.filter(
            Q(name__icontains=query) | Q(code__icontains=query)
        )

    context = {
        'query': query,
        'mess_results': mess_results,
        'routine_results': routine_results,
        'induction_results': induction_results,
        'faculty_results': faculty_results,
        'branch_results': branch_results,
        'now': now,
    }
    return render(request, 'blog/search.html', context)

# Routine View
def routine(request):
    now = get_ist_now()
    today_time = now.time()
    today_day_code = DAYS_MAP[now.weekday()][0]

    sec_filter = request.GET.get('sec', 'CSE 1st SEM (A)')
    day_filter = request.GET.get('day', today_day_code)

    slots = RoutineSlot.objects.filter(section_name=sec_filter, day=day_filter).order_by('slot_number')
    
    evaluated_slots = []
    for s in slots:
        st = s.status(target_day=day_filter, target_time=today_time, current_day=today_day_code)
        evaluated_slots.append({
            'slot': s,
            'status': st
        })

    context = {
        'sec_filter': sec_filter,
        'day_filter': day_filter,
        'all_sections': UNIQUE_SECTIONS,
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
        message_text = request.POST.get('message', '').strip()

        if name and message_text:
            Feedback.objects.create(
                name=name,
                category=category,
                message=message_text
            )
            messages.success(request, 'Thank you! Your feedback has been sent to the developer.')
        else:
            messages.error(request, 'Please provide both your name and feedback message.')

    return redirect(request.META.get('HTTP_REFERER', 'home'))

# Qr-Code
def qr_code(request):
    return render(request, 'blog/qr.html')

# Notes View
def notes(request):
    return render(request, 'blog/notes.html')