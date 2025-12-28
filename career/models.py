from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class CustomUser(AbstractUser):
    """Custom User model with role-based access"""
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

    def save(self, *args, **kwargs):
        # Automatically set is_staff and is_superuser for admin role users
        if self.role == 'admin':
            self.is_staff = True
            self.is_superuser = True
        else:
            # For student role, ensure they don't have staff/superuser access
            # This handles both creation and role downgrades from admin to student
            self.is_staff = False
            self.is_superuser = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"


class StudentProfile(models.Model):
    """Student Profile with academic and professional details"""
    BRANCH_CHOICES = [
        ('CSE', 'Computer Science and Engineering'),
        ('ECE', 'Electronics and Communication Engineering'),
        ('EEE', 'Electrical and Electronics Engineering'),
        ('ME', 'Mechanical Engineering'),
        ('CE', 'Civil Engineering'),
        ('IT', 'Information Technology'),
        ('OTHER', 'Other'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    branch = models.CharField(max_length=10, choices=BRANCH_CHOICES)
    current_cgpa = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text="CGPA on a scale of 10"
    )
    backlogs = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of active backlogs"
    )
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    skills = models.TextField(blank=True, help_text="Comma-separated skills")
    linkedin_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.branch}"


class JobPost(models.Model):
    """Job posting by admin/T&P Cell"""
    company_name = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    package_lpa = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="Package in LPA (Lakhs Per Annum)"
    )
    min_cgpa_required = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text="Minimum CGPA required"
    )
    eligible_branches = models.CharField(
        max_length=500,
        help_text="Comma-separated branch codes (e.g., CSE,ECE,IT)"
    )
    deadline = models.DateTimeField()
    job_description = models.TextField()
    posted_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-posted_at']
    
    def __str__(self):
        return f"{self.company_name} - {self.role}"
    
    def get_eligible_branches_list(self):
        """Returns list of eligible branches"""
        return [branch.strip() for branch in self.eligible_branches.split(',')]
    
    def is_student_eligible(self, student_profile):
        """Check if a student is eligible for this job"""
        # Check CGPA
        if student_profile.current_cgpa < self.min_cgpa_required:
            return False
        
        # Check branch
        eligible_branches = self.get_eligible_branches_list()
        if student_profile.branch not in eligible_branches:
            return False
        
        return True


class Application(models.Model):
    """Student application for a job"""
    STATUS_CHOICES = [
        ('Applied', 'Applied'),
        ('Shortlisted', 'Shortlisted'),
        ('Rejected', 'Rejected'),
    ]
    
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Applied')
    applied_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'job']
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.job.company_name} ({self.status})"


class JobUpdate(models.Model):
    """Updates posted by T&P cell for a specific job"""
    job = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='updates')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Update for {self.job.role} - {self.created_at.date()}"


class CompanyWiki(models.Model):
    """Company interview experience and tips"""
    company_name = models.CharField(max_length=200)
    year = models.IntegerField(help_text="Year of interview")
    interview_questions = models.TextField(help_text="Interview questions asked")
    senior_tips = models.TextField(help_text="Tips from seniors")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-year', '-created_at']
    
    def __str__(self):
        return f"{self.company_name} - {self.year}"


class UserPreference(models.Model):
    """User preferences for theme and notifications"""
    THEME_CHOICES = [
        ('light', 'Light Mode'),
        ('dark', 'Dark Mode'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='preferences')
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    receive_emails = models.BooleanField(default=True, help_text="Receive email notifications for new jobs and updates")
    
    def __str__(self):
        return f"{self.user.username}'s Preferences"
