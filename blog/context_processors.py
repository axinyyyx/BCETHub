
from blog.models import Holiday
from django.utils import timezone
from django.db.models import Q

# get holidays
def holiday_(request):
    today = timezone.localdate()

    active_class_holidays = list(
        Holiday.objects.filter(
            is_class=True,
        ).filter(
            Q(holiday_start__lte=today, holiday_end__gte=today) |
            Q(holiday_start=today, holiday_end__isnull=True) |
            Q(holiday_start__isnull=True, holiday_end=today)
        ).order_by("holiday_start")
    )

    active_mess_holidays = list(
        Holiday.objects.filter(
            is_mess=True,
        ).filter(
            Q(holiday_start__lte=today, holiday_end__gte=today) |
            Q(holiday_start=today, holiday_end__isnull=True) |
            Q(holiday_start__isnull=True, holiday_end=today)
        ).order_by("holiday_start")
    )

    return {
        "holiday_": Holiday.objects.all(),
        "today_": today,
        "active_class_holidays": active_class_holidays,
        "active_mess_holidays": active_mess_holidays,
    }

