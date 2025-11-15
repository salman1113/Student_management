from .models import StudentProfile

def generate_roll_number():
    last = StudentProfile.objects.order_by('-id').first()
    if not last or not last.roll_number:
        return "S0001"

    last_num = int(last.roll_number.replace("S", ""))
    new_num = last_num + 1
    return f"S{new_num:04d}"
