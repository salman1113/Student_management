from django.contrib.auth.decorators import user_passes_test

def is_admin(user):
    return user.is_authenticated and (getattr(user, "role", None) == "admin" or user.is_staff or user.is_superuser)

def is_student(user):
    return user.is_authenticated and getattr(user, "role", None) == "student"

def admin_required(view_func):
    return user_passes_test(is_admin, login_url='login')(view_func)

def student_required(view_func):
    return user_passes_test(is_student, login_url='login')(view_func)
