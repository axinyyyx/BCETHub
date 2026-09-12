import datetime
from django.core.management.base import BaseCommand
from blog.models import Branch, AcademicYear, Faculty, InductionProgram, RoutineSlot, MessTiming, DailyMessMenu

class Command(BaseCommand):
    help = "Seed database with BCET Induction, Routine Timetable, Mess Menu, and Faculty directory data"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Starting database seeding..."))

        # Seed Department Branches
        branches_data = [
            ('Computer Science & Engineering', 'CSE'),
            ('Computer Science & Engineering (AI & ML)', 'CSE-AIML'),
            ('Computer Science & Engineering (Data Science)', 'CSE-DS'),
            ('Electronics & Communication Engineering', 'ECE'),
            ('Electrical Engineering', 'EE'),
            ('Information Technology', 'IT'),
            ('Mechanical Engineering', 'ME'),
            ('Civil Engineering', 'CE'),
        ]
        branch_objs = {}
        for name, code in branches_data:
            obj, _ = Branch.objects.get_or_create(code=code, defaults={'name': name})
            branch_objs[code] = obj

        # Seed Academic Years
        years_data = ['1', '2', '3', '4']
        year_objs = {}
        for y in years_data:
            obj, _ = AcademicYear.objects.get_or_create(year=y)
            year_objs[y] = obj

        # Seed Faculty Members
        faculties_data = [
            ('Prof. (Dr.) Santanu Koley', 'SKK', 'HOD', 'CSE'),
            ('Mr. S.S. Choubey', 'SSC', 'STAFF', 'CSE'),
            ('Mr. S.K. Shukla', 'SKS', 'STAFF', 'CSE'),
            ('Dr. Santanu Modak', 'SM(IT)', 'HOD', 'IT'),
            ('Mr. Swarup Kr. Hazra Choudhury', 'SKHC(AIML)', 'HOD', 'CSE-AIML'),
            ('Mr. Sk. Abdul Rahim', 'SAR(CSE)', 'HOD', 'CSE'),
            ('Dr. V. P. Roy', 'VPR(ECE)', 'HOD', 'ECE'),
            ('Mr. Mintu Ghosh', 'MG(ME)', 'HOD', 'ME'),
            ('Mrs. Supriya Saha Banik', 'SSB(ENG)', 'HOD', 'CSE'),
            ('Mr. Avhijit Ghosh', 'AG(M)', 'HOD', 'CSE'),
            ('Mrs. Prabali Dutta', 'PD(CE)', 'HOD', 'CE'),
            ('Dr. R. K. Aggarwala', 'RKA(PH)', 'HOD', 'CSE'),
            ('Dr. Dinesh Dey', 'DD(CH)', 'HOD', 'CSE'),
            ('Prof. (Dr.) Ratul Kr. Mazumdar', 'RKM(CSE)', 'PROF', 'CSE'),
            ('Prof. (Dr.) Sankar Mukherjee', 'SM(CSE)', 'PROF', 'CSE'),
            ('Dr. Amit Kumar', 'AK(CSE)', 'ASSOC_PROF', 'CSE'),
            ('Mr. Sajal Chakraborty', 'SC(CSE)', 'ASST_PROF', 'CSE'),
            ('Mrs. Kamaljeet Kaur', 'KK(EE)', 'ASST_PROF', 'EE'),
            ('Ms. Sneha Choudhury', 'SC(ENG)', 'ASST_PROF', 'CSE'),
            ('Mr. Gopal Chandra Das', 'GCD(ECE)', 'ASST_PROF', 'ECE'),
            ('Mr. Shiv Prasad', 'SP(IT)', 'ASST_PROF', 'IT'),
            ('Dr. Rakhi Das Ban', 'RDB(CSE)', 'ASSOC_PROF', 'CSE'),
            ('Dr. Sangeeta Sen', 'SS(IT)', 'ASST_PROF', 'IT'),
            ('Prof. (Dr.) P.K. Prasad', 'PKP(EE)', 'PROF', 'EE'),
            ('Mr. Rakesh Yadav', 'RY(TPO)', 'STAFF', 'CSE'),
            
            # Short code routine faculties
            ('Prof. AR (Physics)', 'AR(PH)', 'ASST_PROF', 'CSE'),
            ('Prof. BA (Maths)', 'BA(M)', 'ASST_PROF', 'CSE'),
            ('Prof. NF (EE)', 'NF(EE)', 'ASST_PROF', 'EE'),
            ('Prof. BKJ (Mechanical)', 'BKJ(ME)', 'ASST_PROF', 'ME'),
            ('Prof. AA (English)', 'AA(Eng)', 'ASST_PROF', 'CSE'),
            ('Prof. MM (CS)', 'MM(CS)', 'ASST_PROF', 'CSE'),
            ('Prof. BC (Physics)', 'BC(PH)', 'ASST_PROF', 'CSE'),
            ('Prof. PPP (CS)', 'PPP(CS)', 'ASST_PROF', 'CSE'),
            ('Prof. AS (EE)', 'AS(EE)', 'ASST_PROF', 'EE'),
            ('Prof. PKC (CS)', 'PKC(CS)', 'ASST_PROF', 'CSE'),
            ('Prof. RG (Maths)', 'RG(M)', 'ASST_PROF', 'CSE'),
            ('Prof. IM (AIML)', 'IM(AIML)', 'ASST_PROF', 'CSE-AIML'),
            ('Prof. AR (ME)', 'AR(ME)', 'ASST_PROF', 'ME'),
            ('Prof. AC (Chemistry)', 'AC(CH)', 'ASST_PROF', 'CSE'),
            ('Prof. SD (Maths)', 'SD(M)', 'ASST_PROF', 'CSE'),
            ('Prof. RS (EE)', 'RS(EE)', 'ASST_PROF', 'EE'),
            ('Prof. GKP (ME)', 'GKP(ME)', 'ASST_PROF', 'ME'),
            ('Prof. RB (IT)', 'RB(IT)', 'ASST_PROF', 'IT'),
        ]

        faculty_objs = {}
        for name, short_code, desig, bcode in faculties_data:
            fac, _ = Faculty.objects.get_or_create(
                short_code=short_code,
                defaults={
                    'name': name,
                    'designation': desig,
                    'branch': branch_objs.get(bcode, branch_objs['CSE']),
                    'is_active': True
                }
            )
            faculty_objs[short_code] = fac

        # Seed Induction Program
        induction_data = [
            (1, datetime.date(2026, 8, 19), datetime.time(10, 30), datetime.time(12, 0),
             "Orientation Programme", "Introductory Speeches by: Principal, Registrar, Asst. Registrar, TPO & All HODs", "CSE Seminar Hall"),
            (1, datetime.date(2026, 8, 19), datetime.time(14, 0), datetime.time(16, 0),
             "Campus Visit & Interaction with Faculty Mentors", "Respective HODs & Faculty Mentors", "Central Library, Workshop, Physics & Chemistry Labs"),
            (2, datetime.date(2026, 8, 20), datetime.time(10, 30), datetime.time(12, 0),
             "Training & Placement Activities", "Mr. Rakesh Yadav", "CSE Seminar Hall"),
            (3, datetime.date(2026, 8, 21), datetime.time(10, 30), datetime.time(12, 0),
             "AI & Next Generation", "Dr. Santanu Modak (HOD, IT) & Mr. Swarup Kr. Hazra Choudhury (HOD, AI & ML)", "CSE Seminar Hall"),
            (4, datetime.date(2026, 8, 22), datetime.time(10, 30), datetime.time(11, 30),
             "Universal Human Values (HUV)", "Mr. Sk. Abdul Rahim (HOD, CSE)", "CSE Seminar Hall"),
            (4, datetime.date(2026, 8, 22), datetime.time(11, 30), datetime.time(12, 0),
             "MOOCS & NPTEL", "Mr. Shiv Prasad, IT", "CSE Seminar Hall"),
            (5, datetime.date(2026, 8, 25), datetime.time(10, 30), datetime.time(12, 0),
             "Spiritual Talk", "Dr. R. K. Aggarwala (HOD, Physics) & External Expert", "CSE Seminar Hall"),
            (6, datetime.date(2026, 8, 27), datetime.time(10, 30), datetime.time(12, 0),
             "Innovation & Entrepreneurship", "Dr. Santanu Modak (HOD, IT) & Mr. Swarup Kr. Hazra Choudhury (HOD, AI & ML)", "CSE Seminar Hall"),
            (7, datetime.date(2026, 8, 29), datetime.time(10, 30), datetime.time(12, 0),
             "AI & its Future Scope", "Prof. (Dr.) Ratul Kr. Mazumdar (CSE) & Prof. (Dr.) Sankar Mukherjee (CSE)", "CSE Seminar Hall"),
            (8, datetime.date(2026, 9, 1), datetime.time(10, 30), datetime.time(12, 0),
             "Importance of Core branches in Engineering", "Dr. V. P. Roy (HOD, ECE) & Mr. Mintu Ghosh (HOD, ME)", "CSE Seminar Hall"),
            (9, datetime.date(2026, 9, 2), datetime.time(10, 30), datetime.time(12, 0),
             "Yoga & Meditation", "Mr. S.K. Shukla (Assistant Registrar) & External Expert", "CSE Seminar Hall"),
            (10, datetime.date(2026, 9, 8), datetime.time(10, 30), datetime.time(12, 0),
             "English Proficiency", "Mrs. Supriya Saha Banik (HOD, English)", "CSE Seminar Hall"),
            (11, datetime.date(2026, 9, 9), datetime.time(10, 30), datetime.time(12, 0),
             "Creative & Performing Arts", "Ms. Sneha Choudhury (English)", "CSE Seminar Hall"),
            (12, datetime.date(2026, 9, 10), datetime.time(10, 30), datetime.time(12, 0),
             "CSE/AI & ML/DS as backbone of Leading Industry", "Dr. Amit Kumar (CSE) & Mr. Sajal Chakraborty (CSE)", "CSE Seminar Hall"),
            (13, datetime.date(2026, 9, 11), datetime.time(10, 30), datetime.time(12, 0),
             "Diagnostic Test (Mathematics)", "Mr. Avhijit Ghosh (HOD, Maths)", "CSE Seminar Hall"),
            (14, datetime.date(2026, 9, 12), datetime.time(10, 30), datetime.time(12, 0),
             "Importance of Core branches in Engineering", "Mrs. Kamaljeet Kaur (EE) & Mrs. Prabali Dutta (HOD, CE)", "CSE Seminar Hall"),
            (15, datetime.date(2026, 9, 15), datetime.time(10, 30), datetime.time(12, 0),
             "Diagnostic Test (Physics)", "Dr. R. K. Aggarwala (HOD, Physics)", "CSE Seminar Hall"),
            (16, datetime.date(2026, 9, 16), datetime.time(10, 30), datetime.time(12, 0),
             "NSS Activities", "Mr. Gopal Chandra Das (ECE) & Mr. Shiv Prasad (IT)", "CSE Seminar Hall"),
            (17, datetime.date(2026, 9, 18), datetime.time(10, 30), datetime.time(12, 0),
             "Diagnostic Test (English)", "Mrs. Supriya Saha Banik (HOD, English)", "CSE Seminar Hall"),
            (18, datetime.date(2026, 9, 19), datetime.time(10, 30), datetime.time(12, 0),
             "Diagnostic Test (Chemistry)", "Dr. Dinesh Dey (HOD, Chemistry)", "CSE Seminar Hall"),
            (19, datetime.date(2026, 9, 22), datetime.time(10, 30), datetime.time(12, 0),
             "Sports & Games Activities", "Mr. Gopal Chandra Das (ECE) & Mr. Shiv Prasad (IT)", "Playground"),
            (20, datetime.date(2026, 9, 23), datetime.time(10, 30), datetime.time(12, 0),
             "CSE/AI & ML/DS as backbone of Leading Industry", "Dr. Rakhi Das Ban (CSE) & Dr. Sangeeta Sen (IT)", "CSE Seminar Hall"),
            (21, datetime.date(2026, 9, 24), datetime.time(10, 30), datetime.time(12, 0),
             "Motivational Speech & Conclusion", "Prof. (Dr.) Santanu Koley (Principal), Mr. S.S. Choubey (Registrar), Prof. (Dr.) P.K. Prasad (EE)", "CSE Seminar Hall"),
        ]

        InductionProgram.objects.all().delete()
        for day_num, dt, st, et, topic, persons, venue in induction_data:
            InductionProgram.objects.create(
                day_number=day_num,
                date=dt,
                start_time=st,
                end_time=et,
                topic_programme=topic,
                assigned_persons_text=persons,
                venue=venue
            )

        # Seed Class Routine
        RoutineSlot.objects.all().delete()

        time_slots = {
            1: (datetime.time(10, 30), datetime.time(12, 0)), # Combined Slots 1-4: 10:30 AM - 12:00 PM
            5: (datetime.time(12, 0), datetime.time(13, 0)),  # Slot 5: LUNCH Break 12:00 PM - 01:00 PM
            7: (datetime.time(14, 0), datetime.time(15, 0)),  # Slot 7: 02:00 PM - 03:00 PM
            8: (datetime.time(15, 0), datetime.time(16, 0)),  # Slot 8: 03:00 PM - 04:00 PM
            9: (datetime.time(16, 0), datetime.time(17, 0)),  # Slot 9: 04:00 PM - 05:00 PM
        }

        def add_routine(sec, room, day, slot_num, sub_code, sub_name, fac_code):
            st, et = time_slots[slot_num]
            fac_ref = faculty_objs.get(fac_code, None)
            RoutineSlot.objects.create(
                section_name=sec,
                lh_room=room,
                day=day,
                slot_number=slot_num,
                start_time=st,
                end_time=et,
                subject_code=sub_code,
                subject_name=sub_name or sub_code,
                faculty_code=fac_code,
                faculty_ref=fac_ref
            )

        sections_list = [
            ("CSE 1st SEM (A)", "LH-234"),
            ("CSE 1st SEM (B)", "LH-235"),
            ("CSE 1st SEM (C)", "LH-236"),
            ("CSE (AIML) 1st SEM", "LH-232"),
            ("(ECE + EE) 1st SEM", "LH-231"),
            ("(CSE(DS)+IT+ME+CE) 1st SEM", "LH-233"),
        ]

        days = ['TUE', 'WED', 'THU', 'FRI', 'SAT']

        # Add single Induction Program slot (10:30 AM - 12:00 PM) and Lunch (12:00 PM - 1:00 PM) for all 6 sections on TUE-SAT
        for sec, room in sections_list:
            for day in days:
                add_routine(sec, room, day, 1, "Induction Program", "21-Day Induction Program (10:30 AM - 12:00 PM)", "BCET")
                add_routine(sec, room, day, 5, "LUNCH", "Hostel Lunch Break (12:00 PM - 01:00 PM)", "MESS")

        # Period routines for Slot 7, 8, 9
        # CSE 1st SEM (A)
        add_routine("CSE 1st SEM (A)", "LH-234", "TUE", 7, "BS-PH 101", "Physics-I", "AR(PH)")
        add_routine("CSE 1st SEM (A)", "LH-234", "TUE", 8, "BS-M 101", "Mathematics-I", "BA(M)")
        add_routine("CSE 1st SEM (A)", "LH-234", "TUE", 9, "ES-EE 101", "Basic Electrical", "NF(EE)")

        add_routine("CSE 1st SEM (A)", "LH-234", "WED", 7, "BS-M 101", "Mathematics-I", "BA(M)")
        add_routine("CSE 1st SEM (A)", "LH-234", "WED", 8, "BS-PH 101", "Physics-I", "AR(PH)")
        add_routine("CSE 1st SEM (A)", "LH-234", "WED", 9, "ES-EE 101", "Basic Electrical", "NF(EE)")

        add_routine("CSE 1st SEM (A)", "LH-234", "THU", 7, "ES-ME 192", "Engineering Graphics/Workshop", "BKJ(ME)")
        add_routine("CSE 1st SEM (A)", "LH-234", "THU", 8, "BS-M 101", "Mathematics-I", "BA(M)")
        add_routine("CSE 1st SEM (A)", "LH-234", "THU", 9, "BS-PH 101", "Physics-I", "AR(PH)")

        add_routine("CSE 1st SEM (A)", "LH-234", "FRI", 7, "BS-M 101", "Mathematics-I", "BA(M)")
        add_routine("CSE 1st SEM (A)", "LH-234", "FRI", 8, "ES-EE 101", "Basic Electrical", "NF(EE)")
        add_routine("CSE 1st SEM (A)", "LH-234", "FRI", 9, "Soft Skill", "English Communication", "AA(Eng)")

        add_routine("CSE 1st SEM (A)", "LH-234", "SAT", 7, "BS-PH 101", "Physics-I", "AR(PH)")
        add_routine("CSE 1st SEM (A)", "LH-234", "SAT", 8, "ES-EE 101", "Basic Electrical", "NF(EE)")
        add_routine("CSE 1st SEM (A)", "LH-234", "SAT", 9, "Basic Computing", "Basic Computing (CS)", "MM(CS)")

        # CSE 1st SEM (B)
        add_routine("CSE 1st SEM (B)", "LH-235", "TUE", 7, "ES-EE 101", "Basic Electrical", "NF(EE)")
        add_routine("CSE 1st SEM (B)", "LH-235", "TUE", 8, "BS-PH 101", "Physics-I", "BC(PH)")
        add_routine("CSE 1st SEM (B)", "LH-235", "TUE", 9, "Soft Skill", "English Communication", "AA(Eng)")

        add_routine("CSE 1st SEM (B)", "LH-235", "WED", 7, "BS-PH 101", "Physics-I", "BC(PH)")
        add_routine("CSE 1st SEM (B)", "LH-235", "WED", 8, "BS-M 101", "Mathematics-I", "BA(M)")
        add_routine("CSE 1st SEM (B)", "LH-235", "WED", 9, "ES-ME 192", "Engineering Workshop", "BKJ(ME)")

        add_routine("CSE 1st SEM (B)", "LH-235", "THU", 7, "BS-M 101", "Mathematics-I", "BA(M)")
        add_routine("CSE 1st SEM (B)", "LH-235", "THU", 8, "ES-EE 101", "Basic Electrical", "NF(EE)")
        add_routine("CSE 1st SEM (B)", "LH-235", "THU", 9, "Basic Computing", "Basic Computing PPP", "PPP(CS)")

        add_routine("CSE 1st SEM (B)", "LH-235", "FRI", 7, "ES-EE 101", "Basic Electrical", "NF(EE)")
        add_routine("CSE 1st SEM (B)", "LH-235", "FRI", 8, "BS-PH 101", "Physics-I", "BC(PH)")
        add_routine("CSE 1st SEM (B)", "LH-235", "FRI", 9, "BS-M 101", "Mathematics-I", "BA(M)")

        add_routine("CSE 1st SEM (B)", "LH-235", "SAT", 7, "ES-EE 101", "Basic Electrical", "NF(EE)")
        add_routine("CSE 1st SEM (B)", "LH-235", "SAT", 8, "BS-M 101", "Mathematics-I", "BA(M)")
        add_routine("CSE 1st SEM (B)", "LH-235", "SAT", 9, "BS-PH 101", "Physics-I", "BC(PH)")

        # CSE 1st SEM (C)
        add_routine("CSE 1st SEM (C)", "LH-236", "TUE", 7, "BS-M 101", "Mathematics-I", "AG(M)")
        add_routine("CSE 1st SEM (C)", "LH-236", "TUE", 8, "ES-EE 101", "Basic Electrical", "AS(EE)")
        add_routine("CSE 1st SEM (C)", "LH-236", "TUE", 9, "Bridge Class", "Physics Bridge Class", "RKA(PH)")

        add_routine("CSE 1st SEM (C)", "LH-236", "WED", 7, "ES-EE 101", "Basic Electrical", "AS(EE)")
        add_routine("CSE 1st SEM (C)", "LH-236", "WED", 8, "BS-M 101", "Mathematics-I", "AG(M)")
        add_routine("CSE 1st SEM (C)", "LH-236", "WED", 9, "BS-PH 101", "Physics-I", "RKA(PH)")

        add_routine("CSE 1st SEM (C)", "LH-236", "THU", 7, "BS-PH 101", "Physics-I", "RKA(PH)")
        add_routine("CSE 1st SEM (C)", "LH-236", "THU", 8, "ES-EE 101", "Basic Electrical", "AS(EE)")
        add_routine("CSE 1st SEM (C)", "LH-236", "THU", 9, "BS-M 101", "Mathematics-I", "AG(M)")

        add_routine("CSE 1st SEM (C)", "LH-236", "FRI", 7, "BS-PH 101", "Physics-I", "RKA(PH)")
        add_routine("CSE 1st SEM (C)", "LH-236", "FRI", 8, "ES-EE 101", "Basic Electrical", "AS(EE)")
        add_routine("CSE 1st SEM (C)", "LH-236", "FRI", 9, "Basic Computing", "Basic Computing PKC", "PKC(CS)")

        add_routine("CSE 1st SEM (C)", "LH-236", "SAT", 7, "BS-M 101", "Mathematics-I", "AG(M)")
        add_routine("CSE 1st SEM (C)", "LH-236", "SAT", 8, "BS-PH 101", "Physics-I", "RKA(PH)")
        add_routine("CSE 1st SEM (C)", "LH-236", "SAT", 9, "ES-ME 192", "Engineering Workshop", "BKJ(ME)")

        # CSE (AIML) 1st SEM
        add_routine("CSE (AIML) 1st SEM", "LH-232", "TUE", 7, "ES-EE 101", "Basic Electrical", "AS(EE)")
        add_routine("CSE (AIML) 1st SEM", "LH-232", "TUE", 8, "BS-PH 101", "Physics-I", "AR(PH)")
        add_routine("CSE (AIML) 1st SEM", "LH-232", "TUE", 9, "BS-M 101", "Mathematics-I", "RG(M)")

        add_routine("CSE (AIML) 1st SEM", "LH-232", "WED", 7, "Soft Skill", "English Communication", "SC(ENG)")
        add_routine("CSE (AIML) 1st SEM", "LH-232", "WED", 8, "BS-M 101", "Mathematics-I", "RG(M)")
        add_routine("CSE (AIML) 1st SEM", "LH-232", "WED", 9, "BS-PH 101", "Physics-I", "AR(PH)")

        add_routine("CSE (AIML) 1st SEM", "LH-232", "THU", 7, "ES-EE 101", "Basic Electrical", "AS(EE)")
        add_routine("CSE (AIML) 1st SEM", "LH-232", "THU", 8, "Basic Computing", "Basic Computing (AIML)", "IM(AIML)")
        add_routine("CSE (AIML) 1st SEM", "LH-232", "THU", 9, "BS-M 101", "Mathematics-I", "RG(M)")

        add_routine("CSE (AIML) 1st SEM", "LH-232", "FRI", 7, "ES-EE 101", "Basic Electrical", "AS(EE)")
        add_routine("CSE (AIML) 1st SEM", "LH-232", "FRI", 8, "BS-PH 101", "Physics-I", "AR(PH)")
        add_routine("CSE (AIML) 1st SEM", "LH-232", "FRI", 9, "ES-ME 192", "Engineering Workshop", "AR(ME)")

        add_routine("CSE (AIML) 1st SEM", "LH-232", "SAT", 7, "BS-M 101", "Mathematics-I", "RG(M)")
        add_routine("CSE (AIML) 1st SEM", "LH-232", "SAT", 8, "BS-PH 101", "Physics-I", "AR(PH)")
        add_routine("CSE (AIML) 1st SEM", "LH-232", "SAT", 9, "ES-EE 101", "Basic Electrical", "AS(EE)")

        # (ECE + EE) 1st SEM
        add_routine("(ECE + EE) 1st SEM", "LH-231", "TUE", 7, "BS-CH 101", "Chemistry", "AC(CH)")
        add_routine("(ECE + EE) 1st SEM", "LH-231", "TUE", 8, "BS-M 102", "Mathematics-II", "SD(M)")
        add_routine("(ECE + EE) 1st SEM", "LH-231", "TUE", 9, "ES-EE 101", "Basic Electrical", "RS(EE)")

        add_routine("(ECE + EE) 1st SEM", "LH-231", "WED", 7, "ES-EE 101", "Basic Electrical", "RS(EE)")
        add_routine("(ECE + EE) 1st SEM", "LH-231", "WED", 8, "BS-CH 101", "Chemistry", "AC(CH)")
        add_routine("(ECE + EE) 1st SEM", "LH-231", "WED", 9, "BS-M 102", "Mathematics-II", "SD(M)")

        add_routine("(ECE + EE) 1st SEM", "LH-231", "THU", 7, "BS-M 102", "Mathematics-II", "SD(M)")
        add_routine("(ECE + EE) 1st SEM", "LH-231", "THU", 8, "ES-EE 101", "Basic Electrical", "RS(EE)")
        add_routine("(ECE + EE) 1st SEM", "LH-231", "THU", 9, "Soft Skill", "English Communication", "AA(ENG)")

        add_routine("(ECE + EE) 1st SEM", "LH-231", "FRI", 7, "BS-CH 101", "Chemistry", "AC(CH)")
        add_routine("(ECE + EE) 1st SEM", "LH-231", "FRI", 8, "BS-M 102", "Mathematics-II", "SD(M)")
        add_routine("(ECE + EE) 1st SEM", "LH-231", "FRI", 9, "Bridge Class", "Physics Bridge Class", "AR(PH)")

        add_routine("(ECE + EE) 1st SEM", "LH-231", "SAT", 7, "BS-CH 101", "Chemistry", "AC(CH)")
        add_routine("(ECE + EE) 1st SEM", "LH-231", "SAT", 8, "ES-EE 101", "Basic Electrical", "RS(EE)")
        add_routine("(ECE + EE) 1st SEM", "LH-231", "SAT", 9, "ES-ME 191", "Engineering Graphics", "GKP(ME)")

        # (CSE(DS)+IT+ME+CE) 1st SEM
        add_routine("(CSE(DS)+IT+ME+CE) 1st SEM", "LH-233", "TUE", 7, "ES-ME 192", "Engineering Workshop", "BKJ(ME)")
        add_routine("(CSE(DS)+IT+ME+CE) 1st SEM", "LH-233", "TUE", 8, "BS-M 101", "Mathematics-I", "RG(M)")
        add_routine("(CSE(DS)+IT+ME+CE) 1st SEM", "LH-233", "TUE", 9, "BS-PH 101", "Physics-I", "BC(PH)")

        add_routine("(CSE(DS)+IT+ME+CE) 1st SEM", "LH-233", "WED", 7, "Basic Computing", "Basic Computing RB", "RB(IT)")
        add_routine("(CSE(DS)+IT+ME+CE) 1st SEM", "LH-233", "WED", 8, "BS-PH 101", "Physics-I", "BC(PH)")
        add_routine("(CSE(DS)+IT+ME+CE) 1st SEM", "LH-233", "WED", 9, "BS-M 101", "Mathematics-I", "RG(M)")

        add_routine("(CSE(DS)+IT+ME+CE) 1st SEM", "LH-233", "THU", 7, "BS-M 101", "Mathematics-I", "RG(M)")
        add_routine("(CSE(DS)+IT+ME+CE) 1st SEM", "LH-233", "THU", 8, "BS-PH 101", "Physics-I", "BC(PH)")
        add_routine("(CSE(DS)+IT+ME+CE) 1st SEM", "LH-233", "THU", 9, "Basic Computing", "Basic Computing RB", "RB(IT)")

        add_routine("(CSE(DS)+IT+ME+CE) 1st SEM", "LH-233", "FRI", 7, "Soft Skill", "English Communication", "SC(ENG)")
        add_routine("(CSE(DS)+IT+ME+CE) 1st SEM", "LH-233", "FRI", 8, "BS-M 101", "Mathematics-I", "RG(M)")
        add_routine("(CSE(DS)+IT+ME+CE) 1st SEM", "LH-233", "FRI", 9, "BS-PH 101", "Physics-I", "BC(PH)")

        add_routine("(CSE(DS)+IT+ME+CE) 1st SEM", "LH-233", "SAT", 7, "ES-EE 191", "Electrical Workshop", "AS(EE)")
        add_routine("(CSE(DS)+IT+ME+CE) 1st SEM", "LH-233", "SAT", 8, "ES-EE 191", "Electrical Workshop", "AS(EE)")
        add_routine("(CSE(DS)+IT+ME+CE) 1st SEM", "LH-233", "SAT", 9, "ES-EE 191", "Electrical Workshop", "AS(EE)")

        # Seed Mess Menu
        MessTiming.objects.all().delete()
        
        t1_b = MessTiming.objects.create(meal_type='BREAKFAST', start_time=datetime.time(7, 45), end_time=datetime.time(8, 45))
        t1_b.academic_years.add(year_objs['1'], year_objs['2'])

        t1_l = MessTiming.objects.create(meal_type='LUNCH', start_time=datetime.time(12, 0), end_time=datetime.time(13, 0))
        t1_l.academic_years.add(year_objs['1'], year_objs['2'])

        t1_t = MessTiming.objects.create(meal_type='HI_TEA', start_time=datetime.time(17, 0), end_time=datetime.time(17, 30))
        t1_t.academic_years.add(year_objs['1'], year_objs['2'])

        t1_d = MessTiming.objects.create(meal_type='DINNER', start_time=datetime.time(20, 0), end_time=datetime.time(21, 0))
        t1_d.academic_years.add(year_objs['1'], year_objs['2'])

        t2_b = MessTiming.objects.create(meal_type='BREAKFAST', start_time=datetime.time(8, 45), end_time=datetime.time(9, 45))
        t2_b.academic_years.add(year_objs['3'], year_objs['4'])

        t2_l = MessTiming.objects.create(meal_type='LUNCH', start_time=datetime.time(13, 0), end_time=datetime.time(14, 0))
        t2_l.academic_years.add(year_objs['3'], year_objs['4'])

        t2_t = MessTiming.objects.create(meal_type='HI_TEA', start_time=datetime.time(17, 30), end_time=datetime.time(18, 0))
        t2_t.academic_years.add(year_objs['3'], year_objs['4'])

        t2_d = MessTiming.objects.create(meal_type='DINNER', start_time=datetime.time(21, 0), end_time=datetime.time(22, 0))
        t2_d.academic_years.add(year_objs['3'], year_objs['4'])

        mess_menu_data = [
            ('MON', 
             'IDLI + CHUTNEY + SAMBHAR + TEA',
             'JEERA RICE + ROTI + ARHAR DAL + SEASONAL SABJI + PAPAD',
             'SAMOSA (2PCS) + CHUTNEY + TEA',
             'PLAIN RICE + ROTI + MIXED DAL + SEASONAL SABJI + PAPAD'),
            ('TUE',
             'CHANA DAAL KACHURI + ALOO SABJI WITH GRAVY + TEA + BANANA',
             'PLAIN RICE + ROTI + CHANA DAL + SEASONAL SABJI + PAPAD + TOMATO CHATNI',
             'LITTI + CHOKHA + GREEN CHUTNEY + COFFEE FLAVOURED TEA',
             'VEG PULAO + ROTI + PANEER BUTTER MASALA + PAPAD'),
            ('WED',
             'BREAD BUTTER + ALOO TIKKI + TOMATO KETCHUP + TEA + BOILED EGG',
             'PLAIN RICE + ROTI + MIXED DAL + SEASONAL SABJI + SALAD',
             'KACHORI + AALOO SABJI + TEA',
             'PLAIN RICE + ROTI + KABULI CHANA PANEER SABJI + PAPAD'),
            ('THU',
             'SATHU PARATHA + ALOO SABJI WITH GRAVY + TEA + BANANA',
             'VEG BIRIYANI + ROTI + ARHAR DAAL + SEASONAL SABJI + RAITA',
             'CAKE + BISCUIT + TEA',
             'PLAIN RICE + DAL POORI + TARKA DAL + SEASONAL SABJI'),
            ('FRI',
             'ALOO PARATHA + SABJI WITH GRAVY + CURD + ACHAR + TEA',
             'PLAIN RICE + ROTI + CHANA DAL + SEASONAL SABJI + TOMATO CHATNI',
             'HAKKA NOODLES + LEMON TEA',
             'VEG PULAO + ROTI + CHANA DAL + SEASONAL VEGETABLE + PAPAD'),
            ('SAT',
             'KACHURI + ALOO CHANA DAAL SABJI + TEA + BANANA',
             'ARWA CHAWAL KHICHDI + MASALA CHOKHA + ACHAR + PAPAD',
             'JHAAL MURI + COFFEE',
             'RICE + ROTI + ARHAR DAL + SEASONAL SABJI + PAPAD'),
            ('SUN',
             'CHOLE BHATURE + TEA + LEMON + PYAZ + CHUTNEY + FRIED MIRCHI + SEASONAL FRUIT',
             'PLAIN RICE + ROTI + KADEE + SEASONAL VEGETABLE + PAPAD + TOMATO CHATNI',
             'VEGGIE MAGGI + TEA',
             'ROTI + VEG BIRYANI + CHILLI PANEER + PAPAD'),
        ]

        DailyMessMenu.objects.all().delete()
        for day_code, bf, ln, ht, dn in mess_menu_data:
            DailyMessMenu.objects.create(
                day_of_week=day_code,
                breakfast=bf,
                lunch=ln,
                hi_tea=ht,
                dinner=dn
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded database!"))
