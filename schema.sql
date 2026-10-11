-- Banking Management Roles and Job Application Portal Database Schema
-- Compatible with SQLite and MySQL

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    mobile VARCHAR(20) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    qualification VARCHAR(100) NOT NULL,
    graduation_year INTEGER NOT NULL,
    date_of_birth DATE,
    address TEXT,
    skills TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS admins (
    admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(30) DEFAULT 'SuperAdmin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS jobs (
    job_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bank_name VARCHAR(100) NOT NULL,
    bank_type VARCHAR(20) NOT NULL, -- 'Government' or 'Private'
    category VARCHAR(50) NOT NULL,  -- 'Management', 'Clerical', 'Specialist'
    job_title VARCHAR(150) NOT NULL,
    job_description TEXT NOT NULL,
    eligibility TEXT NOT NULL,
    experience_level VARCHAR(50) NOT NULL, -- 'Fresher', '1-3 Years', '3-5 Years', '5+ Years'
    qualification_required VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    salary_range VARCHAR(100) NOT NULL,
    vacancies_count INTEGER DEFAULT 1,
    application_deadline DATE NOT NULL,
    official_notification_url VARCHAR(255),
    employer_apply_url VARCHAR(255),
    is_sample_data BOOLEAN DEFAULT 1, -- 1 for Demonstration Vacancy
    status VARCHAR(20) DEFAULT 'Active', -- 'Active', 'Closed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS applications (
    application_id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_ref VARCHAR(30) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    candidate_name VARCHAR(100) NOT NULL,
    candidate_email VARCHAR(100) NOT NULL,
    candidate_mobile VARCHAR(20) NOT NULL,
    date_of_birth DATE,
    address TEXT,
    qualification VARCHAR(100) NOT NULL,
    degree_specialization VARCHAR(100) NOT NULL,
    graduation_year INTEGER NOT NULL,
    percentage_cgpa VARCHAR(20) NOT NULL,
    experience_years VARCHAR(50) NOT NULL,
    skills TEXT,
    resume_path VARCHAR(255) NOT NULL,
    photo_path VARCHAR(255),
    application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    application_status VARCHAR(50) DEFAULT 'Submitted',
    -- Statuses: 'Submitted', 'Under Review', 'Shortlisted', 'Interview Scheduled', 'Selected', 'Rejected'
    interview_date DATE,
    interview_time VARCHAR(20),
    interview_mode VARCHAR(50), -- 'In-Person', 'Online / Virtual'
    interview_venue_or_link TEXT,
    interview_instructions TEXT,
    admin_notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS saved_jobs (
    saved_job_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, job_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS contact_inquiries (
    inquiry_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    subject VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS universal_registrations (
    registration_id INTEGER PRIMARY KEY AUTOINCREMENT,
    registration_ref VARCHAR(40) UNIQUE NOT NULL,
    user_id INTEGER,
    candidate_name VARCHAR(100) NOT NULL,
    candidate_email VARCHAR(100) NOT NULL,
    candidate_mobile VARCHAR(20) NOT NULL,
    date_of_birth DATE,
    address TEXT,
    qualification VARCHAR(100) NOT NULL,
    graduation_year INTEGER NOT NULL,
    percentage_cgpa VARCHAR(20) NOT NULL,
    experience_level VARCHAR(50) NOT NULL,
    selected_banks TEXT NOT NULL,
    selected_categories TEXT NOT NULL,
    skills TEXT,
    resume_path VARCHAR(255),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'Registered & Active',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

