from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
import csv
import io
import json
from pypdf import PdfReader
import google.generativeai as genai
from django.conf import settings

from .models import CustomUser, StudentProfile, JobPost, Application, CompanyWiki, JobUpdate, UserPreference
from .forms import (StudentRegistrationForm, StudentProfileForm, JobPostForm, 
                    ApplicationStatusForm, CompanyWikiForm, ResumeUploadForm, JobUpdateForm, UserPreferenceForm)
from .decorators import admin_required, student_required
from django.core.mail import send_mail


def home(request):
    """Home page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'career/home.html')


def login_view(request):
    """Login view for both admin and student"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'career/login.html')


def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


def register_view(request):
    """Student registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        user_form = StudentRegistrationForm(request.POST)
        profile_form = StudentProfileForm(request.POST, request.FILES)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
    else:
        user_form = StudentRegistrationForm()
        profile_form = StudentProfileForm()
    
    return render(request, 'career/register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required
def dashboard(request):
    """Dashboard - redirects based on user role"""
    if request.user.role == 'admin':
        return redirect('admin_dashboard')
    else:
        return redirect('student_dashboard')


@admin_required
def admin_dashboard(request):
    """Admin dashboard view"""
    jobs = JobPost.objects.all()
    total_jobs = jobs.count()
    active_jobs = jobs.filter(is_active=True).count()
    total_applications = Application.objects.count()
    
    context = {
        'jobs': jobs[:10],  # Show latest 10 jobs
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applications': total_applications,
    }
    return render(request, 'career/admin_dashboard.html', context)


@admin_required
def create_job(request):
    """Create new job post"""
    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('admin_dashboard')
    else:
        form = JobPostForm()
    
    return render(request, 'career/create_job.html', {'form': form})


@admin_required
def edit_job(request, job_id):
    """Edit existing job post"""
    job = get_object_or_404(JobPost, id=job_id)
    
    if request.method == 'POST':
        form = JobPostForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully!')
            return redirect('admin_dashboard')
    else:
        form = JobPostForm(instance=job)
    
    return render(request, 'career/edit_job.html', {'form': form, 'job': job})


@admin_required
def delete_job(request, job_id):
    """Delete job post"""
    job = get_object_or_404(JobPost, id=job_id)
    
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job deleted successfully!')
        return redirect('admin_dashboard')
    
    return render(request, 'career/delete_job.html', {'job': job})


@admin_required
def job_applicants(request, job_id):
    """View all applicants for a specific job"""
    job = get_object_or_404(JobPost, id=job_id)
    applications = Application.objects.filter(job=job).select_related('student', 'student__profile')
    
    context = {
        'job': job,
        'applications': applications,
    }
    return render(request, 'career/job_applicants.html', context)


@admin_required
def export_applicants_csv(request, job_id):
    """Export applicants data to CSV"""
    job = get_object_or_404(JobPost, id=job_id)
    applications = Application.objects.filter(job=job).select_related('student', 'student__profile')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{job.company_name}_{job.role}_applicants.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'Branch', 'CGPA', 'Backlogs', 'Skills', 'LinkedIn', 'Status', 'Applied At'])
    
    for app in applications:
        profile = app.student.profile
        writer.writerow([
            app.student.username,
            app.student.email,
            profile.branch,
            profile.current_cgpa,
            profile.backlogs,
            profile.skills,
            profile.linkedin_url or '',
            app.status,
            app.applied_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response


@admin_required
def update_application_status(request, application_id):
    """Update application status"""
    application = get_object_or_404(Application, id=application_id)
    
    if request.method == 'POST':
        form = ApplicationStatusForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, 'Application status updated successfully!')
            return redirect('job_applicants', job_id=application.job.id)
    else:
        form = ApplicationStatusForm(instance=application)
    
    return render(request, 'career/update_status.html', {'form': form, 'application': application})


@student_required
def student_dashboard(request):
    """Student dashboard view"""
    try:
        profile = request.user.profile
    except StudentProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('edit_profile')
    
    # Get active jobs
    active_jobs = JobPost.objects.filter(is_active=True, deadline__gte=timezone.now())
    
    # Get student's applications
    applied_job_ids = Application.objects.filter(student=request.user).values_list('job_id', flat=True)
    
    # Categorize jobs
    jobs_with_eligibility = []
    for job in active_jobs:
        is_eligible = job.is_student_eligible(profile)
        has_applied = job.id in applied_job_ids
        jobs_with_eligibility.append({
            'job': job,
            'is_eligible': is_eligible,
            'has_applied': has_applied,
        })
    
    # Get student's applications
    my_applications = Application.objects.filter(student=request.user).select_related('job')
    
    context = {
        'profile': profile,
        'jobs_with_eligibility': jobs_with_eligibility,
        'my_applications': my_applications,
    }
    return render(request, 'career/student_dashboard.html', context)


@student_required
def edit_profile(request):
    """Edit student profile"""
    try:
        profile = request.user.profile
    except StudentProfile.DoesNotExist:
        profile = None
    
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('student_dashboard')
    else:
        form = StudentProfileForm(instance=profile)
    
    return render(request, 'career/edit_profile.html', {'form': form})


@student_required
def apply_job(request, job_id):
    """Apply for a job"""
    job = get_object_or_404(JobPost, id=job_id)
    
    # Check if already applied
    if Application.objects.filter(student=request.user, job=job).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('student_dashboard')
    
    # Check eligibility
    try:
        profile = request.user.profile
        if not job.is_student_eligible(profile):
            messages.error(request, 'You are not eligible for this job.')
            return redirect('student_dashboard')
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('edit_profile')
    
    # Create application
    Application.objects.create(student=request.user, job=job)
    messages.success(request, f'Successfully applied for {job.company_name} - {job.role}!')
    return redirect('student_dashboard')


@student_required
def ats_scanner(request):
    """ATS Resume Scanner view"""
    jobs = JobPost.objects.filter(is_active=True)
    
    if request.method == 'POST':
        job_id = request.POST.get('job_id')
        form = ResumeUploadForm(request.POST, request.FILES)
        
        if form.is_valid() and job_id:
            job = get_object_or_404(JobPost, id=job_id)
            resume_file = form.cleaned_data['resume']
            
            # Extract text from PDF
            try:
                pdf_reader = PdfReader(io.BytesIO(resume_file.read()))
                resume_text = ""
                for page in pdf_reader.pages:
                    resume_text += page.extract_text()
                
                # Call Gemini API
                if settings.GEMINI_API_KEY:
                    genai.configure(api_key=settings.GEMINI_API_KEY)
                    model = genai.GenerativeModel('models/gemini-2.5-flash')
                    
                    prompt = f"""
                    Compare this resume against the job description and provide:
                    1. A match score from 0-100
                    2. List exactly 3 missing keywords that would improve the match
                    
                    Job Description:
                    {job.job_description}
                    
                    Resume Text:
                    {resume_text[:4000]}  # Limit text to avoid token limits
                    
                    Format your response as:
                    Score: [number]
                    Missing Keywords: [keyword1], [keyword2], [keyword3]
                    """
                    
                    response = model.generate_content(prompt)
                    result_text = response.text
                    
                    context = {
                        'jobs': jobs,
                        'selected_job': job,
                        'result': result_text,
                        'resume_text': resume_text[:500],  # Show preview
                    }
                    return render(request, 'career/ats_scanner.html', context)
                else:
                    messages.error(request, 'Gemini API key not configured.')
            
            except Exception as e:
                messages.error(request, f'Error processing resume: {str(e)}')
    else:
        form = ResumeUploadForm()
    
    context = {
        'form': form,
        'jobs': jobs,
    }
    return render(request, 'career/ats_scanner.html', context)


@login_required
def job_detail(request, job_id):
    """View job details"""
    job = get_object_or_404(JobPost, id=job_id)
    updates = job.updates.all()
    
    is_eligible = False
    has_applied = False
    update_form = None
    
    if request.user.role == 'student':
        try:
            profile = request.user.profile
            is_eligible = job.is_student_eligible(profile)
            has_applied = Application.objects.filter(student=request.user, job=job).exists()
        except StudentProfile.DoesNotExist:
            pass
    elif request.user.role == 'admin':
        update_form = JobUpdateForm()
    
    context = {
        'job': job,
        'updates': updates,
        'is_eligible': is_eligible,
        'has_applied': has_applied,
        'update_form': update_form,
    }
    return render(request, 'career/job_detail.html', context)


@admin_required
def add_job_update(request, job_id):
    """Add update to a job and notify applicants"""
    job = get_object_or_404(JobPost, id=job_id)
    
    if request.method == 'POST':
        form = JobUpdateForm(request.POST)
        if form.is_valid():
            update = form.save(commit=False)
            update.job = job
            update.save()
            
            # Send email to all applicants
            applicants = Application.objects.filter(job=job).select_related('student')
            recipient_list = []
            for app in applicants:
                if app.student.email:
                    # Check preferences
                    if hasattr(app.student, 'preferences') and not app.student.preferences.receive_emails:
                        continue
                    recipient_list.append(app.student.email)
            
            if recipient_list:
                subject = f"Update: {job.role} at {job.company_name}"
                message = f"""
                Dear Candidate,
                
                There is a new update regarding the job opening for {job.role} at {job.company_name}.
                
                Update:
                {update.message}
                
                Visit the portal for more details.
                
                Best regards,
                UniCareer Team
                """
                # Send mass mail or loop (using loop for simplicity/console backend)
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=True)
            
            messages.success(request, 'Update posted and emails sent to applicants!')
            return redirect('job_detail', job_id=job.id)
            
    return redirect('job_detail', job_id=job.id)


@login_required
def company_wiki_list(request):
    """View all company wiki entries"""
    wikis = CompanyWiki.objects.all()
    
    # Filter by company name if provided
    company_filter = request.GET.get('company', '')
    if company_filter:
        wikis = wikis.filter(company_name__icontains=company_filter)
    
    context = {
        'wikis': wikis,
        'company_filter': company_filter,
    }
    return render(request, 'career/company_wiki_list.html', context)


@login_required
def company_wiki_detail(request, wiki_id):
    """View company wiki detail"""
    wiki = get_object_or_404(CompanyWiki, id=wiki_id)
    return render(request, 'career/company_wiki_detail.html', {'wiki': wiki})


@admin_required
def create_company_wiki(request):
    """Create company wiki entry"""
    if request.method == 'POST':
        form = CompanyWikiForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company wiki entry created successfully!')
            return redirect('company_wiki_list')
    else:
        form = CompanyWikiForm()
    
    return render(request, 'career/create_company_wiki.html', {'form': form})


@login_required
def chatbot(request):
    """AI Chatbot view"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            if not settings.GEMINI_API_KEY:
                return JsonResponse({'error': 'Gemini API key not configured'}, status=500)
            
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            
            # Fetch student profile context
            student_context = ""
            if request.user.role == 'student':
                try:
                    profile = request.user.profile
                    
                    # Extract resume text if available
                    resume_text = "Not available"
                    if profile.resume:
                        try:
                            pdf_reader = PdfReader(profile.resume.path)
                            text = ""
                            for page in pdf_reader.pages:
                                text += page.extract_text()
                            resume_text = text[:2000] + "..." if len(text) > 2000 else text
                        except Exception:
                            resume_text = "Error reading resume file"

                    student_context = f"""
                    Student Profile Context:
                    - Name: {request.user.username}
                    - Branch: {profile.get_branch_display()}
                    - CGPA: {profile.current_cgpa}
                    - Backlogs: {profile.backlogs}
                    - Skills: {profile.skills}
                    - Resume Content: {resume_text}
                    """
                except StudentProfile.DoesNotExist:
                    student_context = f"Student Name: {request.user.username} (Profile incomplete)"

            # Create a chat session (stateless for now, but could be improved)
            chat = model.start_chat(history=[])
            
            # Add system context
            system_prompt = f"""
            You are UniCareer AI, an expert career mentor and placement assistant dedicated to helping university students succeed in their career journey on the UniCareer portal.

            {student_context}

            Your Core Responsibilities:
            1. **Personalized Guidance**: Use the student's profile (Branch, CGPA, Skills) to give specific advice. 
               - If CGPA is low (< 7.0), suggest ways to compensate with projects/skills.
               - If they have backlogs, advise on clearing them before placement season.
               - Suggest roles relevant to their branch ({profile.branch if request.user.role == 'student' and hasattr(request.user, 'profile') else 'their field'}).
            2. **Resume & Profile Optimization**: Provide actionable advice to make resumes ATS-friendly. Suggest strong action verbs and keywords for specific roles.
            3. **Internship & Job Strategy**: Guide students on how to prepare for internships and placements.
            4. **Interview Preparation**: Offer tips for Technical, HR, and Managerial rounds. Explain the STAR method for behavioral questions.
            5. **Portal Navigation**: Encourage them to use UniCareer features like the 'ATS Scanner' for resume checks and 'Company Wiki' for past interview experiences.

            **Tone & Style:**
            - Professional, motivating, and student-friendly.
            - Address the student by name if possible.
            - Use clear formatting (bullet points, bold text) for readability.
            """
            
            response = chat.send_message(system_prompt + "\n\nUser: " + user_message)
            
            return JsonResponse({'response': response.text})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return render(request, 'career/chatbot.html')


@login_required
def preferences_view(request):
    """View to manage user preferences"""
    # Ensure user has preferences object (for existing users)
    if not hasattr(request.user, 'preferences'):
        UserPreference.objects.create(user=request.user)
        
    if request.method == 'POST':
        form = UserPreferenceForm(request.POST, instance=request.user.preferences)
        if form.is_valid():
            form.save()
            messages.success(request, 'Preferences updated successfully.')
            return redirect('preferences')
    else:
        form = UserPreferenceForm(instance=request.user.preferences)
    
    return render(request, 'career/preferences.html', {'form': form})
