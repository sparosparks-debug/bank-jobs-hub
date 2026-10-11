import io
import unittest
from app import app
import database
import models

class BankingPortalTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_01_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Build Your Career in', response.data)
        self.assertIn(b'State Bank of India', response.data)
        print("[PASS] Homepage loads successfully with hero section and featured jobs.")

    def test_02_job_search_and_api(self):
        # Public search HTML
        response = self.client.get('/jobs?bank_type=Government')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Government Banks', response.data)

        # Dynamic REST API
        api_res = self.client.get('/api/jobs?bank_type=Government')
        self.assertEqual(api_res.status_code, 200)
        data = api_res.get_json()
        self.assertTrue(data['success'])
        self.assertTrue(len(data['jobs']) > 0)
        for job in data['jobs']:
            self.assertEqual(job['bank_type'], 'Government')
        print(f"[PASS] REST API /api/jobs returns {len(data['jobs'])} government bank vacancies.")

    def test_03_candidate_registration_and_login(self):
        import time
        t = int(time.time())
        email = f'candidate_{t}@testbank.com'
        reg_data = {
            'full_name': 'Aarav Patel',
            'email': email,
            'mobile': '9876543210',
            'password': 'Password@123',
            'confirm_password': 'Password@123',
            'qualification': 'Graduate (B.Com / B.Sc / B.A / BBA)',
            'graduation_year': '2024'
        }
        res = self.client.post('/register', data=reg_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Welcome, Aarav Patel', res.data)
        print("[PASS] Candidate registration & session initialization passed.")

        # Candidate login
        login_res = self.client.post('/login', data={
            'email': email,
            'password': 'Password@123'
        }, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)
        self.assertIn(b'Dashboard (Aarav)', login_res.data)
        print("[PASS] Candidate login verified.")

    def test_04_job_application_flow_and_anti_duplicate(self):
        import time
        t = int(time.time()) + 1
        email = f'applicant_{t}@testbank.com'
        self.client.post('/register', data={
            'full_name': 'Neha Verma',
            'email': email,
            'mobile': '9876543210',
            'password': 'Password@123',
            'confirm_password': 'Password@123',
            'qualification': 'Graduate (B.Com / B.Sc / B.A / BBA)',
            'graduation_year': '2024'
        })

        # Submit Application for Job 2 with PDF resume
        dummy_pdf = io.BytesIO(b"%PDF-1.4 ... test resume content ...")
        app_form = {
            'candidate_name': 'Neha Verma',
            'candidate_email': email,
            'candidate_mobile': '9876543210',
            'date_of_birth': '2001-05-15',
            'address': 'Flat 402, Marine Drive, Mumbai',
            'qualification': 'Graduate (B.Com / B.Sc / B.A / BBA)',
            'degree_specialization': 'B.Com Banking & Insurance',
            'graduation_year': '2024',
            'percentage_cgpa': '82.5%',
            'experience_years': '1 - 3 Years',
            'skills': 'Finacle, Credit Appraisal, Microsoft Excel',
            'consent': 'on',
            'resume': (dummy_pdf, 'neha_verma_resume.pdf')
        }

        submit_res = self.client.post('/apply/2', data=app_form, content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(submit_res.status_code, 200)
        self.assertIn(b'Application Successfully Submitted!', submit_res.data)
        self.assertIn(b'BNK-2026-', submit_res.data)
        print("[PASS] Application submission & unique reference code generated.")

        # Test duplicate application prevention for the same job
        dup_pdf = io.BytesIO(b"%PDF-1.4 ... test resume ...")
        app_form['resume'] = (dup_pdf, 'neha_verma_resume.pdf')
        dup_res = self.client.post('/apply/2', data=app_form, content_type='multipart/form-data', follow_redirects=True)
        self.assertIn(b'already submitted an application', dup_res.data)
        print("[PASS] Anti-duplicate application safeguard verified.")

    def test_05_admin_portal_and_interview_scheduling(self):
        # Admin Login
        login_res = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'Admin@123'
        }, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)
        self.assertIn(b'Banking Recruitment Command Center', login_res.data)
        print("[PASS] Admin authorization and dashboard access verified.")

        # Fetch recent application ID
        apps = models.get_all_applications_admin()
        self.assertTrue(len(apps) > 0)
        target_app = apps[0]
        app_id = target_app['application_id']

        # Update status and schedule interview
        update_data = {
            'application_status': 'Interview Scheduled',
            'interview_date': '2026-11-15',
            'interview_time': '10:30 AM IST',
            'interview_mode': 'Online / Virtual',
            'interview_venue_or_link': 'https://meet.apexbankportal.gov.in/interview/bnk-panel-3',
            'interview_instructions': 'Keep original Aadhaar card and graduation mark sheets ready for video verification.',
            'admin_notes': 'Candidate exhibits strong credit knowledge.'
        }
        update_res = self.client.post(f'/admin/application/{app_id}/update-status', data=update_data, follow_redirects=True)
        self.assertEqual(update_res.status_code, 200)
        print(f"[PASS] Application #{app_id} status updated to 'Interview Scheduled'.")

        # Verify candidate dashboard reflects interview details
        user_client = app.test_client()
        user_client.post('/login', data={'email': target_app['candidate_email'], 'password': 'Password@123'})
        dash_res = user_client.get('/dashboard')
        self.assertIn(b'Official Interview Call Letter Details', dash_res.data)
        self.assertIn(b'2026-11-15', dash_res.data)
        self.assertIn(b'https://meet.apexbankportal.gov.in', dash_res.data)
        print("[PASS] Candidate dashboard reflects scheduled interview call letter details!")

        # Test CSV Export
        csv_res = self.client.get('/admin/reports/export-csv')
        self.assertEqual(csv_res.status_code, 200)
        self.assertTrue(csv_res.content_type.startswith('text/csv'))
        self.assertIn(b'Application Reference', csv_res.data)
        print("[PASS] Recruitment reports CSV export verified.")

if __name__ == '__main__':
    unittest.main()
