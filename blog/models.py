from django.db import models
from django.utils import timezone

class Course(models.Model):
    name = models.CharField(max_length=100, help_text="e.g. B.Tech, M.Tech, MBA")
    code = models.CharField(max_length=20, unique=True, help_text="e.g. BTECH, MTECH, MBA")

    class Meta:
        verbose_name_plural = "Courses"

    def __str__(self):
        return f"{self.name} ({self.code})"

# Academic Branch 
class Branch(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=100, help_text="e.g. Computer Science & Engineering")
    code = models.CharField(max_length=20, unique=True, help_text="e.g. CSE, CSE-AIML, ECE, EE, IT, ME, CE")

    class Meta:
        verbose_name_plural = "Branches"

    def __str__(self):
        return f"{self.name} ({self.code})"

# Academic Year Management
class AcademicYear(models.Model):
    YEAR_CHOICES = [
        ('1', '1st Year'),
        ('2', '2nd Year'),
        ('3', '3rd Year'),
        ('4', '4th Year'),
    ]
    year = models.CharField(max_length=2, choices=YEAR_CHOICES, unique=True)

    def __str__(self):
        return f"{self.get_year_display()}"

class Section(models.Model):
    name = models.CharField(max_length=100, help_text="e.g. A, B, C")
    def __str__(self):
        return self.name

# Faculty Directory for the College
class Faculty(models.Model):
    DESIGNATION_CHOICES = [
        ('HOD', 'Head of Department'),
        ('PROF', 'Professor'),
        ('ASSOC_PROF', 'Associate Professor'),
        ('ASST_PROF', 'Assistant Professor'),
        ('STAFF', 'Supporting Staff'),
    ]

    name = models.CharField(max_length=100)
    short_code = models.CharField(max_length=30, blank=True, null=True, help_text="e.g. AR(PH), BA(M), RKA(PH)")
    designation = models.CharField(max_length=20, choices=DESIGNATION_CHOICES, default='ASST_PROF')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='faculties')
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Faculties"
        ordering = ['name']

    def __str__(self):
        code_str = f" [{self.short_code}]" if self.short_code else ""
        return f"{self.name}{code_str} - {self.get_designation_display()} ({self.branch.code})"


# Induction Program for 1st Year Students
class InductionProgram(models.Model):
    day_number = models.IntegerField(help_text="e.g. 1, 2, 3... 21")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    topic_programme = models.CharField(max_length=255, help_text="e.g. AI & Next Generation, Universal Human Values")
    assigned_faculty = models.ManyToManyField(Faculty, blank=True, related_name='induction_sessions')
    assigned_persons_text = models.CharField(max_length=255, blank=True, null=True, help_text="Text representation of speakers")
    external_guest = models.CharField(max_length=200, blank=True, null=True, help_text="Any external speaker name")
    venue = models.CharField(max_length=150, default="CSE Seminar Hall")
    branches_applicable = models.ManyToManyField(Branch, blank=True, help_text="Applicable for specific or all branches")
    material_file = models.FileField(upload_to='induction_materials/', blank=True, null=True, help_text="Upload session PDF or PPT presentation")

    class Meta:
        ordering = ['day_number', 'start_time']
        verbose_name = "Induction Program Session"
        verbose_name_plural = "Induction Program Schedule"

    def __str__(self):
        return f"Day {self.day_number} ({self.date.strftime('%d/%m/%Y')}) | {self.topic_programme}"

    def status(self, target_date=None, target_time=None):
        if target_date is None:
            now = timezone.localtime()
            target_date = now.date()
            target_time = now.time()

        if self.date < target_date:
            return 'PAST'
        elif self.date > target_date:
            return 'UPCOMING'
        else: 
            if target_time < self.start_time:
                return 'UPCOMING'
            elif self.start_time <= target_time <= self.end_time:
                return 'LIVE'
            else:
                return 'PAST'

# Class Routine Timetable
class RoutineSlot(models.Model):
    DAY_CHOICES = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
    ]

    year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='routine_slots')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='routine_slots')
    section_name = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='routine_slots')
    lh_room = models.CharField(max_length=50, help_text="e.g. LH-234, LH-232, LH-231, LH-233, LH-235, LH-236")
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    slot_number = models.IntegerField(help_text="Slot 1-9")
    start_time = models.TimeField()
    end_time = models.TimeField()
    subject_code = models.CharField(max_length=100, help_text="e.g. BS-PH 101, ES-EE 101, Induction Program")
    subject_name = models.CharField(max_length=150, blank=True, null=True, help_text="Full subject name if any")
    faculty_code = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. AR(PH), BA(M), NF(EE)")
    faculty_ref = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True, related_name='routine_slots')

    class Meta:
        ordering = ['section_name', 'day', 'slot_number']
        verbose_name = "Class Routine Slot"
        verbose_name_plural = "Class Routine Timetable"

    def __str__(self):
        return f"{self.section_name} ({self.lh_room}) | {self.get_day_display()} Slot {self.slot_number}: {self.subject_code}"

    def status(self, target_day=None, target_time=None, current_day=None):
        now = timezone.localtime()
        days_map = {0: 'MON', 1: 'TUE', 2: 'WED', 3: 'THU', 4: 'FRI', 5: 'SAT', 6: 'SUN'}

        if current_day is None:
            current_day = days_map[now.weekday()]
        if target_time is None:
            target_time = now.time()
        if target_day is None:
            target_day = current_day

        if self.day != target_day:
            return 'OTHER_DAY'

        # Only evaluate live status for current actual day
        if target_day != current_day:
            return 'SCHEDULED'

        if target_time < self.start_time:
            return 'UPCOMING'
        elif self.start_time <= target_time <= self.end_time:
            return 'LIVE'
        else:
            return 'PAST'

# Mess Menu for the Hostel
class MessTiming(models.Model):
    MEAL_CHOICES = [
        ('BREAKFAST', 'Breakfast'),
        ('LUNCH', 'Lunch'),
        ('HI_TEA', 'Evening Hi-Tea'),
        ('DINNER', 'Dinner'),
    ]
    
    meal_type = models.CharField(max_length=20, choices=MEAL_CHOICES)
    academic_years = models.ManyToManyField(AcademicYear, help_text="Select 1st & 2nd Year OR 3rd & 4th Year")
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        years = ", ".join([y.get_year_display() for y in self.academic_years.all()])
        return f"{self.get_meal_type_display()} ({years}): {self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')}"

    def status(self, target_time=None):
        if target_time is None:
            target_time = timezone.localtime().time()
            
        if target_time < self.start_time:
            return 'UPCOMING'
        elif self.start_time <= target_time <= self.end_time:
            return 'LIVE'
        else:
            return 'PAST'

# Daily Mess Menu for the Hostel
class DailyMessMenu(models.Model):
    DAY_CHOICES = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
    ]

    day_of_week = models.CharField(max_length=3, choices=DAY_CHOICES, unique=True)
    breakfast = models.TextField(help_text="Items served during Breakfast")
    lunch = models.TextField(help_text="Items served during Lunch")
    hi_tea = models.TextField(help_text="Items served during Evening Tea/Snacks")
    dinner = models.TextField(help_text="Items served during Dinner")

    class Meta:
        verbose_name = "Daily Mess Menu"
        verbose_name_plural = "Hostel Mess Menus"

    def __str__(self):
        return f"Mess Menu - {self.get_day_of_week_display()}"

class Pooling(models.Model):
    pool = models.IntegerField(default=0)

    def __str__(self):
        return f"{((self.pool)/50)*100}%"


# User Feedback
class Feedback(models.Model):
    CATEGORY_CHOICES = [
        ('BUG', 'Bug Report'),
        ('IDEA', 'Suggestion / Idea'),
        ('OTHER', 'General Feedback'),
    ]

    name = models.CharField(max_length=100, help_text="User Name")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='BUG')
    message = models.TextField(help_text="User Message")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "User Feedback"
        verbose_name_plural = "User Feedbacks"

    def __str__(self):
        return f"[{self.get_category_display()}] {self.name} ({self.created_at.strftime('%d/%m/%Y')})"

class CRProfile(models.Model):
    name = models.CharField(max_length=100, help_text="CR Name")
    year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='cr_profiles')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='cr_profiles')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='cr_profiles')
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Class Representative Profiles"
        ordering = ['branch', 'section', 'name']

    def __str__(self):
        return f"{self.name} - {self.branch.code} Section {self.section}"

class Module(models.Model):
    name = models.CharField(max_length=100, help_text="Name of the module")
    code = models.CharField(max_length=20, unique=True, help_text="e.g. DSA01, CN01")

    class Meta:
        verbose_name_plural = "Modules"

    def __str__(self):
        return f"{self.name} ({self.code})"

class Subject(models.Model):
    name = models.CharField(max_length=200, help_text="Name of the subject")
    code = models.CharField(max_length=20, unique=True, help_text="e.g. DSA, CN, DBMS")
    
    class Meta:
        verbose_name_plural = "Subjects"

    def __str__(self):
        return f"{self.name} ({self.code})"

class Notes(models.Model):
    title = models.CharField(max_length=200, help_text="Title of the notes")
    description = models.TextField(help_text="Brief description of the notes")
    file = models.FileField(upload_to='notes_files/', blank=True, null=True, help_text="Upload the notes file (PDF, DOCX, etc.)")
    year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='notes')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='notes')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='notes')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='notes')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='notes', blank=True, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='notes', blank=True, null=True)
    cr = models.ForeignKey(CRProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='notes', help_text="CR who provided this note")
    cr_name = models.CharField(max_length=100, blank=True, null=True, help_text="CR / Author Name e.g. Rishabh Kumar")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name_plural = "Notes"

    def __str__(self):
        return f"{self.title} - {self.branch.code} Section {self.section}"

    def get_cr_name(self):
        if self.cr:
            return self.cr.name
        elif self.cr_name:
            return self.cr_name
        return "CR / Contributor"

import io
from PIL import Image
from django.core.files.base import ContentFile

class NoteImage(models.Model):
    note = models.ForeignKey(Notes, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='notes_images/')
    caption = models.CharField(max_length=150, blank=True, null=True, help_text="Optional caption for page e.g. Page 1")
    order = models.PositiveIntegerField(default=0, help_text="Order/Page Number")

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Note Image"
        verbose_name_plural = "Note Images"

    def __str__(self):
        return f"Image {self.order} for {self.note.title}"

    def save(self, *args, **kwargs):
        if self.image and hasattr(self.image, 'file'):
            try:
                img = Image.open(self.image)
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                orig_w, orig_h = img.size
                if orig_w > 2000 or orig_h > 2000:
                    img.thumbnail((2000, 2000), Image.Resampling.LANCZOS)
                
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=88, optimize=True)
                output.seek(0)
                
                filename = self.image.name.rsplit('.', 1)[0] + '.jpg'
                self.image.save(filename, ContentFile(output.read()), save=False)
            except Exception:
                pass
        super().save(*args, **kwargs)


class PYQ(models.Model):
    SEMESTER_CHOICES = [
        ('1', '1st Semester'),
        ('2', '2nd Semester'),
        ('3', '3rd Semester'),
        ('4', '4th Semester'),
        ('5', '5th Semester'),
        ('6', '6th Semester'),
        ('7', '7th Semester'),
        ('8', '8th Semester'),
    ]

    title = models.CharField(max_length=200, help_text="Title of the PYQ (e.g. End Sem Exam 2024)")
    description = models.TextField(blank=True, null=True, help_text="Details / instructions for this paper")
    file = models.FileField(upload_to='pyq_files/', blank=True, null=True, help_text="Upload PYQ PDF or DOCX file")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='pyqs')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='pyqs')
    year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='pyqs')
    semester = models.CharField(max_length=2, choices=SEMESTER_CHOICES, default='1')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='pyqs', blank=True, null=True)
    exam_year = models.IntegerField(default=2024, help_text="e.g. 2023, 2024, 2025")
    cr_name = models.CharField(max_length=100, blank=True, null=True, help_text="Uploaded by CR / Contributor")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-exam_year', '-uploaded_at']
        verbose_name = "Previous Year Question"
        verbose_name_plural = "Previous Year Questions (PYQs)"

    def __str__(self):
        return f"{self.title} - {self.get_semester_display()} ({self.exam_year})"

    def get_cr_name(self):
        return self.cr_name if self.cr_name else "CR / Contributor"


class PYQImage(models.Model):
    pyq = models.ForeignKey(PYQ, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='pyq_images/')
    caption = models.CharField(max_length=150, blank=True, null=True, help_text="e.g. Question Paper Page 1")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "PYQ Image"
        verbose_name_plural = "PYQ Images"

    def __str__(self):
        return f"Page {self.order} for {self.pyq.title}"

    def save(self, *args, **kwargs):
        if self.image and hasattr(self.image, 'file'):
            try:
                img = Image.open(self.image)
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                orig_w, orig_h = img.size
                if orig_w > 2000 or orig_h > 2000:
                    img.thumbnail((2000, 2000), Image.Resampling.LANCZOS)
                
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=88, optimize=True)
                output.seek(0)
                
                filename = self.image.name.rsplit('.', 1)[0] + '.jpg'
                self.image.save(filename, ContentFile(output.read()), save=False)
            except Exception:
                pass
        super().save(*args, **kwargs)