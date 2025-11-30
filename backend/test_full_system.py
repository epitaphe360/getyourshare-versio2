import requests
import json
import time
import sys
import io
from datetime import datetime

# Configurer l'encodage UTF-8 pour éviter les erreurs avec les émojis sur Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

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
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Color.HEADER}{Color.BOLD}{'='*80}{Color.ENDC}")
    print(f"{Color.HEADER}{Color.BOLD} {text} {Color.ENDC}")
    print(f"{Color.HEADER}{Color.BOLD}{'='*80}{Color.ENDC}")

def print_section(text):
    print(f"\n{Color.BLUE}{Color.BOLD}>> {text}{Color.ENDC}")

def print_success(text):
    print(f"{Color.GREEN}   ✓ {text}{Color.ENDC}")

def print_fail(text, details=""):
    print(f"{Color.FAIL}   ✗ {text}{Color.ENDC}")
    if details:
        print(f"{Color.FAIL}     Details: {details}{Color.ENDC}")

def print_info(key, value):
    print(f"     {key}: {Color.CYAN}{value}{Color.ENDC}")

def login(session, email, role_name):
    print_section(f"Authenticating as {role_name} ({email})...")
    try:
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": email, "password": PASSWORD},
            headers={"Content-Type": "application/json", "Origin": "http://localhost:3000"}
        )
        
        if response.status_code == 200:
            data = response.json()
            user = data.get("user", {})
            print_success(f"Login successful as {user.get('role')}")
            return True
        else:
            print_fail(f"Login failed: {response.status_code}", response.text)
            return False
    except Exception as e:
        print_fail(f"Login exception", str(e))
        return False

def test_admin_dashboard():
    print_header("TESTING ADMIN DASHBOARD")
    session = requests.Session()
    if not login(session, USERS["admin"], "Admin"):
        return

    # 1. Overview Stats
    print_section("Checking Overview Stats")
    try:
        res = session.get(f"{BASE_URL}/api/analytics/overview")
        if res.status_code == 200:
            data = res.json()
            print_success("Overview stats retrieved")
            print_info("Total Users", data.get("users", {}).get("total"))
            print_info("Total Revenue", f"{data.get('financial', {}).get('total_revenue')} €")
        else:
            print_fail("Overview stats failed", res.text)
    except Exception as e:
        print_fail("Exception", str(e))

    # 2. Platform Metrics
    print_section("Checking Platform Metrics")
    try:
        res = session.get(f"{BASE_URL}/api/analytics/platform-metrics")
        if res.status_code == 200:
            data = res.json()
            print_success("Platform metrics retrieved")
            print_info("Monthly Clicks", data.get("monthly_clicks"))
            print_info("Active Users (7d)", data.get("active_users_7d"))
        else:
            print_fail("Platform metrics failed", res.text)
    except Exception as e:
        print_fail("Exception", str(e))

    # 3. Top Merchants
    print_section("Checking Top Merchants")
    try:
        res = session.get(f"{BASE_URL}/api/analytics/top-merchants")
        if res.status_code == 200:
            data = res.json()
            merchants = data.get("merchants", [])
            print_success(f"Top merchants retrieved ({len(merchants)})")
            if merchants:
                print_info("Top Merchant", f"{merchants[0].get('company_name')} ({merchants[0].get('total_revenue')} €)")
        else:
            print_fail("Top merchants failed", res.text)
    except Exception as e:
        print_fail("Exception", str(e))

def test_merchant_dashboard():
    print_header("TESTING MERCHANT DASHBOARD")
    session = requests.Session()
    if not login(session, USERS["merchant"], "Merchant"):
        return

    # 1. Merchant Performance
    print_section("Checking Merchant Performance")
    try:
        res = session.get(f"{BASE_URL}/api/analytics/merchant/performance")
        if res.status_code == 200:
            data = res.json()
            print_success("Performance stats retrieved")
            print_info("Total Revenue", f"{data.get('total_revenue')} €")
            print_info("Total Sales", data.get("total_sales"))
            print_info("Conversion Rate", f"{data.get('conversion_rate')}%")
        else:
            print_fail("Performance stats failed", res.text)
    except Exception as e:
        print_fail("Exception", str(e))

    # 2. Sales Chart
    print_section("Checking Sales Chart Data")
    try:
        res = session.get(f"{BASE_URL}/api/analytics/merchant/sales-chart?days=30")
        if res.status_code == 200:
            data = res.json()
            points = data.get("data", [])
            print_success(f"Sales chart data retrieved ({len(points)} days)")
        else:
            print_fail("Sales chart failed", res.text)
    except Exception as e:
        print_fail("Exception", str(e))

def test_influencer_dashboard():
    print_header("TESTING INFLUENCER DASHBOARD")
    session = requests.Session()
    if not login(session, USERS["influencer"], "Influencer"):
        return

    # 1. Influencer Overview
    print_section("Checking Influencer Overview")
    try:
        res = session.get(f"{BASE_URL}/api/analytics/influencer/overview")
        if res.status_code == 200:
            data = res.json()
            print_success("Overview stats retrieved")
            print_info("Total Earnings", f"{data.get('total_earnings')} €")
            print_info("Total Clicks", data.get("total_clicks"))
            print_info("Balance", f"{data.get('balance')} €")
        else:
            print_fail("Overview stats failed", res.text)
    except Exception as e:
        print_fail("Exception", str(e))

    # 2. Affiliate Links
    print_section("Checking Affiliate Links")
    try:
        res = session.get(f"{BASE_URL}/api/affiliate-links")
        if res.status_code == 200:
            data = res.json()
            links = data.get("links", [])
            print_success(f"Affiliate links retrieved ({len(links)})")
            if links:
                print_info("First Link", links[0].get("affiliate_url"))
        else:
            print_fail("Affiliate links failed", res.text)
    except Exception as e:
        print_fail("Exception", str(e))

def test_commercial_dashboard():
    print_header("TESTING COMMERCIAL DASHBOARD")
    session = requests.Session()
    if not login(session, USERS["commercial"], "Commercial"):
        return

    # 1. Sales Dashboard
    print_section("Checking Sales Dashboard")
    try:
        res = session.get(f"{BASE_URL}/api/sales/dashboard/me")
        if res.status_code == 200:
            data = res.json()
            print_success("Sales dashboard retrieved")
            print_info("Deals this month", data.get("this_month", {}).get("deals"))
            print_info("Commission Earned", f"{data.get('overview', {}).get('commission_earned')} €")
            print_info("Gamification Level", data.get("gamification", {}).get("level_tier"))
        else:
            print_fail("Sales dashboard failed", res.text)
    except Exception as e:
        print_fail("Exception", str(e))

    # 2. Leads
    print_section("Checking Leads")
    try:
        res = session.get(f"{BASE_URL}/api/sales/leads/me")
        if res.status_code == 200:
            data = res.json()
            leads = data.get("leads", [])
            print_success(f"Leads retrieved ({len(leads)})")
            if leads:
                print_info("First Lead", leads[0].get("company_name"))
        else:
            print_fail("Leads failed", res.text)
    except Exception as e:
        print_fail("Exception", str(e))

def test_live_shopping():
    print_header("TESTING LIVE SHOPPING FEATURES")
    session = requests.Session()
    if not login(session, USERS["influencer"], "Influencer"):
        return

    # 1. Upcoming Lives
    print_section("Checking Upcoming Lives")
    try:
        res = session.get(f"{BASE_URL}/api/ai/live-shopping/upcoming")
        if res.status_code == 200:
            data = res.json()
            lives = data.get("upcoming_lives", [])
            print_success(f"Upcoming lives retrieved ({len(lives)})")
        else:
            print_fail("Upcoming lives failed", res.text)
    except Exception as e:
        print_fail("Exception", str(e))

    # 2. My Sessions
    print_section("Checking My Sessions")
    try:
        # Need user ID first
        auth_res = session.get(f"{BASE_URL}/api/auth/me")
        if auth_res.status_code == 200:
            user_id = auth_res.json().get("id")
            res = session.get(f"{BASE_URL}/api/ai/live-shopping/my-sessions/{user_id}")
            if res.status_code == 200:
                data = res.json()
                sessions = data.get("sessions", [])
                print_success(f"My sessions retrieved ({len(sessions)})")
            else:
                print_fail("My sessions failed", res.text)
        else:
            print_fail("Could not get user ID for my sessions check")
    except Exception as e:
        print_fail("Exception", str(e))

if __name__ == "__main__":
    print(f"{Color.BOLD}STARTING FULL SYSTEM AUDIT...{Color.ENDC}")
    print(f"Target: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_admin_dashboard()
    test_merchant_dashboard()
    test_influencer_dashboard()
    test_commercial_dashboard()
    test_live_shopping()
    
    print_header("AUDIT COMPLETE")
