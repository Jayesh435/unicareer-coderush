from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, StudentProfile, JobPost, Application, CompanyWiki, JobUpdate, UserPreference


class StudentRegistrationForm(UserCreationForm):
    """Form for student registration"""
    email = forms.EmailField(required=True)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = 'student'
        if commit:
            user.save()
        return user


class StudentProfileForm(forms.ModelForm):
    """Form for student profile"""
    class Meta:
        model = StudentProfile
        fields = ['branch', 'current_cgpa', 'backlogs', 'resume', 'skills', 'linkedin_url']
        widgets = {
            'skills': forms.Textarea(attrs={'rows': 3, 'placeholder': 'e.g., Python, Java, Machine Learning'}),
            'current_cgpa': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '10'}),
            'backlogs': forms.NumberInput(attrs={'min': '0'}),
        }


class JobPostForm(forms.ModelForm):
    """Form for creating/editing job posts"""
    class Meta:
        model = JobPost
        fields = ['company_name', 'role', 'package_lpa', 'min_cgpa_required', 
                  'eligible_branches', 'deadline', 'job_description', 'is_active']
        widgets = {
            'job_description': forms.Textarea(attrs={'rows': 5}),
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'eligible_branches': forms.TextInput(attrs={'placeholder': 'CSE,ECE,IT,ME'}),
            'package_lpa': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'min_cgpa_required': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '10'}),
        }


class ApplicationStatusForm(forms.ModelForm):
    """Form for updating application status"""
    class Meta:
        model = Application
        fields = ['status']


class CompanyWikiForm(forms.ModelForm):
    """Form for company wiki entries"""
    class Meta:
        model = CompanyWiki
        fields = ['company_name', 'year', 'interview_questions', 'senior_tips']
        widgets = {
            'interview_questions': forms.Textarea(attrs={'rows': 5}),
            'senior_tips': forms.Textarea(attrs={'rows': 5}),
            'year': forms.NumberInput(attrs={'min': '2000', 'max': '2100'}),
        }


class ResumeUploadForm(forms.Form):
    """Form for uploading resume for ATS scan"""
    resume = forms.FileField(
        label='Upload Resume (PDF)',
        help_text='Upload your resume in PDF format for ATS scanning',
        widget=forms.FileInput(attrs={'accept': '.pdf'})
    )


class JobUpdateForm(forms.ModelForm):
    """Form for posting job updates"""
    class Meta:
        model = JobUpdate
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter update message...'}),
        }


class UserPreferenceForm(forms.ModelForm):
    """Form for user preferences"""
    class Meta:
        model = UserPreference
        fields = ['theme', 'receive_emails']
        widgets = {
            'theme': forms.Select(attrs={'class': 'form-select'}),
            'receive_emails': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
