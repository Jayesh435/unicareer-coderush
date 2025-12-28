from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, StudentProfile, JobPost, Application, CompanyWiki


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role', {'fields': ('role',)}),
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'branch', 'current_cgpa', 'backlogs']
    list_filter = ['branch']
    search_fields = ['user__username', 'user__email']


@admin.register(JobPost)
class JobPostAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'role', 'package_lpa', 'min_cgpa_required', 'deadline', 'is_active']
    list_filter = ['is_active', 'posted_at']
    search_fields = ['company_name', 'role']
    date_hierarchy = 'posted_at'


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['student', 'job', 'status', 'applied_at']
    list_filter = ['status', 'applied_at']
    search_fields = ['student__username', 'job__company_name']
    date_hierarchy = 'applied_at'


@admin.register(CompanyWiki)
class CompanyWikiAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'year', 'created_at']
    list_filter = ['year']
    search_fields = ['company_name']
    date_hierarchy = 'created_at'
