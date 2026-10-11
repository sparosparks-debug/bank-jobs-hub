# Govt & Private Bank Jobs Portal (Banking Recruitment and Management)

An enterprise-grade, modern, and fully responsive banking recruitment web application designed for candidates to discover, evaluate, and apply for management, clerical, and specialist roles across **Government (Public Sector)** and **Private Commercial Banks**.

The system features an applicant portal with multi-step status tracking and an administrative command center for recruitment management, resume evaluation, interview scheduling, and analytics reporting.

---

## 🏛️ Key Features

### 1. Public Recruitment Portal & Homepage
- **Hero & Search Engine**: Search vacancies by designation, bank name, location, and sector (Government / Private).
- **Executive Metrics**: Live counters for active vacancies, participating banks, registered applicants, and selections.
- **Popular Job Categories**:
  - **Management Positions**: Bank Manager, Assistant Bank Manager, Branch Manager, Operations Manager, Relationship Manager.
  - **Clerical Positions**: Bank Clerk, Junior Associate, Customer Service Associate, Cashier.
  - **Specialist Positions**: IT Officer, Credit Officer, Loan Officer, Financial Analyst, Risk Management Officer.
- **Sector Comparative Analysis**: Clear distinction between Public Sector Banks (PSBs) and Private Commercial Banks, with official gazette notification links (IBPS, SBI, RBI) and employer career portals.
- **Sample Data Transparency**: Clear `[Sample Listing]` labels distinguishing demo vacancies from verified commission recruitment notices.
- **Candidate FAQ & Help Desk**: Interactive accordions and contact inquiry ticket submission.

### 2. Job Search & Live Filtering
- Multi-faceted filtering by:
  - Bank Sector (Government vs Private)
  - Category (Management, Clerical, Specialist)
  - Experience Level (Fresher, 1-3 Years, 3-5 Years, 5+ Years)
  - Qualification (Graduate, MBA, CA, B.Tech/MCA)
  - Location / City
  - Search keyword with real-time AJAX debounce
- Job bookmarking / saving capability.

### 3. Candidate Experience & Registration
- Secure registration and login with **PBKDF2/SHA-256 password hashing**.
- Form validations for mobile numbers, email uniqueness, and graduation year.
- **Online Job Application Form**:
  - Academic credentials, degree specialization, percentage/CGPA, experience, and domain skills.
  - **Resume Upload**: Strictly validated PDF upload format with file size limit enforcement (< 8MB).
  - Photograph upload support.
  - Legal declaration & consent checkbox.
  - **Anti-Duplicate Safeguard**: Prevents duplicate applications for the same vacancy by the same candidate.
  - **Application Reference Number**: Generates unique identification codes (e.g. `BNK-2026-ABC123`).
  - Printable application confirmation and submission receipt.

### 4. Candidate Dashboard & Interactive Status Tracker
- **Real-time 5-Stage Status Tracker**:
  1. `Submitted`
  2. `Under Review`
  3. `Shortlisted`
  4. `Interview Scheduled`
  5. `Selected` or `Rejected`
- **Interview Call Letter Display**: Shows official interview date, time, mode (In-Person / Virtual), venue/link, and instructions when scheduled by the recruitment board.
- Application withdrawal capability for active applications.
- Profile editing and bookmarked vacancies manager.

### 5. Administrator Command Center
- Secure Administrator Login (`admin` / `Admin@123`).
- **Recruitment Metrics**: Total jobs, Govt vs Private split, total applicants, shortlisted candidates, and final selections.
- **Job Vacancy Management**: Add new jobs, edit job details, mark active/closed, or delete vacancies.
- **Candidate Applications Review Portal**:
  - Filter applications by job, bank, and review status.
  - PDF resume preview and direct download.
  - **Status Update & Interview Scheduler**: Set interview appointment date, time, mode (In-person or virtual conference), venue/link, instructions, and confidential internal remarks.
- **Recruitment Analytics & Reports**: Visual breakdown and one-click **CSV data export**.

---

## 🛠️ Technology Stack

| Layer | Technology | Details |
|---|---|---|
| **Frontend** | HTML5, CSS3, JavaScript (ES6+) | Vanilla CSS design system, responsive grid/flexbox, SVG icons, Google Fonts Plus Jakarta Sans |
| **Backend** | Python (Flask 3.1+) | RESTful APIs, Werkzeug security, session management, file upload sanitization |
| **Database** | SQLite (Production ready with MySQL schema) | Parameterized SQL queries, foreign key constraints, automatic seeding |
| **Authentication** | Werkzeug Security | Secure password hashing (`generate_password_hash`, `check_password_hash`) |

---

## 📁 Project Structure

```
applications job/
│
├── app.py                      # Main Flask application with routes and REST APIs
├── database.py                 # SQLite database setup, connection helpers & seeding
├── models.py                   # Business logic, query models, and status helpers
├── auth.py                     # Authentication decorators (login_required, admin_required)
├── schema.sql                  # Database schema (SQLite & MySQL compatible)
├── test_portal.py              # Automated test suite (Integration & unit tests)
├── requirements.txt            # Python dependencies
├── README.md                   # System documentation & setup guide
│
├── static/
│   ├── css/
│   │   ├── style.css           # Luxury Navy/Gold design system, typography, responsive styling
│   │   └── dashboard.css       # Candidate & Administrator dashboard layouts and trackers
│   ├── js/
│   │   ├── main.js             # Mobile menu, bookmarks AJAX, FAQ accordions, alerts
│   │   ├── jobs.js             # Real-time AJAX live filter and job card rendering
│   │   └── apply.js            # Client-side form & PDF resume file upload validator
│   └── uploads/
│       ├── resumes/            # Secure candidate PDF resumes storage
│       └── photos/             # Candidate photographs storage
│
└── templates/
    ├── base.html               # Master layout with top announcements, nav, and footer
    ├── index.html              # Homepage with hero, search, metrics, and categories
    ├── jobs.html               # Job search & live multi-filter portal
    ├── job_detail.html         # Job specification & official notification links
    ├── apply.html              # Application submission form
    ├── application_confirmation.html # Printable acknowledgement slip & reference
    ├── login.html              # Candidate sign in
    ├── register.html           # Candidate registration
    ├── dashboard.html          # Candidate portal & interactive status tracker
    ├── admin_login.html        # Administrator sign in
    ├── admin_dashboard.html    # Admin metrics & recent submissions
    ├── admin_jobs.html         # Add, edit, delete banking vacancies
    ├── admin_applications.html # Applications review & candidate search
    ├── admin_application_detail.html # Dossier review & interview scheduler
    ├── admin_reports.html      # Recruitment analytics & CSV data export
    ├── about.html              # About recruitment framework
    ├── contact.html            # Help desk inquiry tickets
    └── privacy.html            # Candidate privacy notice & data protection
```

---

## 🚀 Getting Started & Local Setup

### 1. Prerequisites
- Python 3.10+ (Recommended: Python 3.11 or Python 3.13)
- `pip` package manager

### 2. Install Dependencies
In your terminal / PowerShell:
```powershell
pip install -r requirements.txt
```

### 3. Initialize Database & Seed Sample Vacancies
```powershell
python database.py
```
*(The database automatically initializes and seeds 14 realistic banking roles and the admin account on first application run as well).*

### 4. Start the Application Server
```powershell
python app.py
```
*(If on Windows with multiple Python versions, use `python3.13 app.py`)*

The server will launch at:
```
http://127.0.0.1:5000
```

---

## 🔑 Default Credentials

### Administrator Login:
- **URL**: `http://127.0.0.1:5000/admin/login`
- **Username**: `admin`
- **Password**: `Admin@123`

### Candidate Account:
- **URL**: `http://127.0.0.1:5000/register`
- You can register any new candidate email (e.g. `priya.sharma@example.com` / `Password@123`).

---

## 🧪 Running the Automated Test Suite

To verify all system features end-to-end:
```powershell
python test_portal.py
```
*(or `python3.13 test_portal.py`)*

The test suite automatically tests:
- `test_01_homepage`: Validates hero section, metrics, and featured jobs rendering.
- `test_02_job_search_and_api`: Tests public search page and dynamic JSON REST API `/api/jobs`.
- `test_03_candidate_registration_and_login`: Tests candidate registration, password hashing, and session management.
- `test_04_job_application_flow_and_anti_duplicate`: Tests PDF upload, reference code creation (`BNK-2026-XXXXXX`), and duplicate application rejection.
- `test_05_admin_portal_and_interview_scheduling`: Tests admin authorization, status updates, interview scheduling, candidate dashboard reflection, and CSV export.

---

## 🌐 API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/jobs` | `GET` | Filter vacancies by `keyword`, `bank_type`, `category`, `experience_level`, `qualification`, `location`. |
| `/api/save-job/<job_id>` | `POST` | Toggle bookmark for authenticated candidates. |
| `/admin/reports/export-csv` | `GET` | Export complete candidate application records as CSV file. |

---

## 🔒 Security Implementations

1. **Password Hashing**: PBKDF2/SHA-256 via `werkzeug.security`.
2. **SQL Injection Protection**: Fully parameterized queries across all database operations.
3. **Session Management**: Secure signed session cookies with role segregation (`login_required` vs `admin_required`).
4. **File Upload Hardening**: Secure filename generation using `secure_filename()`, strict PDF format validation (`.pdf`), and maximum request size caps (8MB).
5. **Anti-Duplication**: Prevents a candidate from submitting duplicate applications for the same job ID.
