import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'banking_portal.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        cursor.executescript(f.read())
    conn.commit()

    # Seed Admin if not exists
    cursor.execute("SELECT * FROM admins WHERE username = ?", ('admin',))
    if not cursor.fetchone():
        admin_pass_hash = generate_password_hash('Admin@123')
        cursor.execute(
            "INSERT INTO admins (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
            ('admin', 'admin@apexbankportal.gov.in', admin_pass_hash, 'SuperAdmin')
        )
        conn.commit()

    # Seed Sample Jobs if none exist
    cursor.execute("SELECT COUNT(*) FROM jobs")
    count = cursor.fetchone()[0]
    if count == 0:
        seed_sample_jobs(conn)

    conn.close()

def seed_sample_jobs(conn):
    cursor = conn.cursor()
    sample_jobs = [
        # --- MANAGEMENT POSITIONS ---
        (
            "State Bank of India (SBI)",
            "Government",
            "Management",
            "Branch Manager (Scale III)",
            "Lead branch operations, manage portfolio risk, supervise credit appraisal, and ensure adherence to Reserve Bank of India regulatory compliance and customer excellence.",
            "Graduation in any discipline with minimum 60% marks or MBA (Finance) / CA / ICWA. Minimum 5 years of commercial banking experience.",
            "5+ Years",
            "Graduate / Post Graduate / CA",
            "Mumbai, Maharashtra",
            "₹10,50,000 - ₹14,80,000 P.A.",
            45,
            "2026-11-30",
            "https://sbi.co.in/web/careers/current-openings",
            "https://bank.sbi/careers",
            1,
            "Active"
        ),
        (
            "HDFC Bank",
            "Private",
            "Management",
            "Relationship Manager - Corporate Banking",
            "Manage and expand high-net-worth corporate banking relationships, structure working capital facilities, and drive term loan disbursements.",
            "MBA in Finance or Marketing / CFA / Post Graduation in Banking. Relevant corporate relationship management background.",
            "3-5 Years",
            "MBA (Finance) / CFA",
            "Bengaluru, Karnataka",
            "₹9,00,000 - ₹13,50,000 P.A.",
            60,
            "2026-11-25",
            None,
            "https://www.hdfcbank.com/personal/about-us/careers",
            1,
            "Active"
        ),
        (
            "Punjab National Bank (PNB)",
            "Government",
            "Management",
            "Assistant Bank Manager (Operations)",
            "Oversee daily clearing house transactions, oversee treasury settlements, maintain cash reserves, and monitor branch customer grievances.",
            "Bachelor's Degree from a recognized University with computer proficiency and minimum 3 years of banking experience.",
            "3-5 Years",
            "Graduate in any discipline",
            "New Delhi, NCR",
            "₹8,20,000 - ₹11,40,000 P.A.",
            35,
            "2026-12-05",
            "https://www.pnbindia.in/Recruitments.aspx",
            "https://pnbindia.in",
            1,
            "Active"
        ),
        (
            "ICICI Bank",
            "Private",
            "Management",
            "Operations Manager - Retail Banking",
            "Direct retail counter operations, ensure anti-money laundering compliance, supervise audit readiness, and optimize branch efficiency.",
            "Bachelor's Degree or Master's in Business Administration / Finance with strong leadership and analytical skills.",
            "3-5 Years",
            "Graduate / MBA",
            "Hyderabad, Telangana",
            "₹8,50,000 - ₹12,00,000 P.A.",
            50,
            "2026-11-28",
            None,
            "https://www.icicicareers.com",
            1,
            "Active"
        ),
        (
            "Bank of Baroda",
            "Government",
            "Management",
            "Senior Bank Manager (Credit & Risk)",
            "Evaluate large corporate credit proposals, manage syndicated loans, conduct stress-testing of asset portfolios, and ensure NPAs remain minimized.",
            "Post Graduate in Management with Finance specialization / CA / CFA with at least 5 years experience in credit underwriting.",
            "5+ Years",
            "MBA Finance / CA",
            "Ahmedabad, Gujarat",
            "₹12,00,000 - ₹16,50,000 P.A.",
            25,
            "2026-12-15",
            "https://www.bankofbaroda.in/career-detail",
            "https://bankofbaroda.in",
            1,
            "Active"
        ),

        # --- CLERICAL POSITIONS ---
        (
            "Reserve Bank of India (RBI)",
            "Government",
            "Clerical",
            "Junior Associate (Assistant Cadre)",
            "Handle currency management, verify document submissions, maintain inter-bank ledger registers, and assist central banking departments.",
            "Bachelor's Degree in any discipline with a minimum of 50% aggregate marks. Proficient knowledge of local language and computer applications.",
            "Fresher",
            "Graduate in any discipline",
            "Kolkata, West Bengal",
            "₹5,40,000 - ₹7,20,000 P.A.",
            150,
            "2026-11-20",
            "https://opportunities.rbi.org.in",
            "https://opportunities.rbi.org.in/scripts/vacancies.aspx",
            1,
            "Active"
        ),
        (
            "Axis Bank",
            "Private",
            "Clerical",
            "Customer Service Associate",
            "Handle customer onboarding, promote digital banking adoption, assist with KYC document verification, and manage counter inquiries.",
            "Any Graduate (Regular course) with excellent communication skills and basic proficiency in Microsoft Excel and Core Banking Systems.",
            "Fresher",
            "Graduate (B.Com / B.Sc / B.A / BBA)",
            "Chennai, Tamil Nadu",
            "₹4,00,000 - ₹5,50,000 P.A.",
            80,
            "2026-12-10",
            None,
            "https://www.axisbank.com/careers",
            1,
            "Active"
        ),
        (
            "Canara Bank",
            "Government",
            "Clerical",
            "Bank Clerk / Cashier",
            "Perform cash receipt and disbursement operations, maintain currency counting security, issue demand drafts, and process NEFT/RTGS slips.",
            "Degree in any discipline from a recognized University with operating and working knowledge in computer systems.",
            "Fresher",
            "Graduate in any discipline",
            "Pune, Maharashtra",
            "₹4,80,000 - ₹6,50,000 P.A.",
            110,
            "2026-12-01",
            "https://canarabank.com/pages/recruitment",
            "https://ibps.in",
            1,
            "Active"
        ),
        (
            "Kotak Mahindra Bank",
            "Private",
            "Clerical",
            "Branch Customer Cashier",
            "Execute teller transactions, reconcile daily vault balancing, maintain error-free vault records, and resolve teller counter customer queries.",
            "Graduation with mathematics or commerce background preferred. Minimum 1 year teller or cash handling experience.",
            "1-3 Years",
            "B.Com / Any Graduate",
            "Jaipur, Rajasthan",
            "₹4,20,000 - ₹5,80,000 P.A.",
            40,
            "2026-11-22",
            None,
            "https://kotak.com/careers",
            1,
            "Active"
        ),

        # --- SPECIALIST POSITIONS ---
        (
            "State Bank of India (SBI)",
            "Government",
            "Specialist",
            "IT Officer (Cybersecurity & Infrastructure)",
            "Maintain core banking system cybersecurity, conduct vulnerability assessments, manage network firewalls, and prevent unauthorized intrusion vectors.",
            "B.E. / B.Tech in Computer Science / Information Technology / Cybersecurity or MCA / M.Sc (IT) with 60% aggregate.",
            "1-3 Years",
            "B.Tech / B.E. / MCA",
            "Navi Mumbai, Maharashtra",
            "₹9,50,000 - ₹13,00,000 P.A.",
            40,
            "2026-12-12",
            "https://sbi.co.in/careers/specialist-cadre-officers",
            "https://bank.sbi/careers",
            1,
            "Active"
        ),
        (
            "ICICI Bank",
            "Private",
            "Specialist",
            "Credit Officer (MSME & Commercial)",
            "Analyze financial statements, balance sheets, cash flow models, and GST filings to evaluate SME working capital and loan eligibility.",
            "Chartered Accountant (CA) or MBA Finance with in-depth knowledge of financial statement analysis and debt servicing ratios.",
            "1-3 Years",
            "CA / MBA Finance",
            "Surat, Gujarat",
            "₹8,00,000 - ₹11,50,000 P.A.",
            35,
            "2026-11-26",
            None,
            "https://www.icicicareers.com",
            1,
            "Active"
        ),
        (
            "Union Bank of India",
            "Government",
            "Specialist",
            "Risk Management Officer (Market & Liquidity)",
            "Model credit default risks, execute Value-at-Risk (VaR) models, monitor Basel III capital adequacy ratios, and report to ALCO committees.",
            "Master’s Degree in Statistics / Economics / Mathematics / Finance or MBA (Finance) / FRM certification.",
            "3-5 Years",
            "Post Graduate in Statistics / Finance / FRM",
            "Lucknow, Uttar Pradesh",
            "₹10,00,000 - ₹14,20,000 P.A.",
            20,
            "2026-12-18",
            "https://www.unionbankofindia.co.in/english/recruitment.aspx",
            "https://unionbankofindia.co.in",
            1,
            "Active"
        ),
        (
            "HDFC Bank",
            "Private",
            "Specialist",
            "Financial Analyst (Treasury & Investment)",
            "Monitor domestic foreign exchange markets, sovereign bond yield movements, execute asset-liability matching strategies, and prepare macro-economic briefings.",
            "CFA Level 2+ or MBA in Finance from premier institute. Strong quantitative and econometric modeling proficiency.",
            "1-3 Years",
            "CFA / MBA Finance",
            "Gurugram, Haryana",
            "₹11,00,000 - ₹15,00,000 P.A.",
            25,
            "2026-11-29",
            None,
            "https://www.hdfcbank.com/careers",
            1,
            "Active"
        ),
        (
            "Punjab National Bank (PNB)",
            "Government",
            "Specialist",
            "Loan Officer (Retail Mortgages & Agriculture)",
            "Inspect physical collateral properties, conduct legal title search verifications, appraise loan applications under Priority Sector Lending norms.",
            "Degree in Agriculture, Horticulture, or Finance/Commerce with knowledge of credit appraisal guidelines.",
            "1-3 Years",
            "B.Sc (Agri) / B.Com / MBA",
            "Chandigarh, Punjab",
            "₹7,50,000 - ₹10,20,000 P.A.",
            55,
            "2026-12-08",
            "https://pnbindia.in/Recruitments.aspx",
            "https://pnbindia.in",
            1,
            "Active"
        )
    ]

    cursor.executemany(
        """
        INSERT INTO jobs (
            bank_name, bank_type, category, job_title, job_description, eligibility,
            experience_level, qualification_required, location, salary_range, vacancies_count,
            application_deadline, official_notification_url, employer_apply_url, is_sample_data, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        sample_jobs
    )
    conn.commit()
