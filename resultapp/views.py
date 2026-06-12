from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import (
    Class,
    Student,
    Subject,
    SubjectCombination,
    Result,
    Notice
)
from .forms import NoticeForm


# -------------------------
# Home & Auth
# -------------------------

# resultapp/views.py
from django.shortcuts import render
from .models import Result

def index(request):
    # show latest 10 results on homepage
    results = Result.objects.select_related("student", "subject").order_by("-id")[:10]
    context = {"results": results}
    return render(request, "resultapp/index.html", context)

def home(request):
    # fetch a few latest results for marquee
    results = Result.objects.select_related('student', 'subject').order_by('-id')[:10]        
    notices = Notice.objects.order_by('-publish_date')[:5]  # latest 5 notices

    return render(request, 'index.html', {'results': results,'notices':notices})

def notice_list(request):
    notices = Notice.objects.filter(
        expiry_date__gte=timezone.now()
    ) | Notice.objects.filter(expiry_date__isnull=True)

    return render(
        request,
        "notices/notice_list.html",
        {"notices": notices.order_by("-publish_date")}
    )


def admin_login(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')
    error = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            error = "Invalid credentials or not authorized."
    return render(request, 'resultapp/admin_login.html', {"error": error})


def admin_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('admin-login')
    return render(request, 'admin_dashboard.html')


def admin_logout(request):
    logout(request)
    return redirect('admin-login')


# -------------------------
# Classes
# -------------------------
@login_required
def create_class(request):
    if request.method == 'POST':
        try:
            Class.objects.create(
                class_name=request.POST.get('class_name'),
                department=request.POST.get('department'),
                year=request.POST.get('year'),
                semester=request.POST.get('semester'),
                section=request.POST.get('section'),
                academic_session=request.POST.get('academic_session'),
                remarks=request.POST.get('remarks'),
            )
            messages.success(request, "Class created successfully.")
            return redirect('create_class')
        except Exception as e:
            messages.error(request, f"Something went wrong: {str(e)}")
            return redirect('create_class')
    return render(request, 'create_class.html')


@login_required
def manage_classes(request):
    classes = Class.objects.all()
    departments = Class.objects.values_list("department", flat=True).distinct().order_by("department")

    delete_id = request.GET.get('delete')
    if delete_id:
        try:
            class_obj = get_object_or_404(Class, id=delete_id)
            class_obj.delete()
            messages.success(request, "Class deleted successfully")
            return redirect('manage_classes')
        except Exception as e:
            messages.error(request, f"Something went wrong: {str(e)}")
            return redirect('manage_classes')

    return render(request, 'manage_classes.html', {
        "classes": classes,
        "departments": departments,
    })


@login_required
def edit_class(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    if request.method == 'POST':
        try:
            class_obj.class_name = request.POST.get('class_name')
            class_obj.department = request.POST.get('department')
            class_obj.year = request.POST.get('year')
            class_obj.semester = request.POST.get('semester')
            class_obj.section = request.POST.get('section')
            class_obj.academic_session = request.POST.get('academic_session')
            class_obj.remarks = request.POST.get('remarks')
            class_obj.save()
            messages.success(request, "Class updated successfully.")
            return redirect('manage_classes')
        except Exception as e:
            messages.error(request, f"Something went wrong: {str(e)}")
            return redirect('edit_class', class_id=class_obj.id)
    return render(request, 'edit_class.html', {"class_obj": class_obj})


# -------------------------
# Subjects
# -------------------------
@login_required
def create_subject(request):
    classes = Class.objects.all()
    if request.method == "POST":
        subject_code = request.POST.get("subject_code")
        subject_name = request.POST.get("subject_name")
        subject_type = request.POST.get("subject_type")
        credits = request.POST.get("credits")
        assigned_class = request.POST.get("assigned_class")

        if subject_code and subject_name and subject_type and credits and assigned_class:
            Subject.objects.create(
                subject_code=subject_code,
                subject_name=subject_name,
                subject_type=subject_type,
                credits=credits,
                assigned_class_id=assigned_class,
            )
            messages.success(request, "Subject created successfully!")
            return redirect('manage_subjects')
        else:
            messages.error(request, "Please fill all required fields!")

    return render(request, 'create_subject.html', {"classes": classes})


@login_required
def manage_subjects(request):
    subjects = Subject.objects.select_related('assigned_class').all()
    departments = Class.objects.values_list('department', flat=True).distinct()

    subjects_by_department = {}
    for subject in subjects:
        dept = subject.assigned_class.department
        subjects_by_department.setdefault(dept, []).append(subject)

    return render(request, 'manage_subjects.html', {
        "subjects": subjects,
        "departments": departments,
        "subjects_by_department": subjects_by_department,
    })


@login_required
def edit_subject(request, subject_id):
    subject_obj = get_object_or_404(Subject, id=subject_id)
    classes = Class.objects.all()
    if request.method == 'POST':
        try:
            subject_obj.subject_name = request.POST.get('subject_name')
            subject_obj.subject_code = request.POST.get('subject_code')
            subject_obj.subject_type = request.POST.get('subject_type')
            subject_obj.credits = request.POST.get('credits')
            assigned_class_id = request.POST.get('assigned_class')
            if assigned_class_id:
                subject_obj.assigned_class = get_object_or_404(Class, id=assigned_class_id)
            subject_obj.save()
            messages.success(request, "Subject updated successfully.")
            return redirect('manage_subjects')
        except Exception as e:
            messages.error(request, f"Something went wrong: {str(e)}")
            return redirect('manage_subjects')
    return render(request, 'edit_subject.html', {"subject": subject_obj, "classes": classes})


@login_required
def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    subject.delete()
    messages.success(request, "Subject deleted successfully!")
    return redirect('manage_subjects')


# -------------------------
# Subject Combinations
# -------------------------
@login_required
def add_subject_combination(request):
    classes = Class.objects.all()
    subjects = Subject.objects.all()
    departments = Class.objects.values_list("department", flat=True).distinct()

    if request.method == "POST":
        student_class_id = request.POST.get("student_class")
        selected_subject_ids = request.POST.getlist("subjects")
        try:
            student_class = Class.objects.get(id=student_class_id)
            combination = SubjectCombination.objects.create(student_class=student_class)
            combination.subjects.set(selected_subject_ids)
            combination.save()
            messages.success(request, "Subject combination added successfully.")
            return redirect("manage_subject_combinations")
        except Exception as e:
            messages.error(request, f"Something went wrong: {str(e)}")

    return render(request, "add_subject_combination.html", {
        "classes": classes,
        "subjects": subjects,
        "departments": departments,
    })


@login_required
def manage_subject_combinations(request):
    combinations = SubjectCombination.objects.select_related(
        "student_class"
    ).prefetch_related("subjects").all()

    departments = Class.objects.values_list('department', flat=True).distinct()

    delete_id = request.GET.get("delete")
    if delete_id:
        combo = get_object_or_404(SubjectCombination, id=delete_id)
        combo.delete()
        messages.success(request, "Subject Combination deleted successfully.")
        return redirect("manage_subject_combinations")

    return render(request, "manage_subject_combinations.html", {
        "combinations": combinations,
        "departments": departments
    })


@login_required
def edit_subject_combination(request, combo_id):
    combo = get_object_or_404(SubjectCombination, id=combo_id)
    classes = Class.objects.all()
    subjects = Subject.objects.all()

    if request.method == "POST":
        student_class_id = request.POST.get("student_class")
        subject_ids = request.POST.getlist("subjects")

        if not student_class_id or not subject_ids:
            messages.error(request, "Please select both class and subjects.")
            return redirect("edit_subject_combination", combo_id=combo.id)

        try:
            combo.student_class = Class.objects.get(id=student_class_id)
            combo.subjects.set(subject_ids)
            combo.save()
            messages.success(request, "Subject Combination updated successfully!")
            return redirect("manage_subject_combinations")
        except Exception as e:
            messages.error(request, f"Something went wrong: {str(e)}")
            return redirect("edit_subject_combination", combo_id=combo.id)

    return render(request, "edit_subject_combination.html", {
        "combo": combo,
        "classes": classes,
        "subjects": subjects
    })


@login_required
def delete_subject_combination(request, id):
    combination = get_object_or_404(SubjectCombination, id=id)
    combination.delete()
    messages.success(request, "Subject Combination deleted successfully.")
    return redirect('manage_subject_combinations')


# -------------------------
# Students
# -------------------------
@login_required
def add_student(request):
    classes = Class.objects.all()
    if request.method == "POST":
        roll_number = request.POST.get("roll_number")
        full_name = request.POST.get("full_name")
        gender = request.POST.get("gender")
        date_of_birth = request.POST.get("date_of_birth")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        student_class_id = request.POST.get("student_class")
        admission_year = request.POST.get("admission_year")
        profile_picture = request.FILES.get("profile_picture")

        if Student.objects.filter(roll_number=roll_number).exists():
            messages.error(request, "Roll number already exists!")
            return redirect("add_student")
        if Student.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect("add_student")

        try:
            student_class = Class.objects.get(id=student_class_id)
            Student.objects.create(
                roll_number=roll_number,
                full_name=full_name,
                gender=gender,
                date_of_birth=date_of_birth,
                email=email,
                phone=phone,
                address=address,
                student_class=student_class,
                admission_year=admission_year,
                profile_picture=profile_picture,
            )
            messages.success(request, f"Student {full_name} added successfully!")
            return redirect("manage_students")
        except Class.DoesNotExist:
            messages.error(request, "Selected class does not exist!")

    return render(request, "student/add_student.html", {"classes": classes})


@login_required
def manage_students(request):
    students = Student.objects.all().order_by('-id')
    return render(request, "student/manage_students.html", {"students": students})


@login_required
def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    classes = Class.objects.all()
    if request.method == "POST":
        try:
            student.roll_number = request.POST.get("roll_number")
            student.full_name = request.POST.get("full_name")
            student.gender = request.POST.get("gender")
            student.date_of_birth = request.POST.get("date_of_birth")
            student.email = request.POST.get("email")
            student.phone = request.POST.get("phone")
            student.address = request.POST.get("address")
            student_class_id = request.POST.get("student_class")
            student.admission_year = request.POST.get("admission_year")
            profile_picture = request.FILES.get("profile_picture")

            if student_class_id:
                student.student_class = Class.objects.get(id=student_class_id)
            if profile_picture:
                student.profile_picture = profile_picture

            student.save()
            messages.success(request, f"Student {student.full_name} updated successfully!")
            return redirect("manage_students")
        except Exception as e:
            messages.error(request, f"Something went wrong: {str(e)}")
            return redirect("edit_student", student_id=student.id)

    return render(request, "student/edit_student.html", {"student": student, "classes": classes})


# -------------------------
# Results
# -------------------------
@login_required
def add_result(request):
    departments = Class.objects.values_list("department", flat=True).distinct()
    selected_department = request.GET.get("department")
    selected_class_id = request.GET.get("class")

    classes = Class.objects.all()
    if selected_department:
        classes = classes.filter(department=selected_department)

    students = Student.objects.all()
    if selected_class_id:
        students = students.filter(student_class_id=selected_class_id)

    subject = Subject.objects.all()
    if selected_class_id:
        subject = subject.filter(assigned_class_id=selected_class_id)

    combinations = SubjectCombination.objects.all()
    if selected_class_id:
        combinations = combinations.filter(student_class_id=selected_class_id)

    if request.method == "POST":
        try:
            student = Student.objects.get(id=request.POST.get("student"))
            subject = Subject.objects.get(id=request.POST.get("subject"))
            combination = SubjectCombination.objects.get(id=request.POST.get("combination"))
            semester = request.POST.get("semester")

            internal_marks = Decimal(request.POST.get("internal_marks") or 0)
            external_marks = Decimal(request.POST.get("external_marks") or 0)
            remarks = request.POST.get("remarks", "")
            Result.objects.create(
                student=student,
                subject=subject,
                subject_combination=combination,
                semester=int(semester),
                internal_marks=internal_marks,
                external_marks=external_marks,
                remarks=remarks
            )
            messages.success(request, f"Result added successfully for {student.full_name}.")
            return redirect('add_result')
        except Exception as e:
            messages.error(request, f"Something went wrong: {str(e)}")

    return render(request, "results/add_result.html", {
        "departments": departments,
        "classes": classes,
        "students": students,
        "subject": subject,
        "combinations": combinations,
        "selected_department": selected_department,
        "selected_class_id": selected_class_id
    })


@login_required
def manage_results(request):
    results = Result.objects.select_related("student", "subject", "subject_combination").all().order_by('-id')

    # Filters
    selected_department = request.GET.get('department')
    selected_semester = request.GET.get('semester')
    selected_subject = request.GET.get('subject')

    if selected_department:
        results = results.filter(student__student_class__department=selected_department)
    if selected_semester:
        results = results.filter(semester=selected_semester)
    if selected_subject:
        results = results.filter(subject_id=selected_subject)

    delete_id = request.GET.get("delete")
    if delete_id:
        try:
            result_obj = get_object_or_404(Result, id=delete_id)
            result_obj.delete()
            messages.success(request, "Result deleted successfully.")
            return redirect('manage_results')
        except Exception as e:
            messages.error(request, f"Something went wrong: {str(e)}")
            return redirect('manage_results')

    # Pass departments, subjects, semesters to template
    departments = Class.objects.values_list('department', flat=True).distinct()
    subject = Subject.objects.all()
    semesters = Result.SEMESTER_CHOICES

    context = {
        "results": results,
        "departments": departments,
        "subject": subject,
        "semesters": semesters,
        "selected_department": selected_department,
        "selected_semester": selected_semester,
        "selected_subject": selected_subject,
    }
    return render(request, "results/manage_results.html", context)




@login_required
def edit_result(request, result_id):
    result = get_object_or_404(Result, id=result_id)
    students = Student.objects.all()
    subject = Subject.objects.all()
    combinations = SubjectCombination.objects.all()

    if request.method == "POST":
        try:
            result.student = Student.objects.get(id=request.POST.get("student"))
            result.subject = Subject.objects.get(id=request.POST.get("subject"))
            result.subject_combination = SubjectCombination.objects.get(id=request.POST.get("combination"))
            result.semester = request.POST.get("semester")

            result.internal_marks = Decimal(request.POST.get("internal_marks") or 0)
            result.external_marks = Decimal(request.POST.get("external_marks") or 0)
            result.remarks = request.POST.get("remarks", "")

            result.save()
            messages.success(request, f"Result updated successfully for {result.student.full_name}.")
            return redirect('manage_results')
        except Exception as e:
            messages.error(request, f"Something went wrong: {str(e)}")

    return render(request, "results/edit_result.html", {
        "result": result,
        "students": students,
        "subject": subject,
        "combinations": combinations
    })


@login_required
def delete_result(request, result_id):
    result = get_object_or_404(Result, id=result_id)
    if request.method == "POST":
        result.delete()
        messages.success(request, "Result deleted successfully.")
        return redirect('manage_results')
    return render(request, "results/delete_result_confirm.html", {"result": result})


# -------------------------
# Notices
# -------------------------
@login_required
def add_notice(request):
    if request.method == "POST":
        form = NoticeForm(request.POST, request.FILES)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.author = request.user
            notice.save()
            messages.success(request, "Notice created successfully!")
            return redirect('manage_notices')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = NoticeForm()
    return render(request, 'notices/add_notice.html', {"form": form})


@login_required
def manage_notices(request):
    notices = Notice.objects.all()
    dept_filter = request.GET.get('department')
    class_filter = request.GET.get('class')
    if dept_filter:
        notices = notices.filter(department=dept_filter)
    if class_filter:
        notices = notices.filter(target_class__id=class_filter)

    delete_id = request.GET.get("delete")
    if delete_id:
        notice = get_object_or_404(Notice, id=delete_id)
        notice.delete()
        messages.success(request, "Notice deleted successfully!")
        return redirect('manage_notices')

    classes = Class.objects.all()
    return render(request, 'notices/manage_notices.html', {"notices": notices, "classes": classes})


@login_required
def edit_notice(request, notice_id):
    notice = get_object_or_404(Notice, id=notice_id)
    if request.method == "POST":
        form = NoticeForm(request.POST, request.FILES, instance=notice)
        if form.is_valid():
            form.save()
            messages.success(request, "Notice updated successfully!")
            return redirect('manage_notices')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = NoticeForm(instance=notice)
    return render(request, 'notices/edit_notice.html', {"form": form, "notice": notice})


def notice_detail(request, notice_id):
    notice = get_object_or_404(Notice, id=notice_id)
    return render(request, "notices/notice_detail.html", {"notice": notice})


def get_global_notices(request):
    notices = Notice.objects.filter(
        expiry_date__gte=timezone.now()
    ) | Notice.objects.filter(expiry_date__isnull=True)

    return {'notices': notices.order_by('-priority', '-publish_date')}
# resultapp/views.py


from django.shortcuts import render
from .models import Student, Result, Class

def student_results(request):
    results = []
    student = None
    grand_total = 0
    overall_status = "Pass"

    # Get all options for dropdowns
    departments = Class.objects.values_list('department', flat=True).distinct()
    years = Class.objects.values_list('year', flat=True).distinct()
    semesters = Result.SEMESTER_CHOICES

    # Get filter values from GET or POST
    selected_department = request.GET.get("department") or request.POST.get("department")
    selected_year = request.GET.get("year") or request.POST.get("year")
    selected_semester = request.GET.get("semester") or request.POST.get("semester")

    # Filter students based on department/year/semester
    students_queryset = Student.objects.select_related('student_class').all()
    if selected_department:
        students_queryset = students_queryset.filter(student_class__department=selected_department)
    if selected_year:
        students_queryset = students_queryset.filter(student_class__year=selected_year)

    # If roll number is provided, filter student
    roll_number = request.POST.get("roll_number")
    if roll_number:
        student = students_queryset.filter(roll_number=roll_number).first()
        if student:
            results = Result.objects.filter(student=student)
            if selected_semester:
                results = results.filter(semester=int(selected_semester))  # convert to int

            grand_total = sum(r.internal_marks + r.external_marks for r in results)
            for r in results:
                if r.status == "Fail":
                    overall_status = "Fail"
                    break

    context = {
        "student": student,
        "results": results,
        "grand_total": grand_total,
        "overall_status": overall_status,
        "departments": departments,
        "years": years,
        "semesters": semesters,
        "selected_department": selected_department,
        "selected_year": selected_year,
        "selected_semester": selected_semester,
        "students": students_queryset,  # optional: to show filtered student list
    }

    return render(request, "student_results.html", context)
