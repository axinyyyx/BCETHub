from django.contrib import admin
from .models import Branch, AcademicYear, Pooling, Faculty, InductionProgram, MessTiming, DailyMessMenu, RoutineSlot, Feedback

@admin.register(Pooling)
class PoolingAdmin(admin.ModelAdmin):
     list_display = ['id', 'pool']
     
@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('year', 'get_year_display')

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_code', 'designation', 'branch', 'is_active')
    list_filter = ('designation', 'branch', 'is_active')
    search_fields = ('name', 'short_code', 'email')

@admin.register(InductionProgram)
class InductionProgramAdmin(admin.ModelAdmin):
    list_display = ('day_number', 'date', 'start_time', 'end_time', 'topic_programme', 'venue', 'material_file')
    list_filter = ('date', 'venue')
    search_fields = ('topic_programme', 'external_guest', 'assigned_persons_text')
    filter_horizontal = ('assigned_faculty', 'branches_applicable')

@admin.register(RoutineSlot)
class RoutineSlotAdmin(admin.ModelAdmin):
    list_display = ('section_name', 'lh_room', 'day', 'slot_number', 'start_time', 'end_time', 'subject_code', 'faculty_code')
    list_filter = ('section_name', 'lh_room', 'day')
    search_fields = ('section_name', 'subject_code', 'faculty_code', 'subject_name')

@admin.register(MessTiming)
class MessTimingAdmin(admin.ModelAdmin):
    list_display = ('meal_type', 'start_time', 'end_time', 'get_years')
    list_filter = ('meal_type', 'academic_years')
    filter_horizontal = ('academic_years',)

    def get_years(self, obj):
        return ", ".join([y.get_year_display() for y in obj.academic_years.all()])
    get_years.short_description = 'Academic Years'

@admin.register(DailyMessMenu)
class DailyMessMenuAdmin(admin.ModelAdmin):
    list_display = ('day_of_week', 'breakfast', 'lunch', 'hi_tea', 'dinner')
    list_filter = ('day_of_week',)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'created_at', 'short_message')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'message')

    def short_message(self, obj):
        return obj.message[:60] + "..." if len(obj.message) > 60 else obj.message
    short_message.short_description = 'Message Preview'

