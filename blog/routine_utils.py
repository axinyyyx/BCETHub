import os
import csv
import time
from datetime import datetime
from django.conf import settings
from django.utils import timezone

def get_csv_file_path():
    media_path = os.path.join(settings.MEDIA_ROOT, 'routine', 'routine.csv')
    if os.path.exists(media_path):
        return media_path
    static_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'routine.csv')
    if os.path.exists(static_path):
        return static_path
    return media_path

def get_routine_file_version():
    """Returns timestamp string representing routine file version."""
    path = get_csv_file_path()
    if os.path.exists(path):
        return str(int(os.path.getmtime(path)))
    try:
        from blog.models import RoutineFile
        rf = RoutineFile.objects.filter(is_active=True).order_by('-updated_at').first()
        if rf and rf.updated_at:
            return str(int(rf.updated_at.timestamp()))
    except Exception:
        pass
    return "1"

def read_routine_csv():
    """Reads routine from CSV and returns list of dictionaries."""
    path = get_csv_file_path()
    if not os.path.exists(path):
        return []
    
    slots = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                try:
                    slot_num = int(row.get('slot_number', 1))
                except ValueError:
                    slot_num = 1
                
                fac_code = (row.get('faculty_code') or '').strip()
                if not fac_code or fac_code.upper() in ['LIB', 'FACULTY', '--']:
                    fac_code_clean = '--'
                else:
                    fac_code_clean = fac_code

                slots.append({
                    'id': idx + 1,
                    'year': str(row.get('year', '1')).strip(),
                    'branch': str(row.get('branch', 'CSE')).strip(),
                    'section': str(row.get('section', 'A')).strip(),
                    'lh_room': str(row.get('lh_room', '')).strip(),
                    'day': str(row.get('day', 'MON')).strip().upper(),
                    'slot_number': slot_num,
                    'start_time': str(row.get('start_time', '')).strip(),
                    'end_time': str(row.get('end_time', '')).strip(),
                    'subject_code': str(row.get('subject_code', '')).strip(),
                    'subject_name': str(row.get('subject_name', '')).strip(),
                    'faculty_code': fac_code_clean,
                })
    except Exception as e:
        print(f"Error reading routine CSV: {e}")
        return []
    return slots

def evaluate_slot_status(slot, target_day, target_time_str, current_day):
    """
    Evaluates status (LIVE, UPCOMING, PAST) based on target_day, current_day, and time string.
    """
    days_order = {'MON': 0, 'TUE': 1, 'WED': 2, 'THU': 3, 'FRI': 4, 'SAT': 5, 'SUN': 6}
    t_day_idx = days_order.get(target_day, 0)
    c_day_idx = days_order.get(current_day, 0)

    if t_day_idx < c_day_idx:
        return 'PAST'
    elif t_day_idx > c_day_idx:
        return 'UPCOMING'
    
    if not slot.get('start_time') or not slot.get('end_time'):
        return 'PAST'
    
    try:
        if isinstance(target_time_str, str):
            now_t = datetime.strptime(target_time_str[:5], '%H:%M').time()
        else:
            now_t = target_time_str
        
        s_time = datetime.strptime(slot['start_time'][:5], '%H:%M').time()
        e_time = datetime.strptime(slot['end_time'][:5], '%H:%M').time()
        
        if now_t < s_time:
            return 'UPCOMING'
        elif s_time <= now_t <= e_time:
            return 'LIVE'
        else:
            return 'PAST'
    except Exception:
        return 'PAST'

def get_filtered_routine_csv(year_filter=None, sec_filter=None, day_filter=None, query=None):
    all_slots = read_routine_csv()
    filtered = []
    
    for s in all_slots:
        if year_filter and str(s['year']) != str(year_filter):
            continue
        if sec_filter and s['section'].lower() != str(sec_filter).lower():
            continue
        if day_filter and s['day'].upper() != str(day_filter).upper():
            continue
        if query:
            q = query.lower()
            match = (
                q in s['subject_code'].lower() or
                q in s['subject_name'].lower() or
                q in s['faculty_code'].lower() or
                q in s['lh_room'].lower() or
                q in s['section'].lower() or
                q in s['day'].lower()
            )
            if not match:
                continue
        filtered.append(s)
        
    filtered.sort(key=lambda x: x['slot_number'])
    return filtered
