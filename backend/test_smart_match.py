import requests
import json

BASE_URL = "http://localhost:8000"
EMAIL = "admin@getyourshare.com"
PASSWORD = "Admin123!"

def test_smart_match_flow():
    session = requests.Session()
    
    # 1. Get CSRF Token via GET request
    print("1. Fetching CSRF token...")
    health_response = session.get(f"{BASE_URL}/health")
    if health_response.status_code != 200:
        print(f"Health check failed: {health_response.text}")
        return

    csrf_token = session.cookies.get("csrf_token")
    if not csrf_token:
        print("No CSRF token found in cookies")
        # Try to see if it's in the response headers or set-cookie
        print("Cookies:", session.cookies.get_dict())
        return
    
    print(f"CSRF Token obtained: {csrf_token[:10]}...")

    # 2. Login
    print("2. Logging in...")
    login_url = f"{BASE_URL}/api/auth/login"
    login_payload = {
        "email": EMAIL,
        "password": PASSWORD
    }
    
    # Login usually doesn't need CSRF if excluded, but good practice to include if we have it
    login_response = session.post(login_url, json=login_payload)
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return
    
    print("Login successful")

    # Extract access_token from cookies
    access_token = session.cookies.get("access_token")
    if not access_token:
        print("No access_token found in cookies")
        print("Cookies:", session.cookies.get_dict())
        # Try to see if it's in the response body
        try:
            data = login_response.json()
            if "access_token" in data:
                access_token = data["access_token"]
                print("Access token found in response body")
        except Exception:
            pass
            
    if not access_token:
        print("Could not find access token")
        return

    # 3. Test Smart Match
    print("3. Testing Smart Match...")
    match_url = f"{BASE_URL}/api/smart-match/find-influencers"
    
    # Payload matching BrandProfile model
    payload = {
        "company_id": "test_company",
        "company_name": "Test Company",
        "product_category": "beauty",
        "target_audience_age": ["18-24", "25-34"],
        "target_audience_gender": "female",
        "target_locations": ["MA"],
        "budget_per_influencer": 5000,
        "commission_percentage": 10,
        "campaign_description": "Test campaign",
        "required_followers_min": 1000,
        "required_engagement_min": 2.0,
        "preferred_platforms": ["instagram"],
        "language": ["fr"]
    }
    
    # Add CSRF header
    headers = {
        "X-CSRF-Token": csrf_token,
        "Authorization": f"Bearer {access_token}"
    }
    
    response = session.post(match_url, json=payload, headers=headers)
    
    if response.status_code == 200:
        print("Smart Match successful")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Smart Match failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_smart_match_flow()
