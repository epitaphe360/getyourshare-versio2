import requests
import json
import time
import math
import sys
import random
import string
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

try:
    from supabase_client import supabase
except ImportError:
    print("Warning: Could not import supabase_client. Database operations will be skipped.")
    supabase = None

BASE_URL = "http://localhost:5000"
PASSWORD = "Test1234!"

USERS = {
    "admin": "admin@getyourshare.com",
    "merchant": "merchant1@fashionstore.com",
    "influencer": "influencer1@fashion.com",
    "commercial": "commercial1@shareyoursales.ma"
}

class Color:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

STATS = {
    "total_requests": 0,
    "success": 0,
    "failed": 0,
    "slow": 0,
    "total_time": 0
}

SLOW_THRESHOLD = 1.0  # Seconds

def print_header(text):
    print(f"\n{Color.HEADER}{Color.BOLD}{'='*80}{Color.ENDC}")
    print(f"{Color.HEADER}{Color.BOLD} {text} {Color.ENDC}")
    print(f"{Color.HEADER}{Color.BOLD}{'='*80}{Color.ENDC}")

def print_section(text):
    print(f"\n{Color.BLUE}{Color.BOLD}>> {text}{Color.ENDC}")

def print_success(text, time_taken=None):
    time_str = f" ({time_taken:.3f}s)" if time_taken is not None else ""
    print(f"{Color.GREEN}   [OK] {text}{time_str}{Color.ENDC}")

def print_warning(text):
    print(f"{Color.WARNING}   [WARN] {text}{Color.ENDC}")

def print_fail(text, details=""):
    print(f"{Color.FAIL}   [FAIL] {text}{Color.ENDC}")
    if details:
        print(f"{Color.FAIL}     Details: {details}{Color.ENDC}")

def print_info(key, value):
    print(f"     {key}: {Color.CYAN}{value}{Color.ENDC}")

def check_integrity(data, path="root"):
    """Recursively check for NaN, Infinity, or 'NaN' strings in JSON data."""
    issues = []
    
    if isinstance(data, dict):
        for k, v in data.items():
            issues.extend(check_integrity(v, f"{path}.{k}"))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            issues.extend(check_integrity(item, f"{path}[{i}]"))
    elif isinstance(data, float):
        if math.isnan(data) or math.isinf(data):
            issues.append(f"Found NaN/Inf at {path}: {data}")
    elif isinstance(data, str):
        if data.lower() == "nan":
            issues.append(f"Found 'NaN' string at {path}")
            
    return issues

def validate_response(response, description, expected_status=[200, 201], check_json=True):
    start_time = time.time()
    STATS["total_requests"] += 1
    
    if response.status_code not in expected_status:
        STATS["failed"] += 1
        print_fail(f"Failed {description}", f"Status: {response.status_code}, Body: {response.text[:500]}")
        return False
    
    try:
        if check_json:
            data = response.json()
            issues = check_integrity(data)
            if issues:
                STATS["failed"] += 1
                print_fail(f"Data integrity issues in {description}", ", ".join(issues[:3]))
                return False
        
        STATS["success"] += 1
        return True
    except Exception as e:
        STATS["failed"] += 1
        print_fail(f"Exception validating {description}", str(e))
        return False

def request_wrapper(method, url, description, session=None, **kwargs):
    """Wrapper to measure time and handle validation"""
    start_time = time.time()
    try:
        if session:
            response = session.request(method, url, **kwargs)
        else:
            response = requests.request(method, url, **kwargs)
            
        duration = time.time() - start_time
        STATS["total_time"] += duration
        
        if duration > SLOW_THRESHOLD:
            STATS["slow"] += 1
            print_warning(f"Slow response for {description}: {duration:.3f}s")
            
        if validate_response(response, description):
            print_success(f"{description}", duration)
            return response
        return None
    except Exception as e:
        STATS["failed"] += 1
        print_fail(f"Request Error for {description}", str(e))
        return None

def login(session, email, role_name):
    print_section(f"Authenticating as {role_name} ({email})...")
    try:
        response = request_wrapper(
            "POST",
            f"{BASE_URL}/api/auth/login",
            f"Login {role_name}",
            session=session,
            json={"email": email, "password": PASSWORD},
            headers={"Content-Type": "application/json", "Origin": "http://localhost:3000"}
        )
        
        if response:
            data = response.json()
            user = data.get("user", {})
            
            # Extract token from cookies and set Authorization header
            token = response.cookies.get("access_token")
            if token:
                session.headers.update({"Authorization": f"Bearer {token}"})
            else:
                print_fail("Token not found in cookies")
            
            # Perform a GET request to ensure CSRF cookie is set
            session.get(f"{BASE_URL}/api/dashboard/stats")
            
            # Extract CSRF token from cookies and set X-CSRF-Token header
            csrf_token = session.cookies.get("XSRF-TOKEN")
            if csrf_token:
                session.headers.update({"X-XSRF-TOKEN": csrf_token})
            else:
                print_warning("CSRF Token not found in cookies (might be needed for POST/PUT)")
                
            return user
        return None
    except Exception as e:
        print_fail(f"Login exception", str(e))
        return None

def refresh_csrf_header(session):
    """Update X-CSRF-Token header from current session cookies"""
    csrf_token = session.cookies.get("XSRF-TOKEN")
    if csrf_token:
        session.headers.update({"X-XSRF-TOKEN": csrf_token})

# --- 1. SYSTEM HEALTH & CONFIG ---
def test_system_health(session):
    print_header("TESTING SYSTEM HEALTH")
    request_wrapper("GET", f"{BASE_URL}/health", "System Health Check", session)
    request_wrapper("GET", f"{BASE_URL}/api/health", "API Health Check", session)
    
    # Check Database Connection via a simple query endpoint
    request_wrapper("GET", f"{BASE_URL}/api/public/services", "Database Connection Check", session)

# --- 2. ADMIN DASHBOARD & ANALYTICS ---
def test_admin_dashboard(session):
    print_header("TESTING ADMIN DASHBOARD (ULTRA)")
    
    endpoints = [
        ("/api/dashboard/stats", "Admin Stats (Legacy)"),
        ("/api/analytics/overview", "Admin Analytics Overview"),
        ("/api/analytics/platform-metrics", "Platform Metrics"),
        ("/api/analytics/revenue-chart?days=30", "Revenue Chart"),
        ("/api/analytics/categories", "Category Distribution"),
        ("/api/analytics/top-merchants", "Top Merchants"),
        ("/api/analytics/top-influencers", "Top Influencers"),
        ("/api/admin/users?role=merchant", "Merchant List"),
        ("/api/admin/users?role=influencer", "Influencer List"),
        ("/api/admin/users?role=commercial", "Commercial List"),
        ("/api/admin/invoices", "Admin Invoices"),
        ("/api/admin/gateways/stats", "Gateway Stats"),
        ("/api/logs/audit", "Audit Logs"),
        ("/api/admin/social/posts", "Social Posts"),
        ("/api/admin/social/templates", "Social Templates"),
        ("/api/admin/social/analytics", "Social Analytics")
    ]
    
    for endpoint, desc in endpoints:
        request_wrapper("GET", f"{BASE_URL}{endpoint}", desc, session)

# --- 3. MERCHANT FEATURES ---
def test_merchant_features(session, user_id):
    print_header("TESTING MERCHANT FEATURES (ULTRA)")
    
    endpoints = [
        ("/api/dashboard/stats", "Merchant Stats"),
        (f"/api/analytics/merchant/performance?merchant_id={user_id}", "Merchant Performance"),
        (f"/api/analytics/merchant/sales-chart?merchant_id={user_id}&days=30", "Sales Chart"),
        ("/api/campaigns", "Campaigns List"),
        ("/api/products", "Products List"),
        ("/api/subscriptions/current", "Current Subscription"),
        ("/api/merchant/invoices", "My Invoices"),
        ("/api/leads/deposits/balance", "Deposit Balance"),
        ("/api/leads/deposits/transactions", "Deposit Transactions"),
        ("/api/mobile-payments-ma/providers", "Mobile Payment Providers"),
        ("/api/team/members", "Team Members"),
        ("/api/team/stats", "Team Stats"),
        ("/api/company/links/my-company-links", "Company Links"),
        ("/api/affiliation-requests/merchant/pending", "Pending Affiliation Requests"),
        ("/api/merchant/affiliation-requests/stats", "Affiliation Request Stats"),
        (f"/api/gamification/{user_id}", "Gamification Status"),
        (f"/api/matching/get-recommendations?merchant_id={user_id}", "Influencer Matching")
    ]
    
    for endpoint, desc in endpoints:
        request_wrapper("GET", f"{BASE_URL}{endpoint}", desc, session)

# --- 4. INFLUENCER FEATURES ---
def test_influencer_features(session, user_id):
    print_header("TESTING INFLUENCER FEATURES (ULTRA)")
    
    endpoints = [
        ("/api/dashboard/stats", "Influencer Stats"),
        (f"/api/analytics/influencer/overview?influencer_id={user_id}", "Influencer Overview"),
        (f"/api/analytics/influencer/earnings-chart?influencer_id={user_id}&days=30", "Earnings Chart"),
        ("/api/marketplace/products", "Marketplace Products"),
        ("/api/finance/earnings", "Earnings Wallet"),
        (f"/api/ai/product-recommendations/{user_id}", "AI Product Recommendations"),
        (f"/api/ai/content-templates/{user_id}", "AI Content Templates"),
        ("/api/content-studio/templates", "Content Studio Templates"),
        ("/api/social-media/connections", "Social Connections"),
        ("/api/social-media/dashboard", "Social Dashboard"),
        ("/api/affiliation-requests/my-requests", "My Affiliation Requests"),
        (f"/api/gamification/{user_id}", "Gamification Status"),
        ("/api/affiliate-links", "My Affiliate Links")
    ]
    
    for endpoint, desc in endpoints:
        request_wrapper("GET", f"{BASE_URL}{endpoint}", desc, session)

# --- 5. COMMERCIAL FEATURES ---
def test_commercial_features(session, user_id):
    print_header("TESTING COMMERCIAL FEATURES (ULTRA)")
    
    endpoints = [
        ("/api/sales/dashboard/me", "Commercial Dashboard"),
        ("/api/leads", "Leads List"),
        ("/api/commercials/directory", "Commercials Directory"),
        ("/api/commercials/profile/my-profile", "My Profile"),
        (f"/api/commercials/{user_id}", "Public Profile"),
        ("/api/bot/conversations", "AI Bot Conversations")
    ]
    
    for endpoint, desc in endpoints:
        request_wrapper("GET", f"{BASE_URL}{endpoint}", desc, session)

# --- 6. GLOBAL SEARCH & NEW FEATURES ---
def test_new_features(session):
    print_header("TESTING NEW FEATURES (GLOBAL SEARCH, ETC)")
    
    # Global Search
    search_queries = ["test", "admin", "product", "campaign"]
    for query in search_queries:
        request_wrapper("GET", f"{BASE_URL}/api/search/global?q={query}", f"Global Search: '{query}'", session)
        
    # Notifications
    request_wrapper("GET", f"{BASE_URL}/api/notifications", "Notifications", session)
    
    # SaaS Plans
    request_wrapper("GET", f"{BASE_URL}/api/subscriptions/plans", "SaaS Plans", session)

# --- 7. SECURITY & ACCESS CONTROL ---
def test_security_access(influencer_session):
    print_header("TESTING SECURITY & ACCESS CONTROL")
    
    # Try to access admin endpoints as influencer
    forbidden_endpoints = [
        "/api/admin/users",
        "/api/admin/invoices",
        "/api/analytics/overview"
    ]
    
    for endpoint in forbidden_endpoints:
        print_section(f"Attempting unauthorized access to {endpoint}")
        res = influencer_session.get(f"{BASE_URL}{endpoint}")
        if res.status_code in [401, 403]:
            print_success(f"Access Denied correctly ({res.status_code})")
        else:
            print_fail(f"Security Breach! Influencer accessed {endpoint}", f"Status: {res.status_code}")
            STATS["failed"] += 1

# --- 8. STRESS & PERFORMANCE (MINI) ---
def test_performance_mini(session):
    print_header("TESTING PERFORMANCE (MINI STRESS TEST)")
    
    # Rapidly hit a lightweight endpoint
    endpoint = f"{BASE_URL}/api/health"
    count = 20
    print_section(f"Firing {count} requests to {endpoint}...")
    
    start = time.time()
    successes = 0
    
    def make_req():
        try:
            r = session.get(endpoint)
            return r.status_code == 200
        except Exception:
            return False

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(lambda _: make_req(), range(count)))
        
    duration = time.time() - start
    successes = sum(results)
    
    print_info("Total Requests", count)
    print_info("Successful", successes)
    print_info("Total Time", f"{duration:.3f}s")
    print_info("Avg Time/Req", f"{duration/count:.3f}s")
    print_info("RPS", f"{count/duration:.1f}")
    
    if successes == count:
        print_success("Performance test passed")
    else:
        print_fail("Performance test showed failures")

# --- 9. DATA MUTATION TESTS ---
def test_data_mutation(session, role):
    print_header(f"TESTING DATA MUTATION ({role})")
    
    # Create a temporary campaign (Merchant)
    if role == "Merchant":
        print_section("Creating Test Campaign")
        payload = {
            "name": f"Test Campaign {int(time.time())}",
            "description": "Automated Test Campaign",
            "status": "active",
            "budget": 1000.0,
            "commission_rate": 10.0
        }
        refresh_csrf_header(session)
        res = request_wrapper("POST", f"{BASE_URL}/api/campaigns", "Create Campaign", session, json=payload)
        
        if res and res.status_code in [200, 201]:
            camp_id = res.json().get("id")
            if camp_id:
                print_success(f"Campaign Created: {camp_id}")
                # Delete it (if endpoint exists, otherwise just leave it)
                # request_wrapper("DELETE", f"{BASE_URL}/api/campaigns/{camp_id}", "Delete Campaign", session)

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    print(f"{Color.BOLD}STARTING ULTRA COMPREHENSIVE SYSTEM AUDIT...{Color.ENDC}")
    print(f"Target: {BASE_URL}")
    print(f"Time: {datetime.now().isoformat()}")
    
    # Sessions
    admin_session = requests.Session()
    merchant_session = requests.Session()
    influencer_session = requests.Session()
    commercial_session = requests.Session()
    
    # 0. System Health
    test_system_health(requests.Session())
    
    # 1. Admin Tests
    admin_user = login(admin_session, USERS["admin"], "Admin")
    if admin_user:
        test_admin_dashboard(admin_session)
        test_new_features(admin_session)
        test_performance_mini(admin_session)
        
    # 2. Merchant Tests
    merchant_user = login(merchant_session, USERS["merchant"], "Merchant")
    if merchant_user:
        test_merchant_features(merchant_session, merchant_user["id"])
        test_data_mutation(merchant_session, "Merchant")
        
    # 3. Influencer Tests
    influencer_user = login(influencer_session, USERS["influencer"], "Influencer")
    if influencer_user:
        test_influencer_features(influencer_session, influencer_user["id"])
        test_security_access(influencer_session)
        
    # 4. Commercial Tests
    commercial_user = login(commercial_session, USERS["commercial"], "Commercial")
    if commercial_user:
        test_commercial_features(commercial_session, commercial_user["id"])
        
    # Final Report
    print_header("AUDIT SUMMARY")
    print_info("Total Requests", STATS["total_requests"])
    print_info("Success", f"{Color.GREEN}{STATS['success']}{Color.ENDC}")
    print_info("Failed", f"{Color.FAIL}{STATS['failed']}{Color.ENDC}")
    print_info("Slow Requests", f"{Color.WARNING}{STATS['slow']}{Color.ENDC}")
    print_info("Total Duration", f"{STATS['total_time']:.2f}s")
    
    if STATS["failed"] == 0:
        print(f"\n{Color.GREEN}{Color.BOLD}>> SYSTEM IS HEALTHY AND FULLY OPERATIONAL <<{Color.ENDC}")
    else:
        print(f"\n{Color.FAIL}{Color.BOLD}>> SYSTEM HAS ISSUES ({STATS['failed']} failures) <<{Color.ENDC}")
