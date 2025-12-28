# UniCareer - Campus Placement Portal

A comprehensive Django-based web application for managing campus placements, featuring role-based access control, smart job filtering, and AI-powered resume analysis.

## Features

### 1. **Authentication & Authorization**
- Custom user model with role-based access (Admin/Student)
- Separate dashboards for Admins and Students
- Secure login/logout functionality
- Student registration with profile creation

### 2. **Admin Dashboard (Training & Placement Cell)**
- Create, Edit, and Delete job postings
- View all applicants for each job
- Update application status (Applied/Shortlisted/Rejected)
- Export applicant data to CSV
- Add company interview experiences to Company Wiki
- Dashboard with key metrics (Total Jobs, Active Jobs, Total Applications)

### 3. **Student Dashboard**
- **Smart Job Filtering**: Jobs are visually categorized as:
  - **Eligible** (Green badge) - Student meets CGPA and branch requirements
  - **Not Eligible** (Warning badge) - Apply button is disabled
  - **Applied** (Success badge) - Already submitted application
- View active job opportunities
- Apply for eligible jobs with one click
- Track application status
- Edit profile (CGPA, branch, skills, resume, LinkedIn)

### 4. **AI-Powered ATS Resume Scanner**
- Upload resume (PDF format) for specific job postings
- Powered by **Google Gemini API**
- Extracts text from PDF using `pypdf`
- Provides:
  - Match score (0-100)
  - 3 missing keywords for improvement
- Helps students optimize their resumes

### 5. **Company Wiki**
- Repository of interview experiences
- Search functionality by company name
- View interview questions and tips from seniors
- Admin can add new entries

## Technology Stack

- **Backend**: Django 4.2
- **Frontend**: HTML, CSS, Bootstrap 5
- **Database**: SQLite (dev) / PostgreSQL (prod - Supabase)
- **Deployment**: Render (Docker)
- **AI Integration**: Google Gemini API
- **PDF Processing**: pypdf

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/Jayesh435/unicareer-coderush.git
   cd UniCareer
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your Google Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
   Get your API key from: https://makersuite.google.com/app/apikey

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create an admin user**
   
   **Option A: Use the custom createadmin command (Recommended)**
   ```bash
   python manage.py createadmin <username> <email> <password>
   ```
   Example:
   ```bash
   python manage.py createadmin admin admin@unicareer.com adminpass123
   ```
   This automatically creates an admin user with access to both:
   - Django Admin Panel: https://unicareer.onrender.com/admin/
   - Custom Admin Dashboard: https://unicareer.onrender.com/admin-dashboard/
   
   > **Security Note:** For production environments, avoid passing passwords as command-line arguments. Use Option B or set passwords via the Django admin interface after user creation.
   
   **Option B: Use Django's createsuperuser command**
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to set username, email, and password.
   
   Then set the role to 'admin':
   ```bash
   python manage.py shell
   ```
   ```python
   from career.models import CustomUser
   user = CustomUser.objects.get(username='your_username')
   user.role = 'admin'
   user.save()
   exit()
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Home page: http://unicareer.onrender.com/
   - **Admin Access:**
     - Django Admin Panel (manage models): https://unicareer.onrender.com/admin/
     - Custom Admin Dashboard (job management): https://unicareer.onrender.com/admin-dashboard/
     - Login page: https://unicareer.onrender.com/login/
   - **Student Access:**
     - Student registration: https://unicareer.onrender.com/register/
     - Login page: https://unicareer.onrender.com/login/

## Deployment (Render + Docker + Supabase)

This project is configured for deployment on Render using Docker and a Supabase PostgreSQL database.

### Prerequisites
1.  **GitHub Account**: Fork this repository.
2.  **Supabase Account**: Create a new project and get the connection string.
3.  **Render Account**: Sign up for a free account.

### Steps

1.  **Supabase Setup**:
    *   Create a new project on [Supabase](https://supabase.com/).
    *   Go to **Project Settings -> Database**.
    *   Copy the **Connection String (URI)**. It looks like: `postgresql://postgres:[PASSWORD]@db.projectref.supabase.co:5432/postgres`.

2.  **Render Setup**:
    *   Create a new **Web Service** on [Render](https://render.com/).
    *   Connect your GitHub repository.
    *   Select **Docker** as the Runtime.
    *   **Environment Variables**:
        *   `DATABASE_URL`: Paste your Supabase connection string.
        *   `SECRET_KEY`: Generate a random string.
        *   `DEBUG`: `False`
        *   `ALLOWED_HOSTS`: `*` (or your Render URL).
        *   `GEMINI_API_KEY`: Your Google Gemini API key.

3.  **Deploy**:
    *   Click **Create Web Service**.
    *   Render will build the Docker image and start the container.

## Database Models

### 1. CustomUser
- Extends Django's AbstractUser
- Fields: username, email, password, role (student/admin)

### 2. StudentProfile
- One-to-One with CustomUser
- Fields: branch, current_cgpa, backlogs, resume, skills, linkedin_url

### 3. JobPost
- Fields: company_name, role, package_lpa, min_cgpa_required, eligible_branches, deadline, job_description, posted_at, is_active

### 4. Application
- Links Student to JobPost
- Fields: student, job, status (Applied/Shortlisted/Rejected), applied_at
- Unique constraint on (student, job)

### 5. CompanyWiki
- Fields: company_name, year, interview_questions, senior_tips, created_at

## Usage Guide

### Understanding Admin Access

UniCareer provides **two admin interfaces** with different purposes:

1. **Django Admin Panel** (`/admin/`)
   - Built-in Django administration interface
   - Used for direct database management
   - Create, edit, delete any model records
   - Manage users, roles, and permissions
   - Best for system administration and troubleshooting

2. **Custom Admin Dashboard** (`/admin-dashboard/`)
   - Custom-built interface for Training & Placement Cell
   - User-friendly job posting and management
   - View and manage student applications
   - Export applicant data to CSV
   - Add company interview experiences
   - Dashboard with key metrics

**Both interfaces are accessible after logging in with admin credentials.**

### For Admins

1. **Login** with admin credentials at https://unicareer.onrender.com/login/
2. **Choose your admin interface:**
   - For job posting and application management → Custom Admin Dashboard
   - For system administration → Django Admin Panel
3. **Post a Job** (Custom Dashboard):
   - Click "Post New Job"
   - Fill in company details, package, CGPA requirement, eligible branches
   - Set deadline and job description
4. **Manage Applications** (Custom Dashboard):
   - Click on "View Applicants" for any job
   - Review student profiles
   - Update application status
   - Export data to CSV
5. **Add Company Wiki** (Custom Dashboard):
   - Click "Add Company Wiki"
   - Enter company name, year, interview questions, and tips

### For Students

1. **Register** for an account
2. **Complete Profile**:
   - Add branch, CGPA, skills
   - Upload resume (optional)
   - Add LinkedIn profile
3. **Browse Jobs**:
   - View all active opportunities
   - Jobs are filtered based on your eligibility
4. **Apply for Jobs**:
   - Click "Apply Now" for eligible jobs
   - Track status in "My Applications" section
5. **Use ATS Scanner**:
   - Go to "ATS Scanner"
   - Select a job
   - Upload your resume
   - Get AI-powered feedback
6. **Browse Company Wiki**:
   - Research companies
   - Read interview experiences from seniors

## Key Features Explained

### Smart Eligibility Filter

The system automatically checks:
- **CGPA Match**: Student's CGPA >= Job's minimum CGPA requirement
- **Branch Match**: Student's branch is in the job's eligible branches list

If either condition fails:
- Job is marked as "Not Eligible" with a warning badge
- "Apply" button is disabled
- Student can still view job details

### CSV Export Format

Exported CSV includes:
- Username
- Email
- Branch
- CGPA
- Backlogs
- Skills
- LinkedIn URL
- Application Status
- Applied Date/Time

### ATS Scanner Workflow

1. Student selects a job posting
2. Uploads resume (PDF)
3. System extracts text using pypdf
4. Sends job description + resume to Gemini API
5. AI analyzes and returns:
   - Match score (0-100)
   - 3 missing keywords
6. Student can improve resume based on feedback

## Project Structure

```
UniCareer/
├── career/                 # Main Django app
│   ├── migrations/         # Database migrations
│   ├── admin.py           # Admin panel configuration
│   ├── decorators.py      # Role-based access decorators
│   ├── forms.py           # Django forms
│   ├── models.py          # Database models
│   ├── urls.py            # URL routing
│   └── views.py           # View functions
├── templates/
│   └── career/            # HTML templates
├── static/                # Static files (CSS, JS)
├── media/                 # User uploads (resumes)
├── unicareer/            # Project settings
│   ├── settings.py       # Django settings
│   └── urls.py           # Root URL configuration
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Security Features

- Password validation
- CSRF protection
- Role-based access control with decorators
- User authentication required for all features
- SQL injection prevention (Django ORM)

## Future Enhancements

- Email notifications for application status updates
- Advanced search and filters for jobs
- Student analytics dashboard
- Multiple resume versions
- Interview scheduling system
- Video interview integration
- Mobile responsive design improvements

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or contributions, please open an issue on the GitHub repository.

## Screenshots

### Home Page
![Home Page](https://github.com/user-attachments/assets/37561e3e-3ffe-4716-8c8c-5b817e2a1ce7)

### Admin Dashboard
![Admin Dashboard](https://github.com/user-attachments/assets/98401a5a-419b-43f1-aabc-4e170e2f69fc)

### Student Dashboard with Eligibility
![Student Dashboard](https://github.com/user-attachments/assets/88257233-b290-4d49-9734-36cc2552dde7)

### ATS Resume Scanner
![ATS Scanner](https://github.com/user-attachments/assets/87000ebf-d576-424f-9d50-13499b16c4ee)

### Job Applicants Management
![Job Applicants](https://github.com/user-attachments/assets/2f7660d0-a1b5-4cbe-83d1-1d89851c883f)

---

**Built with ❤️ for campus placement management**
