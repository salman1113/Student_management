from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import send_mail
from .models import CustomUser, StudentProfile, Enrollment

@receiver(post_save, sender=CustomUser)
def create_student_profile_and_welcome(sender, instance, created, **kwargs):
    if created and instance.role == "student":

        profile, _ = StudentProfile.objects.get_or_create(
            user=instance,
            defaults={
                "roll_number": f"S{instance.id:04d}",   # FIXED
            }
        )

        if instance.email:
            subject = "Welcome to Student Management"
            message = (
                f"Hi {instance.username},\n\n"
                f"Your student account has been created.\n"
                f"Your roll number is: {profile.roll_number}\n\n"
                f"Regards,\nStudent Management"
            )
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.email],
                fail_silently=True,
            )

@receiver(post_save, sender=Enrollment)
def notify_enrollment(sender, instance, created, **kwargs):
    if created:
        student_user = instance.student.user

        if student_user.email:
            subject = f"Course Assigned: {instance.course.title}"
            message = (
                f"Hi {student_user.username},\n\n"
                f"You have been enrolled in the course:\n"
                f" - {instance.course.title}\n\n"
                "Regards,\nStudent Management"
            )
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [student_user.email],
                fail_silently=True,
            )
