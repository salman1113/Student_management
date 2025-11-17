from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count

from .decorators import admin_required, student_required
from .models import StudentProfile, CustomUser, Course, Enrollment
from .forms import (
    CustomUserRegisterForm,
    StudentProfileAdminForm,
    AdminCreateStudentUserForm,
    StudentProfileForm,
    UserUpdateForm,
    CourseForm,
    EnrollmentForm,
    CustomLoginForm
)

from .utils import generate_roll_number


def home(request):
    return render(request, 'home.html')


def register(request):
    if request.method == "POST":
        form = CustomUserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            profile, created = StudentProfile.objects.get_or_create(user=user)

            if created:
                profile.roll_number = generate_roll_number()
                profile.save()

            messages.success(request, "Account created successfully. Please log in.")
            return redirect("login")
    else:
        form = CustomUserRegisterForm()

    return render(request, "register.html", {"form": form})


@login_required
@admin_required
def admin_dashboard(request):
    student_count = CustomUser.objects.filter(role="student").count()
    course_count = Course.objects.count()
    enrollment_count = Enrollment.objects.count()

    recent_students = StudentProfile.objects.select_related('user').order_by('-id')[:6]

    students_by_dept_qs = (
        StudentProfile.objects
        .exclude(department__isnull=True)
        .exclude(department="")
        .values('department')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    departments = [row['department'] for row in students_by_dept_qs]
    students_by_dept = [row['count'] for row in students_by_dept_qs]

    enrollments_by_course_qs = (
        Enrollment.objects.values('course__title')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    course_titles = [row['course__title'] for row in enrollments_by_course_qs]
    enrollments_counts = [row['count'] for row in enrollments_by_course_qs]

    return render(request, 'dashboards/admin_dashboard.html', {
        'student_count': student_count,
        'course_count': course_count,
        'enrollment_count': enrollment_count,
        'recent_students': recent_students,
        'departments': departments,
        'students_by_dept': students_by_dept,
        'course_titles': course_titles,
        'enrollments_counts': enrollments_counts,
    })



@login_required
@admin_required
def student_list(request):
    search = request.GET.get("q", "")

    students = StudentProfile.objects.select_related("user").filter(user__role="student")

    if search:
        students = students.filter(
            Q(user__username__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(roll_number__icontains=search) |
            Q(department__icontains=search)
        )

    paginator = Paginator(students.order_by("roll_number"), 10)
    page = request.GET.get("page")
    students_page = paginator.get_page(page)

    return render(request, "students/student_list.html", {
        "students": students_page,
        "search": search,
    })


@login_required
@admin_required
def student_create(request):
    if request.method == "POST":
        user_form = AdminCreateStudentUserForm(request.POST)
        profile_form = StudentProfileAdminForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.role = "student"
            user.set_password("student123")
            user.save()

            profile, created = StudentProfile.objects.get_or_create(user=user)

            if created:
                profile.roll_number = generate_roll_number()

            profile_form = StudentProfileAdminForm(request.POST, request.FILES, instance=profile)
            profile_form.save()

            messages.success(request, "Student added successfully.")
            return redirect("student_list")

    else:
        user_form = AdminCreateStudentUserForm()
        profile_form = StudentProfileAdminForm()

    return render(request, "students/student_create.html", {
        "user_form": user_form,
        "profile_form": profile_form,
    })


@login_required
@admin_required
def student_edit(request, pk):
    profile = get_object_or_404(StudentProfile, pk=pk)
    user = profile.user

    if request.method == "POST":
        user_form = AdminCreateStudentUserForm(request.POST, instance=user)
        profile_form = StudentProfileAdminForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            messages.success(request, "Student updated.")
            return redirect("student_list")

    else:
        user_form = AdminCreateStudentUserForm(instance=user)
        profile_form = StudentProfileAdminForm(instance=profile)

    return render(request, "students/student_edit.html", {
        "user_form": user_form,
        "profile_form": profile_form,
        "profile": profile,
    })


@login_required
@admin_required
def student_delete(request, pk):
    profile = get_object_or_404(StudentProfile, pk=pk)
    user = profile.user

    if request.method == "POST":
        user.delete()
        messages.success(request, "Student deleted.")
        return redirect("student_list")

    return render(request, "students/student_delete_confirm.html", {"profile": profile})


@login_required
@admin_required
def student_detail(request, pk):
    profile = get_object_or_404(StudentProfile, pk=pk)
    return render(request, "students/student_detail.html", {"profile": profile})


@login_required
@student_required
def student_dashboard(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    enrollments = Enrollment.objects.filter(student=profile).select_related('course')

    return render(request, 'dashboards/student_dashboard.html', {
        'profile': profile,
        'enrollments': enrollments,
    })


@login_required
@student_required
def edit_my_profile(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = StudentProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('student_dashboard')

        messages.error(request, "Please correct the errors below.")

    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = StudentProfileForm(instance=profile)

    return render(request, 'students/student_profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile,
    })


@login_required
@admin_required
def course_list(request):
    q = request.GET.get('q', '')
    qs = Course.objects.all()

    if q:
        qs = qs.filter(title__icontains=q)

    paginator = Paginator(qs.order_by('-id'), 10)
    page = request.GET.get('page')
    courses = paginator.get_page(page)

    return render(request, 'courses/course_list.html', {'courses': courses, 'q': q})


@login_required
@admin_required
def course_create(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Course created successfully.")
            return redirect('course_list')
    else:
        form = CourseForm()

    return render(request, 'courses/course_form.html', {'form': form, 'title': 'Add Course'})


@login_required
@admin_required
def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully.")
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)

    return render(request, 'courses/course_form.html', {'form': form, 'title': 'Edit Course'})


@login_required
@admin_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.method == "POST__":
        course.delete()
        messages.success(request, "Course deleted successfully.")
        return redirect('course_list')

    return render(request, 'courses/course_delete_confirm.html', {'course': course})


@login_required
@admin_required
def enrollment_list(request):
    q = request.GET.get('q', '')
    qs = Enrollment.objects.select_related('student__user', 'course').order_by('-id')

    if q:
        qs = qs.filter(
            Q(student__user__username__icontains=q) |
            Q(course__title__icontains=q)
        )

    paginator = Paginator(qs, 10)
    page = request.GET.get("page")
    enrollments = paginator.get_page(page)

    return render(request, "enrollments/enrollment_list.html", {
        "enrollments": enrollments,
        "q": q
    })


@login_required
@admin_required
def enrollment_create(request):
    if request.method == "POST":
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Course assigned successfully.")
            except:
                messages.error(request, "This student is already enrolled in this course.")
            return redirect("enrollment_list")
    else:
        form = EnrollmentForm()

    return render(request, "enrollments/enrollment_form.html", {
        "form": form,
        "title": "Assign Course"
    })


@login_required
@admin_required
def enrollment_delete(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)

    if request.method == "POST":
        enrollment.delete()
        messages.success(request, "Enrollment removed.")
        return redirect("enrollment_list")

    return render(request, "enrollments/enrollment_delete_confirm.html", {"enrollment": enrollment})


@login_required
@student_required
def mark_course_complete(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk, student__user=request.user)

    enrollment.completed = True
    enrollment.progress = 100
    enrollment.save()

    messages.success(request, f"You completed {enrollment.course.title}!")
    return redirect("student_dashboard")


def login_view(request):
    if request.method == "POST":
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if user.is_superuser or user.role == "admin":
                return redirect("admin_dashboard")
            return redirect("student_dashboard")
    else:
        form = CustomLoginForm()

    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")
