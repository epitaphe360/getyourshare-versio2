import requests
import json

BASE_URL = "http://localhost:8000"
EMAIL = "admin@getyourshare.com"
PASSWORD = "Admin123!"

def test_gamification_flow():
    session = requests.Session()
    
    # 1. Get CSRF Token via GET request
    print("1. Fetching CSRF token...")
    try:
        health_response = session.get(f"{BASE_URL}/health")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Is it running?")
        return

    if health_response.status_code != 200:
        print(f"Health check failed: {health_response.text}")
        return

    csrf_token = session.cookies.get("csrf_token")
    if not csrf_token:
        print("No CSRF token found in cookies")
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
    
    login_response = session.post(login_url, json=login_payload)
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return
    
    print("Login successful")

    # Extract access_token from cookies
    access_token = session.cookies.get("access_token")
    if not access_token:
        print("No access_token found in cookies")
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

    # 3. Get User ID
    print("3. Getting User ID...")
    me_url = f"{BASE_URL}/api/auth/me"
    headers = {
        "X-CSRF-Token": csrf_token,
        "Authorization": f"Bearer {access_token}"
    }
    
    me_response = session.get(me_url, headers=headers)
    if me_response.status_code != 200:
        print(f"Failed to get user info: {me_response.text}")
        return
        
    user_data = me_response.json()
    user_id = user_data.get("id")
    print(f"User ID: {user_id}")

    # 4. Test Gamification Profile
    print("4. Testing Gamification Profile...")
    gamification_url = f"{BASE_URL}/api/gamification/profile"
    params = {"user_id": user_id}
    
    response = session.get(gamification_url, params=params, headers=headers)
    
    if response.status_code == 200:
        print("Gamification Profile successful")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Gamification Profile failed: {response.status_code} - {response.text}")

    # 5. Test Leaderboard
    print("5. Testing Leaderboard...")
    leaderboard_url = f"{BASE_URL}/api/gamification/leaderboard"
    response = session.get(leaderboard_url, headers=headers)
    
    if response.status_code == 200:
        print("Leaderboard successful")
        # Print first 2 entries to avoid spam
        data = response.json()
        if data.get("leaderboard"):
            data["leaderboard"] = data["leaderboard"][:2]
        print(json.dumps(data, indent=2))
    else:
        print(f"Leaderboard failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_gamification_flow()
