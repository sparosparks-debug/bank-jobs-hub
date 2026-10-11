import urllib.request
import urllib.parse
import http.cookiejar
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def run_live_tests():
    print("=" * 60)
    print("  Apex Banking Portal - Live Server End-to-End Tests")
    print(f"  Target: {BASE_URL}")
    print("=" * 60)

    # 1. Test Homepage
    req = urllib.request.Request(f"{BASE_URL}/")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        body = resp.read().decode('utf-8')
        assert "Build Your Career in" in body
        assert "State Bank of India" in body
        print("[PASS] 1. Homepage loads (Status 200 OK)")

    # 2. Test Job Listings
    with urllib.request.urlopen(f"{BASE_URL}/jobs") as resp:
        assert resp.status == 200
        body = resp.read().decode('utf-8')
        assert "Banking Vacancies & Opportunities" in body
        print("[PASS] 2. Job Vacancies Directory loads (Status 200 OK)")

    # 3. Test REST API Live Filtering
    with urllib.request.urlopen(f"{BASE_URL}/api/jobs?category=Management") as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode('utf-8'))
        assert data['success'] is True
        assert data['count'] > 0
        for job in data['jobs']:
            assert job['category'] == 'Management'
        print(f"[PASS] 3. REST API /api/jobs returned {data['count']} Management vacancies")

    # 4. Test Job Detail View
    with urllib.request.urlopen(f"{BASE_URL}/jobs/1") as resp:
        assert resp.status == 200
        body = resp.read().decode('utf-8')
        assert "Role Description & Operational Scope" in body
        print("[PASS] 4. Job Detail view for Job #1 loads (Status 200 OK)")

    # 5. Test About, Privacy, Contact pages
    for path in ['/about', '/privacy', '/contact']:
        with urllib.request.urlopen(f"{BASE_URL}{path}") as resp:
            assert resp.status == 200
            print(f"[PASS] 5. Route '{path}' loads (Status 200 OK)")

    # 6. Test Candidate Registration and Dashboard with Session Cookies
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    ts = int(time.time())
    email = f"live_candidate_{ts}@bankingtest.in"
    reg_data = urllib.parse.urlencode({
        'full_name': 'Devendra Singh',
        'email': email,
        'mobile': '9876543210',
        'password': 'Password@123',
        'confirm_password': 'Password@123',
        'qualification': 'MBA / Post Graduate in Management (Finance / Marketing)',
        'graduation_year': '2023'
    }).encode('utf-8')

    reg_req = urllib.request.Request(f"{BASE_URL}/register", data=reg_data)
    with opener.open(reg_req) as resp:
        assert resp.status == 200
        body = resp.read().decode('utf-8')
        assert "Welcome, Devendra Singh" in body
        print(f"[PASS] 6. Candidate registered and logged in as '{email}'")

    # 7. Test Candidate Dashboard Access
    with opener.open(f"{BASE_URL}/dashboard") as resp:
        assert resp.status == 200
        body = resp.read().decode('utf-8')
        assert "My Submitted Applications" in body
        print("[PASS] 7. Candidate Dashboard rendered for authenticated candidate")

    # 8. Test Bookmark API
    save_req = urllib.request.Request(f"{BASE_URL}/api/save-job/1", data=b'', method='POST')
    save_req.add_header('Content-Type', 'application/json')
    save_req.add_header('X-Requested-With', 'XMLHttpRequest')
    with opener.open(save_req) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode('utf-8'))
        assert data['success'] is True
        print(f"[PASS] 8. Candidate bookmarked Job #1: {data['message']}")

    # 9. Test Admin Authentication & Protected Dashboard
    admin_cj = http.cookiejar.CookieJar()
    admin_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(admin_cj))

    admin_login_data = urllib.parse.urlencode({
        'username': 'admin',
        'password': 'Admin@123'
    }).encode('utf-8')

    admin_login_req = urllib.request.Request(f"{BASE_URL}/admin/login", data=admin_login_data)
    with admin_opener.open(admin_login_req) as resp:
        assert resp.status == 200
        body = resp.read().decode('utf-8')
        assert "Banking Recruitment Command Center" in body
        print("[PASS] 9. Admin authorized successfully with credentials (admin / Admin@123)")

    # 10. Test Admin Jobs, Applications, and Reports Routes
    for admin_path in ['/admin/jobs', '/admin/applications', '/admin/reports']:
        with admin_opener.open(f"{BASE_URL}{admin_path}") as resp:
            assert resp.status == 200
            print(f"[PASS] 10. Admin portal route '{admin_path}' verified (Status 200 OK)")

    # 11. Test Admin CSV Report Export
    with admin_opener.open(f"{BASE_URL}/admin/reports/export-csv") as resp:
        assert resp.status == 200
        content_type = resp.headers.get('Content-Type', '')
        assert 'text/csv' in content_type
        csv_content = resp.read().decode('utf-8')
        assert "Application Reference" in csv_content
        print("[PASS] 11. Recruitment Data CSV Report exported successfully")

    print("=" * 60)
    print("  ALL 11 LIVE SERVER TESTS COMPLETED WITH 100% SUCCESS!")
    print("=" * 60)

if __name__ == '__main__':
    run_live_tests()
