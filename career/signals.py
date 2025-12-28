from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Application, JobPost, StudentProfile, CustomUser, UserPreference

@receiver(post_save, sender=Application)
def send_application_email(sender, instance, created, **kwargs):
    """
    Signal to send email when an application is created or updated.
    """
    student = instance.student
    job = instance.job
    
    # Check if user wants to receive emails
    if hasattr(student, 'preferences') and not student.preferences.receive_emails:
        return
    
    if created:
        # Case 1: Student applies for a job (Confirmation)
        subject = f'Application Received: {job.role} at {job.company_name}'
        message = f"""
        Dear {student.username},

        We have received your application for the position of {job.role} at {job.company_name}.
        
        Current Status: {instance.status}
        
        We will notify you of any updates.

        Best regards,
        UniCareer Team
        """
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [student.email],
            fail_silently=False,
        )
    else:
        # Case 2: Admin updates an application status
        # We assume any update to an existing application is a status change for now
        # Ideally we would check if the status field actually changed
        subject = f'Application Update: {job.role} at {job.company_name}'
        message = f"""
        Dear {student.username},

        There has been an update to your application for the position of {job.role} at {job.company_name}.

        New Status: {instance.status}

        Please login to your dashboard for more details.

        Best regards,
        UniCareer Team
        """
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [student.email],
            fail_silently=False,
        )

@receiver(post_save, sender=JobPost)
def send_new_job_notification(sender, instance, created, **kwargs):
    """
    Signal to send email to eligible students when a new job is posted.
    """
    if created and instance.is_active:
        # Case 3: A new job is posted
        # Find eligible students
        eligible_emails = []
        profiles = StudentProfile.objects.select_related('user').all()
        
        for profile in profiles:
            # Check preferences
            if hasattr(profile.user, 'preferences') and not profile.user.preferences.receive_emails:
                continue

            if instance.is_student_eligible(profile):
                if profile.user.email:
                    eligible_emails.append(profile.user.email)
        
        if eligible_emails:
            subject = f'New Job Alert: {instance.role} at {instance.company_name}'
            message = f"""
            Hello,

            A new job opening matching your profile has been posted on UniCareer.

            Company: {instance.company_name}
            Role: {instance.role}
            Package: {instance.package_lpa} LPA
            Deadline: {instance.deadline.strftime('%Y-%m-%d')}

            Login to UniCareer to apply now!

            Best regards,
            UniCareer Team
            """
            
            # Send individual emails to protect privacy (or use bcc)
            # For simplicity in this demo, we loop. For production, use send_mass_mail or BCC.
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                eligible_emails,
                fail_silently=False,
            )


@receiver(post_save, sender=CustomUser)
def create_user_preferences(sender, instance, created, **kwargs):
    """Create UserPreference when a new User is created"""
    if created:
        UserPreference.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_preferences(sender, instance, **kwargs):
    """Save UserPreference when User is saved"""
    if hasattr(instance, 'preferences'):
        instance.preferences.save()
