from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    
    # Admin - Job Management
    path('job/create/', views.create_job, name='create_job'),
    path('job/<int:job_id>/edit/', views.edit_job, name='edit_job'),
    path('job/<int:job_id>/delete/', views.delete_job, name='delete_job'),
    path('job/<int:job_id>/applicants/', views.job_applicants, name='job_applicants'),
    path('job/<int:job_id>/export-csv/', views.export_applicants_csv, name='export_applicants_csv'),
    path('job/<int:job_id>/add-update/', views.add_job_update, name='add_job_update'),
    path('application/<int:application_id>/update-status/', views.update_application_status, name='update_application_status'),
    
    # Student
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('job/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('ats-scanner/', views.ats_scanner, name='ats_scanner'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('preferences/', views.preferences_view, name='preferences'),
    
    # Common
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    
    # Company Wiki
    path('company-wiki/', views.company_wiki_list, name='company_wiki_list'),
    path('company-wiki/<int:wiki_id>/', views.company_wiki_detail, name='company_wiki_detail'),
    path('company-wiki/create/', views.create_company_wiki, name='create_company_wiki'),
]
