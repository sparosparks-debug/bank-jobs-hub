import random
import string
from datetime import datetime
from database import get_db

def generate_application_ref():
    """Generate professional banking application reference: BNK-2026-ABC123"""
    year = datetime.now().year
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"BNK-{year}-{random_str}"

# ----------------- USERS -----------------
def create_user(full_name, email, mobile, password_hash, qualification, graduation_year, dob=None, address=None, skills=None):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO users (full_name, email, mobile, password_hash, qualification, graduation_year, date_of_birth, address, skills)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (full_name, email.strip().lower(), mobile, password_hash, qualification, graduation_year, dob, address, skills)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return user_id, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()

def get_user_by_email(email):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email.strip(),))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_user_profile(user_id, full_name, mobile, qualification, graduation_year, dob, address, skills):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE users 
        SET full_name = ?, mobile = ?, qualification = ?, graduation_year = ?, date_of_birth = ?, address = ?, skills = ?
        WHERE user_id = ?
        """,
        (full_name, mobile, qualification, graduation_year, dob, address, skills, user_id)
    )
    conn.commit()
    conn.close()
    return True

# ----------------- ADMINS -----------------
def get_admin_by_username(username):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE username = ?", (username.strip(),))
    admin = cursor.fetchone()
    conn.close()
    return admin

def get_admin_by_id(admin_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE admin_id = ?", (admin_id,))
    admin = cursor.fetchone()
    conn.close()
    return admin

# ----------------- JOBS -----------------
def get_all_jobs(filters=None):
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM jobs WHERE 1=1"
    params = []

    if filters:
        if filters.get('keyword'):
            kw = f"%{filters['keyword']}%"
            query += " AND (job_title LIKE ? OR bank_name LIKE ? OR location LIKE ? OR job_description LIKE ?)"
            params.extend([kw, kw, kw, kw])
            
        if filters.get('bank_type') and filters['bank_type'] != 'All':
            query += " AND bank_type = ?"
            params.append(filters['bank_type'])
            
        if filters.get('category') and filters['category'] != 'All':
            query += " AND category = ?"
            params.append(filters['category'])
            
        if filters.get('experience_level') and filters['experience_level'] != 'All':
            query += " AND experience_level = ?"
            params.append(filters['experience_level'])
            
        if filters.get('qualification') and filters['qualification'] != 'All':
            query += " AND qualification_required LIKE ?"
            params.append(f"%{filters['qualification']}%")
            
        if filters.get('location') and filters['location'] != 'All':
            query += " AND location LIKE ?"
            params.append(f"%{filters['location']}%")
            
        if filters.get('status'):
            query += " AND status = ?"
            params.append(filters['status'])
        else:
            query += " AND status = 'Active'"

    query += " ORDER BY job_id DESC"
    cursor.execute(query, params)
    jobs = cursor.fetchall()
    conn.close()
    return jobs

def get_job_by_id(job_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
    job = cursor.fetchone()
    conn.close()
    return job

def get_featured_jobs(limit=6):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE status = 'Active' ORDER BY job_id DESC LIMIT ?", (limit,))
    jobs = cursor.fetchall()
    conn.close()
    return jobs

def get_jobs_by_type(bank_type, limit=4):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM jobs WHERE status = 'Active' AND bank_type = ? ORDER BY job_id DESC LIMIT ?",
        (bank_type, limit)
    )
    jobs = cursor.fetchall()
    conn.close()
    return jobs

def create_job(bank_name, bank_type, category, job_title, job_description, eligibility,
               experience_level, qualification_required, location, salary_range, vacancies_count,
               application_deadline, official_notification_url=None, employer_apply_url=None, is_sample_data=1):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO jobs (
            bank_name, bank_type, category, job_title, job_description, eligibility,
            experience_level, qualification_required, location, salary_range, vacancies_count,
            application_deadline, official_notification_url, employer_apply_url, is_sample_data, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active')
        """,
        (bank_name, bank_type, category, job_title, job_description, eligibility,
         experience_level, qualification_required, location, salary_range, vacancies_count,
         application_deadline, official_notification_url, employer_apply_url, is_sample_data)
    )
    conn.commit()
    job_id = cursor.lastrowid
    conn.close()
    return job_id

def update_job(job_id, bank_name, bank_type, category, job_title, job_description, eligibility,
               experience_level, qualification_required, location, salary_range, vacancies_count,
               application_deadline, official_notification_url, employer_apply_url, status):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE jobs SET
            bank_name = ?, bank_type = ?, category = ?, job_title = ?, job_description = ?,
            eligibility = ?, experience_level = ?, qualification_required = ?, location = ?,
            salary_range = ?, vacancies_count = ?, application_deadline = ?,
            official_notification_url = ?, employer_apply_url = ?, status = ?
        WHERE job_id = ?
        """,
        (bank_name, bank_type, category, job_title, job_description, eligibility,
         experience_level, qualification_required, location, salary_range, vacancies_count,
         application_deadline, official_notification_url, employer_apply_url, status, job_id)
    )
    conn.commit()
    conn.close()
    return True

def delete_job(job_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs WHERE job_id = ?", (job_id,))
    conn.commit()
    conn.close()
    return True

# ----------------- SAVED JOBS -----------------
def toggle_saved_job(user_id, job_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT saved_job_id FROM saved_jobs WHERE user_id = ? AND job_id = ?", (user_id, job_id))
    existing = cursor.fetchone()
    if existing:
        cursor.execute("DELETE FROM saved_jobs WHERE user_id = ? AND job_id = ?", (user_id, job_id))
        saved = False
    else:
        cursor.execute("INSERT INTO saved_jobs (user_id, job_id) VALUES (?, ?)", (user_id, job_id))
        saved = True
    conn.commit()
    conn.close()
    return saved

def get_saved_jobs_for_user(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT j.*, sj.saved_at
        FROM saved_jobs sj
        JOIN jobs j ON sj.job_id = j.job_id
        WHERE sj.user_id = ?
        ORDER BY sj.saved_at DESC
        """,
        (user_id,)
    )
    saved = cursor.fetchall()
    conn.close()
    return saved

def is_job_saved(user_id, job_id):
    if not user_id:
        return False
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM saved_jobs WHERE user_id = ? AND job_id = ?", (user_id, job_id))
    saved = cursor.fetchone() is not None
    conn.close()
    return saved

# ----------------- APPLICATIONS -----------------
def check_already_applied(user_id, job_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT application_id FROM applications WHERE user_id = ? AND job_id = ?", (user_id, job_id))
    app = cursor.fetchone()
    conn.close()
    return app is not None

def submit_application(data):
    conn = get_db()
    cursor = conn.cursor()
    
    # Verify no duplicate
    cursor.execute(
        "SELECT application_id FROM applications WHERE user_id = ? AND job_id = ?",
        (data['user_id'], data['job_id'])
    )
    if cursor.fetchone():
        conn.close()
        return None, "You have already submitted an application for this vacancy."
    
    ref_num = generate_application_ref()
    cursor.execute(
        """
        INSERT INTO applications (
            application_ref, user_id, job_id, candidate_name, candidate_email,
            candidate_mobile, date_of_birth, address, qualification, degree_specialization,
            graduation_year, percentage_cgpa, experience_years, skills, resume_path, photo_path,
            application_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Submitted')
        """,
        (
            ref_num, data['user_id'], data['job_id'], data['candidate_name'], data['candidate_email'],
            data['candidate_mobile'], data.get('date_of_birth'), data.get('address'),
            data['qualification'], data['degree_specialization'], data['graduation_year'],
            data['percentage_cgpa'], data['experience_years'], data.get('skills'),
            data['resume_path'], data.get('photo_path')
        )
    )
    conn.commit()
    app_id = cursor.lastrowid
    conn.close()
    return ref_num, None

def get_applications_by_user(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT a.*, j.job_title, j.bank_name, j.bank_type, j.location, j.application_deadline, j.category
        FROM applications a
        JOIN jobs j ON a.job_id = j.job_id
        WHERE a.user_id = ?
        ORDER BY a.application_id DESC
        """,
        (user_id,)
    )
    apps = cursor.fetchall()
    conn.close()
    return apps

def get_application_by_id(app_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT a.*, j.job_title, j.bank_name, j.bank_type, j.location, j.salary_range, j.category
        FROM applications a
        JOIN jobs j ON a.job_id = j.job_id
        WHERE a.application_id = ?
        """,
        (app_id,)
    )
    app = cursor.fetchone()
    conn.close()
    return app

def get_application_by_ref(app_ref):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT a.*, j.job_title, j.bank_name, j.bank_type, j.location, j.salary_range, j.category
        FROM applications a
        JOIN jobs j ON a.job_id = j.job_id
        WHERE a.application_ref = ?
        """,
        (app_ref,)
    )
    app = cursor.fetchone()
    conn.close()
    return app

def withdraw_application(app_id, user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT application_status FROM applications WHERE application_id = ? AND user_id = ?",
        (app_id, user_id)
    )
    res = cursor.fetchone()
    if not res:
        conn.close()
        return False, "Application not found or unauthorized."
    
    current_status = res['application_status']
    if current_status in ['Selected', 'Rejected', 'Withdrawn']:
        conn.close()
        return False, f"Cannot withdraw an application with status '{current_status}'."

    cursor.execute(
        "UPDATE applications SET application_status = 'Withdrawn' WHERE application_id = ? AND user_id = ?",
        (app_id, user_id)
    )
    conn.commit()
    conn.close()
    return True, None

# ----------------- ADMIN DASHBOARD & MANAGEMENT -----------------
def get_all_applications_admin(filters=None):
    conn = get_db()
    cursor = conn.cursor()
    query = """
        SELECT a.*, j.job_title, j.bank_name, j.bank_type, j.category
        FROM applications a
        JOIN jobs j ON a.job_id = j.job_id
        WHERE 1=1
    """
    params = []
    if filters:
        if filters.get('status') and filters['status'] != 'All':
            query += " AND a.application_status = ?"
            params.append(filters['status'])
        if filters.get('job_id') and filters['job_id'] != 'All':
            query += " AND a.job_id = ?"
            params.append(filters['job_id'])
        if filters.get('keyword'):
            kw = f"%{filters['keyword']}%"
            query += " AND (a.candidate_name LIKE ? OR a.candidate_email LIKE ? OR a.application_ref LIKE ? OR j.bank_name LIKE ?)"
            params.extend([kw, kw, kw, kw])
    
    query += " ORDER BY a.application_id DESC"
    cursor.execute(query, params)
    apps = cursor.fetchall()
    conn.close()
    return apps

def update_application_status_and_interview(app_id, status, interview_date=None, interview_time=None,
                                            interview_mode=None, interview_venue=None, instructions=None, admin_notes=None):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE applications SET
            application_status = ?,
            interview_date = ?,
            interview_time = ?,
            interview_mode = ?,
            interview_venue_or_link = ?,
            interview_instructions = ?,
            admin_notes = ?
        WHERE application_id = ?
        """,
        (status, interview_date, interview_time, interview_mode, interview_venue, instructions, admin_notes, app_id)
    )
    conn.commit()
    conn.close()
    return True

def get_admin_dashboard_stats():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM jobs")
    total_jobs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM jobs WHERE bank_type = 'Government'")
    govt_jobs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM jobs WHERE bank_type = 'Private'")
    private_jobs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM applications")
    total_applications = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM applications WHERE application_status = 'Submitted'")
    submitted_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM applications WHERE application_status = 'Under Review'")
    under_review_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM applications WHERE application_status = 'Shortlisted'")
    shortlisted_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM applications WHERE application_status = 'Interview Scheduled'")
    interview_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM applications WHERE application_status = 'Selected'")
    selected_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users")
    total_candidates = cursor.fetchone()[0]
    
    conn.close()
    return {
        'total_jobs': total_jobs,
        'govt_jobs': govt_jobs,
        'private_jobs': private_jobs,
        'total_applications': total_applications,
        'submitted_count': submitted_count,
        'under_review_count': under_review_count,
        'shortlisted_count': shortlisted_count,
        'interview_count': interview_count,
        'selected_count': selected_count,
        'total_candidates': total_candidates
    }

# ----------------- UNIVERSAL / ALL-BANK REGISTRATIONS -----------------
def generate_universal_ref():
    year = datetime.now().year
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"APEX-ALL-{year}-{random_str}"

def get_all_bank_institutions():
    """Return all unique banks with their sector for selection form"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT bank_name, bank_type FROM jobs ORDER BY bank_type DESC, bank_name ASC")
    banks = cursor.fetchall()
    conn.close()
    return banks

def create_universal_registration(data):
    conn = get_db()
    cursor = conn.cursor()
    ref_num = generate_universal_ref()
    
    cursor.execute(
        """
        INSERT INTO universal_registrations (
            registration_ref, user_id, candidate_name, candidate_email, candidate_mobile,
            date_of_birth, address, qualification, graduation_year, percentage_cgpa,
            experience_level, selected_banks, selected_categories, skills, resume_path, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Registered & Active')
        """,
        (
            ref_num, data.get('user_id'), data['candidate_name'], data['candidate_email'],
            data['candidate_mobile'], data.get('date_of_birth'), data.get('address'),
            data['qualification'], data['graduation_year'], data['percentage_cgpa'],
            data['experience_level'], data['selected_banks'], data['selected_categories'],
            data.get('skills'), data.get('resume_path')
        )
    )
    conn.commit()
    conn.close()
    return ref_num

def get_universal_registration_by_ref(ref):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM universal_registrations WHERE registration_ref = ?", (ref,))
    reg = cursor.fetchone()
    conn.close()
    return reg

