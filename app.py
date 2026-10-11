import os
import csv
import io
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect, url_for, flash,
    session, jsonify, send_from_directory, Response, make_response
)
from werkzeug.utils import secure_filename

import database
import models
import auth

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'banking-portal-secure-key-2026-apex-recruitment')

# Upload configs
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
RESUME_FOLDER = os.path.join(UPLOAD_FOLDER, 'resumes')
PHOTO_FOLDER = os.path.join(UPLOAD_FOLDER, 'photos')

os.makedirs(RESUME_FOLDER, exist_ok=True)
os.makedirs(PHOTO_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # 8 MB max upload limit

ALLOWED_RESUME_EXTENSIONS = {'pdf'}
ALLOWED_PHOTO_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# Initialize DB on start
with app.app_context():
    database.init_db()

# Global template context processor
@app.context_processor
def inject_global_data():
    current_user = None
    current_admin = None
    if 'user_id' in session:
        current_user = models.get_user_by_id(session['user_id'])
    if 'admin_id' in session:
        current_admin = models.get_admin_by_id(session['admin_id'])
    return {
        'current_user': current_user,
        'current_admin': current_admin,
        'now_year': datetime.now().year
    }

# ----------------- PUBLIC ROUTES -----------------

@app.route('/')
def index():
    featured_jobs = models.get_featured_jobs(limit=6)
    govt_jobs = models.get_jobs_by_type('Government', limit=4)
    private_jobs = models.get_jobs_by_type('Private', limit=4)
    stats = models.get_admin_dashboard_stats()
    return render_template(
        'index.html',
        featured_jobs=featured_jobs,
        govt_jobs=govt_jobs,
        private_jobs=private_jobs,
        stats=stats
    )

@app.route('/jobs')
def job_listings():
    # Read query parameters for initial server render
    keyword = request.args.get('keyword', '')
    bank_type = request.args.get('bank_type', 'All')
    category = request.args.get('category', 'All')
    experience_level = request.args.get('experience_level', 'All')
    qualification = request.args.get('qualification', 'All')
    location = request.args.get('location', 'All')

    filters = {
        'keyword': keyword,
        'bank_type': bank_type,
        'category': category,
        'experience_level': experience_level,
        'qualification': qualification,
        'location': location,
        'status': 'Active'
    }

    jobs = models.get_all_jobs(filters)
    return render_template(
        'jobs.html',
        jobs=jobs,
        filters=filters,
        total_results=len(jobs)
    )

@app.route('/jobs/<int:job_id>')
def job_detail(job_id):
    job = models.get_job_by_id(job_id)
    if not job:
        flash('Job vacancy not found.', 'warning')
        return redirect(url_for('job_listings'))
    
    has_applied = False
    is_saved = False
    if 'user_id' in session:
        has_applied = models.check_already_applied(session['user_id'], job_id)
        is_saved = models.is_job_saved(session['user_id'], job_id)
    
    similar_jobs = models.get_all_jobs({
        'category': job['category'],
        'status': 'Active'
    })
    # Filter out current job and limit to 3
    similar_jobs = [j for j in similar_jobs if j['job_id'] != job_id][:3]

    return render_template(
        'job_detail.html',
        job=job,
        has_applied=has_applied,
        is_saved=is_saved,
        similar_jobs=similar_jobs
    )

@app.route('/api/jobs')
def api_jobs():
    """REST API for dynamic AJAX live filtering and searching"""
    keyword = request.args.get('keyword', '').strip()
    bank_type = request.args.get('bank_type', 'All')
    category = request.args.get('category', 'All')
    experience_level = request.args.get('experience_level', 'All')
    qualification = request.args.get('qualification', 'All')
    location = request.args.get('location', 'All')

    filters = {
        'keyword': keyword,
        'bank_type': bank_type,
        'category': category,
        'experience_level': experience_level,
        'qualification': qualification,
        'location': location,
        'status': 'Active'
    }

    jobs_data = models.get_all_jobs(filters)
    results = []
    user_id = session.get('user_id')

    for j in jobs_data:
        saved = False
        applied = False
        if user_id:
            saved = models.is_job_saved(user_id, j['job_id'])
            applied = models.check_already_applied(user_id, j['job_id'])
        results.append({
            'job_id': j['job_id'],
            'bank_name': j['bank_name'],
            'bank_type': j['bank_type'],
            'category': j['category'],
            'job_title': j['job_title'],
            'job_description': j['job_description'],
            'eligibility': j['eligibility'],
            'experience_level': j['experience_level'],
            'qualification_required': j['qualification_required'],
            'location': j['location'],
            'salary_range': j['salary_range'],
            'vacancies_count': j['vacancies_count'],
            'application_deadline': j['application_deadline'],
            'official_notification_url': j['official_notification_url'],
            'employer_apply_url': j['employer_apply_url'],
            'is_sample_data': bool(j['is_sample_data']),
            'is_saved': saved,
            'has_applied': applied
        })

    return jsonify({
        'success': True,
        'count': len(results),
        'jobs': results
    })

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()

        if not name or not email or not subject or not message:
            flash('Please fill in all contact form fields.', 'danger')
        else:
            models.save_contact_inquiry(name, email, subject, message)
            flash('Thank you for contacting us. Your recruitment inquiry has been received by the support desk.', 'success')
            return redirect(url_for('contact'))

    return render_template('contact.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

# ----------------- CANDIDATE AUTHENTICATION -----------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('candidate_dashboard'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        mobile = request.form.get('mobile', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        qualification = request.form.get('qualification', '').strip()
        graduation_year = request.form.get('graduation_year', '').strip()

        # Validation
        if not all([full_name, email, mobile, password, confirm_password, qualification, graduation_year]):
            flash('All registration fields are required.', 'danger')
            return render_template('register.html', form_data=request.form)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html', form_data=request.form)

        if len(password) < 6:
            flash('Password must contain at least 6 characters.', 'danger')
            return render_template('register.html', form_data=request.form)

        try:
            grad_year_int = int(graduation_year)
            if grad_year_int < 1970 or grad_year_int > datetime.now().year + 5:
                flash('Please enter a valid graduation year.', 'danger')
                return render_template('register.html', form_data=request.form)
        except ValueError:
            flash('Graduation year must be a valid number.', 'danger')
            return render_template('register.html', form_data=request.form)

        existing_user = models.get_user_by_email(email)
        if existing_user:
            flash('An account with this email address already exists. Please log in.', 'warning')
            return redirect(url_for('candidate_login'))

        # Secure password hashing
        password_hash = auth.hash_password(password)
        user_id, err = models.create_user(
            full_name=full_name,
            email=email,
            mobile=mobile,
            password_hash=password_hash,
            qualification=qualification,
            graduation_year=grad_year_int
        )

        if err:
            flash(f'Registration error: {err}', 'danger')
            return render_template('register.html', form_data=request.form)

        # Log user in
        session['user_id'] = user_id
        session['user_name'] = full_name
        session['user_email'] = email
        flash('Registration successful! Welcome to the Banking Recruitment Portal.', 'success')
        return redirect(url_for('candidate_dashboard'))

    return render_template('register.html', form_data={})

@app.route('/login', methods=['GET', 'POST'])
def candidate_login():
    if 'user_id' in session:
        return redirect(url_for('candidate_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template('login.html', email=email)

        user = models.get_user_by_email(email)
        if not user or not auth.verify_password(password, user['password_hash']):
            flash('Invalid email or password. Please try again.', 'danger')
            return render_template('login.html', email=email)

        # Establish session
        session['user_id'] = user['user_id']
        session['user_name'] = user['full_name']
        session['user_email'] = user['email']

        flash(f"Welcome back, {user['full_name']}!", 'success')
        next_url = request.args.get('next')
        if next_url and next_url.startswith('/'):
            return redirect(next_url)
        return redirect(url_for('candidate_dashboard'))

    return render_template('login.html')

# ----------------- UNIVERSAL ALL-BANKS REGISTRATION -----------------

@app.route('/register-all-banks', methods=['GET', 'POST'])
def register_all_banks():
    banks_list = models.get_all_bank_institutions()
    current_user_obj = None
    if 'user_id' in session:
        current_user_obj = models.get_user_by_id(session['user_id'])

    if request.method == 'POST':
        candidate_name = request.form.get('candidate_name', '').strip()
        candidate_email = request.form.get('candidate_email', '').strip().lower()
        candidate_mobile = request.form.get('candidate_mobile', '').strip()
        password = request.form.get('password', '').strip()
        dob = request.form.get('date_of_birth', '').strip()
        address = request.form.get('address', '').strip()
        qualification = request.form.get('qualification', '').strip()
        graduation_year = request.form.get('graduation_year', '').strip()
        percentage_cgpa = request.form.get('percentage_cgpa', '').strip()
        experience_level = request.form.get('experience_level', 'Fresher')
        skills = request.form.get('skills', '').strip()
        consent = request.form.get('consent')

        selected_banks = request.form.getlist('banks')
        selected_categories = request.form.getlist('categories')

        if not selected_banks:
            flash('Please select at least one banking institution (or click "Select All Banks").', 'warning')
            return render_template('register_all_banks.html', banks_list=banks_list, current_user_obj=current_user_obj)

        if not selected_categories:
            selected_categories = ['Management', 'Clerical', 'Specialist']

        if not all([candidate_name, candidate_email, candidate_mobile, qualification, graduation_year, percentage_cgpa]):
            flash('Please complete all mandatory particulars marked with *.', 'danger')
            return render_template('register_all_banks.html', banks_list=banks_list, current_user_obj=current_user_obj)

        if not consent:
            flash('Please check the declaration and consent checkbox.', 'danger')
            return render_template('register_all_banks.html', banks_list=banks_list, current_user_obj=current_user_obj)

        # Handle resume file
        resume_rel_path = None
        if 'resume' in request.files and request.files['resume'].filename != '':
            resume_file = request.files['resume']
            if not allowed_file(resume_file.filename, ALLOWED_RESUME_EXTENSIONS):
                flash('Resume must be in PDF format (.pdf).', 'danger')
                return render_template('register_all_banks.html', banks_list=banks_list, current_user_obj=current_user_obj)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_name = secure_filename(f"universal_resume_{timestamp}_{resume_file.filename}")
            resume_file.save(os.path.join(RESUME_FOLDER, safe_name))
            resume_rel_path = f"uploads/resumes/{safe_name}"

        # Create or fetch user
        user_id = session.get('user_id')
        if not user_id:
            existing_user = models.get_user_by_email(candidate_email)
            if existing_user:
                user_id = existing_user['user_id']
            else:
                user_pass = password if password else 'BankCandidate@2026'
                hashed = auth.hash_password(user_pass)
                user_id, _ = models.create_user(
                    full_name=candidate_name,
                    email=candidate_email,
                    mobile=candidate_mobile,
                    password_hash=hashed,
                    qualification=qualification,
                    graduation_year=int(graduation_year),
                    dob=dob or None,
                    address=address or None,
                    skills=skills or None
                )

            # Auto-login candidate
            session['user_id'] = user_id
            session['user_name'] = candidate_name
            session['user_email'] = candidate_email

        # Save Universal Registration
        reg_payload = {
            'user_id': user_id,
            'candidate_name': candidate_name,
            'candidate_email': candidate_email,
            'candidate_mobile': candidate_mobile,
            'date_of_birth': dob or None,
            'address': address or None,
            'qualification': qualification,
            'graduation_year': int(graduation_year),
            'percentage_cgpa': percentage_cgpa,
            'experience_level': experience_level,
            'selected_banks': ", ".join(selected_banks),
            'selected_categories': ", ".join(selected_categories),
            'skills': skills or None,
            'resume_path': resume_rel_path or "uploads/resumes/default_resume.pdf"
        }

        ref_no = models.create_universal_registration(reg_payload)

        # Enroll candidate across active jobs in selected banks
        for bank_item in selected_banks:
            # find matching active jobs in this bank
            conn = database.get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT job_id, job_title FROM jobs WHERE bank_name LIKE ? AND status = 'Active'", (f"%{bank_item}%",))
            bank_jobs = cursor.fetchall()
            conn.close()

            for bj in bank_jobs:
                if not models.check_already_applied(user_id, bj['job_id']):
                    models.submit_application({
                        'user_id': user_id,
                        'job_id': bj['job_id'],
                        'candidate_name': candidate_name,
                        'candidate_email': candidate_email,
                        'candidate_mobile': candidate_mobile,
                        'date_of_birth': dob or None,
                        'address': address or None,
                        'qualification': qualification,
                        'degree_specialization': qualification,
                        'graduation_year': int(graduation_year),
                        'percentage_cgpa': percentage_cgpa,
                        'experience_years': experience_level,
                        'skills': skills or None,
                        'resume_path': resume_rel_path or "uploads/resumes/default_resume.pdf",
                        'photo_path': None
                    })

        flash(f'Universal Registration successful! Reference Code: {ref_no}', 'success')
        return redirect(url_for('registration_success', ref=ref_no))

    return render_template('register_all_banks.html', banks_list=banks_list, current_user_obj=current_user_obj)

@app.route('/registration-success/<ref>')
def registration_success(ref):
    reg = models.get_universal_registration_by_ref(ref)
    if not reg:
        flash('Registration reference not found.', 'warning')
        return redirect(url_for('index'))
    return render_template('registration_success.html', reg=reg)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_email', None)
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('index'))

# ----------------- CANDIDATE DASHBOARD & ACTIONS -----------------

@app.route('/dashboard')
@auth.login_required
def candidate_dashboard():
    user = models.get_user_by_id(session['user_id'])
    applications = models.get_applications_by_user(session['user_id'])
    saved_jobs = models.get_saved_jobs_for_user(session['user_id'])

    # Application status summary
    status_counts = {
        'Total': len(applications),
        'Submitted': sum(1 for a in applications if a['application_status'] == 'Submitted'),
        'Under Review': sum(1 for a in applications if a['application_status'] == 'Under Review'),
        'Shortlisted': sum(1 for a in applications if a['application_status'] == 'Shortlisted'),
        'Interview Scheduled': sum(1 for a in applications if a['application_status'] == 'Interview Scheduled'),
        'Selected': sum(1 for a in applications if a['application_status'] == 'Selected'),
        'Rejected': sum(1 for a in applications if a['application_status'] == 'Rejected')
    }

    return render_template(
        'dashboard.html',
        user=user,
        applications=applications,
        saved_jobs=saved_jobs,
        status_counts=status_counts
    )

@app.route('/profile/update', methods=['POST'])
@auth.login_required
def update_profile():
    full_name = request.form.get('full_name', '').strip()
    mobile = request.form.get('mobile', '').strip()
    qualification = request.form.get('qualification', '').strip()
    graduation_year = request.form.get('graduation_year', '').strip()
    dob = request.form.get('date_of_birth', '').strip()
    address = request.form.get('address', '').strip()
    skills = request.form.get('skills', '').strip()

    if not full_name or not mobile or not qualification or not graduation_year:
        flash('Full name, mobile number, qualification, and graduation year are required.', 'danger')
        return redirect(url_for('candidate_dashboard'))

    try:
        grad_year_int = int(graduation_year)
    except ValueError:
        flash('Invalid graduation year.', 'danger')
        return redirect(url_for('candidate_dashboard'))

    models.update_user_profile(
        user_id=session['user_id'],
        full_name=full_name,
        mobile=mobile,
        qualification=qualification,
        graduation_year=grad_year_int,
        dob=dob or None,
        address=address or None,
        skills=skills or None
    )
    session['user_name'] = full_name
    flash('Candidate profile updated successfully.', 'success')
    return redirect(url_for('candidate_dashboard'))

@app.route('/apply/<int:job_id>', methods=['GET', 'POST'])
@auth.login_required
def apply_job(job_id):
    job = models.get_job_by_id(job_id)
    if not job:
        flash('The selected job vacancy does not exist.', 'warning')
        return redirect(url_for('job_listings'))

    user = models.get_user_by_id(session['user_id'])
    
    # Check duplicate application
    if models.check_already_applied(session['user_id'], job_id):
        flash('You have already submitted an application for this vacancy. Check your dashboard for tracking status.', 'info')
        return redirect(url_for('candidate_dashboard'))

    if request.method == 'POST':
        candidate_name = request.form.get('candidate_name', '').strip()
        candidate_email = request.form.get('candidate_email', '').strip()
        candidate_mobile = request.form.get('candidate_mobile', '').strip()
        dob = request.form.get('date_of_birth', '').strip()
        address = request.form.get('address', '').strip()
        qualification = request.form.get('qualification', '').strip()
        degree_specialization = request.form.get('degree_specialization', '').strip()
        graduation_year = request.form.get('graduation_year', '').strip()
        percentage_cgpa = request.form.get('percentage_cgpa', '').strip()
        experience_years = request.form.get('experience_years', '').strip()
        skills = request.form.get('skills', '').strip()
        consent = request.form.get('consent')

        # Form validations
        if not consent:
            flash('You must agree to the declaration and verification terms.', 'danger')
            return render_template('apply.html', job=job, user=user, form_data=request.form)

        if not all([candidate_name, candidate_email, candidate_mobile, qualification, degree_specialization, graduation_year, percentage_cgpa, experience_years]):
            flash('Please fill in all mandatory application fields marked with *.', 'danger')
            return render_template('apply.html', job=job, user=user, form_data=request.form)

        # File upload: Resume (PDF required)
        if 'resume' not in request.files:
            flash('Please upload your resume in PDF format.', 'danger')
            return render_template('apply.html', job=job, user=user, form_data=request.form)

        resume_file = request.files['resume']
        if resume_file.filename == '':
            flash('No resume file selected.', 'danger')
            return render_template('apply.html', job=job, user=user, form_data=request.form)

        if not allowed_file(resume_file.filename, ALLOWED_RESUME_EXTENSIONS):
            flash('Invalid resume file format. Only PDF files (.pdf) are allowed.', 'danger')
            return render_template('apply.html', job=job, user=user, form_data=request.form)

        # Save resume securely
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_resume_name = secure_filename(f"resume_{session['user_id']}_{job_id}_{timestamp}.pdf")
        resume_save_path = os.path.join(RESUME_FOLDER, safe_resume_name)
        resume_file.save(resume_save_path)

        # Optional Photo Upload
        photo_rel_path = None
        if 'photo' in request.files:
            photo_file = request.files['photo']
            if photo_file.filename != '' and allowed_file(photo_file.filename, ALLOWED_PHOTO_EXTENSIONS):
                ext = photo_file.filename.rsplit('.', 1)[1].lower()
                safe_photo_name = secure_filename(f"photo_{session['user_id']}_{job_id}_{timestamp}.{ext}")
                photo_file.save(os.path.join(PHOTO_FOLDER, safe_photo_name))
                photo_rel_path = f"uploads/photos/{safe_photo_name}"

        # Submit to DB
        app_data = {
            'user_id': session['user_id'],
            'job_id': job_id,
            'candidate_name': candidate_name,
            'candidate_email': candidate_email,
            'candidate_mobile': candidate_mobile,
            'date_of_birth': dob or None,
            'address': address or None,
            'qualification': qualification,
            'degree_specialization': degree_specialization,
            'graduation_year': int(graduation_year),
            'percentage_cgpa': percentage_cgpa,
            'experience_years': experience_years,
            'skills': skills or None,
            'resume_path': f"uploads/resumes/{safe_resume_name}",
            'photo_path': photo_rel_path
        }

        ref_no, err = models.submit_application(app_data)
        if err:
            flash(err, 'danger')
            return render_template('apply.html', job=job, user=user, form_data=request.form)

        flash(f'Application submitted successfully! Reference Number: {ref_no}', 'success')
        return redirect(url_for('application_confirmation', app_ref=ref_no))

    return render_template('apply.html', job=job, user=user, form_data={})

@app.route('/application/confirm/<app_ref>')
@auth.login_required
def application_confirmation(app_ref):
    application = models.get_application_by_ref(app_ref)
    if not application:
        flash('Application reference not found.', 'warning')
        return redirect(url_for('candidate_dashboard'))

    # Ensure this application belongs to the logged-in candidate
    if application['user_id'] != session['user_id']:
        flash('Unauthorized access to application confirmation.', 'danger')
        return redirect(url_for('candidate_dashboard'))

    return render_template('application_confirmation.html', app=application)

@app.route('/application/<int:app_id>/withdraw', methods=['POST'])
@auth.login_required
def withdraw_app(app_id):
    success, msg = models.withdraw_application(app_id, session['user_id'])
    if success:
        flash('Your application has been withdrawn.', 'info')
    else:
        flash(msg or 'Unable to withdraw application.', 'warning')
    return redirect(url_for('candidate_dashboard'))

@app.route('/api/save-job/<int:job_id>', methods=['POST'])
@auth.login_required
def api_toggle_save(job_id):
    saved = models.toggle_saved_job(session['user_id'], job_id)
    return jsonify({
        'success': True,
        'saved': saved,
        'message': 'Job saved to favorites' if saved else 'Job removed from favorites'
    })

# ----------------- ADMINISTRATOR PORTAL -----------------

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if 'admin_id' in session:
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        admin = models.get_admin_by_username(username)
        if not admin or not auth.verify_password(password, admin['password_hash']):
            flash('Invalid Administrator credentials. Please verify your username and password.', 'danger')
            return render_template('admin_login.html', username=username)

        session['admin_id'] = admin['admin_id']
        session['admin_username'] = admin['username']
        session['admin_role'] = admin['role']

        flash('Administrator authentication successful.', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    session.pop('admin_role', None)
    flash('Administrator session terminated.', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@auth.admin_required
def admin_dashboard():
    stats = models.get_admin_dashboard_stats()
    recent_applications = models.get_all_applications_admin()[:8]
    
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT j.job_id, j.job_title, j.bank_name, j.bank_type, j.category, COUNT(a.application_id) as applicant_count
        FROM jobs j
        LEFT JOIN applications a ON j.job_id = a.job_id
        GROUP BY j.job_id
        ORDER BY applicant_count DESC, j.job_id ASC
    """)
    job_stats = cursor.fetchall()
    conn.close()

    return render_template(
        'admin_dashboard.html',
        stats=stats,
        recent_applications=recent_applications,
        job_stats=job_stats
    )

@app.route('/admin/jobs', methods=['GET', 'POST'])
@auth.admin_required
def admin_jobs():
    if request.method == 'POST':
        bank_name = request.form.get('bank_name', '').strip()
        bank_type = request.form.get('bank_type', 'Government')
        category = request.form.get('category', 'Management')
        job_title = request.form.get('job_title', '').strip()
        job_description = request.form.get('job_description', '').strip()
        eligibility = request.form.get('eligibility', '').strip()
        experience_level = request.form.get('experience_level', 'Fresher')
        qualification_required = request.form.get('qualification_required', '').strip()
        location = request.form.get('location', '').strip()
        salary_range = request.form.get('salary_range', '').strip()
        vacancies_count = request.form.get('vacancies_count', 1)
        application_deadline = request.form.get('application_deadline', '').strip()
        official_notification_url = request.form.get('official_notification_url', '').strip() or None
        employer_apply_url = request.form.get('employer_apply_url', '').strip() or None

        if not all([bank_name, job_title, job_description, eligibility, qualification_required, location, salary_range, application_deadline]):
            flash('Please complete all required vacancy fields.', 'danger')
        else:
            models.create_job(
                bank_name=bank_name,
                bank_type=bank_type,
                category=category,
                job_title=job_title,
                job_description=job_description,
                eligibility=eligibility,
                experience_level=experience_level,
                qualification_required=qualification_required,
                location=location,
                salary_range=salary_range,
                vacancies_count=int(vacancies_count or 1),
                application_deadline=application_deadline,
                official_notification_url=official_notification_url,
                employer_apply_url=employer_apply_url,
                is_sample_data=0
            )
            flash(f'New vacancy "{job_title}" at {bank_name} published successfully!', 'success')
            return redirect(url_for('admin_jobs'))

    # get active and inactive with applicant counts
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT j.*, COUNT(a.application_id) as applicant_count
        FROM jobs j
        LEFT JOIN applications a ON j.job_id = a.job_id
        GROUP BY j.job_id
        ORDER BY applicant_count DESC, j.job_id DESC
    """)
    all_jobs = cursor.fetchall()
    conn.close()

    return render_template('admin_jobs.html', jobs=all_jobs)

@app.route('/admin/jobs/<int:job_id>/edit', methods=['POST'])
@auth.admin_required
def admin_job_edit(job_id):
    bank_name = request.form.get('bank_name', '').strip()
    bank_type = request.form.get('bank_type', 'Government')
    category = request.form.get('category', 'Management')
    job_title = request.form.get('job_title', '').strip()
    job_description = request.form.get('job_description', '').strip()
    eligibility = request.form.get('eligibility', '').strip()
    experience_level = request.form.get('experience_level', 'Fresher')
    qualification_required = request.form.get('qualification_required', '').strip()
    location = request.form.get('location', '').strip()
    salary_range = request.form.get('salary_range', '').strip()
    vacancies_count = request.form.get('vacancies_count', 1)
    application_deadline = request.form.get('application_deadline', '').strip()
    official_notification_url = request.form.get('official_notification_url', '').strip() or None
    employer_apply_url = request.form.get('employer_apply_url', '').strip() or None
    status = request.form.get('status', 'Active')

    models.update_job(
        job_id=job_id,
        bank_name=bank_name,
        bank_type=bank_type,
        category=category,
        job_title=job_title,
        job_description=job_description,
        eligibility=eligibility,
        experience_level=experience_level,
        qualification_required=qualification_required,
        location=location,
        salary_range=salary_range,
        vacancies_count=int(vacancies_count or 1),
        application_deadline=application_deadline,
        official_notification_url=official_notification_url,
        employer_apply_url=employer_apply_url,
        status=status
    )
    flash(f'Vacancy #{job_id} updated successfully.', 'success')
    return redirect(url_for('admin_jobs'))

@app.route('/admin/jobs/<int:job_id>/delete', methods=['POST'])
@auth.admin_required
def admin_job_delete(job_id):
    models.delete_job(job_id)
    flash(f'Vacancy #{job_id} deleted successfully.', 'info')
    return redirect(url_for('admin_jobs'))

@app.route('/admin/applications')
@auth.admin_required
def admin_applications():
    status = request.args.get('status', 'All')
    job_id = request.args.get('job_id', 'All')
    keyword = request.args.get('keyword', '')

    filters = {
        'status': status,
        'job_id': job_id,
        'keyword': keyword
    }

    applications = models.get_all_applications_admin(filters)
    jobs = models.get_all_jobs({'status': 'All'})

    return render_template(
        'admin_applications.html',
        applications=applications,
        jobs=jobs,
        filters=filters
    )

@app.route('/admin/application/<int:app_id>')
@auth.admin_required
def admin_application_detail(app_id):
    app_data = models.get_application_by_id(app_id)
    if not app_data:
        flash('Application record not found.', 'warning')
        return redirect(url_for('admin_applications'))
    return render_template('admin_application_detail.html', app=app_data)

@app.route('/admin/application/<int:app_id>/update-status', methods=['POST'])
@auth.admin_required
def admin_update_app_status(app_id):
    status = request.form.get('application_status')
    interview_date = request.form.get('interview_date', '').strip() or None
    interview_time = request.form.get('interview_time', '').strip() or None
    interview_mode = request.form.get('interview_mode', '').strip() or None
    interview_venue = request.form.get('interview_venue_or_link', '').strip() or None
    instructions = request.form.get('interview_instructions', '').strip() or None
    admin_notes = request.form.get('admin_notes', '').strip() or None

    models.update_application_status_and_interview(
        app_id=app_id,
        status=status,
        interview_date=interview_date,
        interview_time=interview_time,
        interview_mode=interview_mode,
        interview_venue=interview_venue,
        instructions=instructions,
        admin_notes=admin_notes
    )

    flash(f'Application status updated to "{status}" successfully.', 'success')
    return redirect(request.referrer or url_for('admin_applications'))

@app.route('/admin/reports')
@auth.admin_required
def admin_reports():
    stats = models.get_admin_dashboard_stats()
    applications = models.get_all_applications_admin()
    return render_template('admin_reports.html', stats=stats, applications=applications)

@app.route('/admin/reports/export-csv')
@auth.admin_required
def admin_export_csv():
    applications = models.get_all_applications_admin()
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'Application Reference', 'Candidate Name', 'Email', 'Mobile', 'Bank Name',
        'Bank Type', 'Job Title', 'Category', 'Qualification', 'Experience',
        'Status', 'Application Date', 'Interview Date', 'Interview Venue/Link'
    ])

    for a in applications:
        writer.writerow([
            a['application_ref'], a['candidate_name'], a['candidate_email'], a['candidate_mobile'],
            a['bank_name'], a['bank_type'], a['job_title'], a['category'], a['qualification'],
            a['experience_years'], a['application_status'], a['application_date'],
            a['interview_date'] or 'N/A', a['interview_venue_or_link'] or 'N/A'
        ])

    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f"attachment; filename=banking_recruitment_report_{datetime.now().strftime('%Y%m%d')}.csv"
    response.headers['Content-type'] = 'text/csv'
    return response

@app.route('/uploads/resumes/<filename>')
def view_resume(filename):
    """Secure endpoint for viewing uploaded candidate PDF resumes"""
    safe_name = secure_filename(filename)
    return send_from_directory(RESUME_FOLDER, safe_name)

if __name__ == '__main__':
    print("=" * 65)
    print("  Apex Banking Recruitment & Career Management Portal")
    print("  Default Admin Login: username='admin' | password='Admin@123'")
    print("  Server running on http://127.0.0.1:5000")
    print("=" * 65)
    app.run(host='127.0.0.1', port=5000, debug=True)
