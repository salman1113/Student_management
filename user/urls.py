from django.urls import path
from .views import (
    home, register, login_view, logout_view,
    admin_dashboard, student_dashboard,
    student_list, student_create, student_edit, student_delete, student_detail,
    edit_my_profile,
    course_list, course_create, course_edit, course_delete,
    enrollment_list, enrollment_create, enrollment_delete, mark_course_complete
)

urlpatterns = [
    path("", home, name="home"),

    # Authentication
    path("register/", register, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    # Admin
    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),

    # Student
    path("student-dashboard/", student_dashboard, name="student_dashboard"),
    path("edit-my-profile/", edit_my_profile, name="edit_my_profile"),

    # Student CRUD
    path("students/", student_list, name="student_list"),
    path("students/add/", student_create, name="student_create"),
    path("students/<int:pk>/edit/", student_edit, name="student_edit"),
    path("students/<int:pk>/delete/", student_delete, name="student_delete"),
    path("students/<int:pk>/", student_detail, name="student_detail"),

    # Courses
    path("courses/", course_list, name="course_list"),
    path("courses/create/", course_create, name="course_create"),
    path("courses/<int:pk>/edit/", course_edit, name="course_edit"),
    path("courses/<int:pk>/delete/", course_delete, name="course_delete"),

    # Enrollments
    path("enrollments/", enrollment_list, name="enrollment_list"),
    path("enrollments/create/", enrollment_create, name="enrollment_create"),
    path("enrollments/<int:pk>/delete/", enrollment_delete, name="enrollment_delete"),

    # Student Progress
    path("enrollment/<int:pk>/complete/", mark_course_complete, name="mark_course_complete"),
]
