import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:5000"
EMAIL = "admin@getyourshare.com"
PASSWORD = "Test123!"

def debug_api():
    session = requests.Session()
    
    # 1. Login
    print(f"Logging in as {EMAIL}...")
    try:
        login_response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": EMAIL, "password": PASSWORD}
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            return

        print("✅ Login successful")
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Check Merchants
        print("\nChecking /api/merchants...")
        merchants_response = session.get(f"{BASE_URL}/api/merchants", headers=headers)
        print(f"Status: {merchants_response.status_code}")
        try:
            data = merchants_response.json()
            print(f"Total merchants: {data.get('total')}")
            print(f"Merchants list length: {len(data.get('merchants', []))}")
            if len(data.get('merchants', [])) > 0:
                print("First merchant sample:", json.dumps(data['merchants'][0], indent=2))
            else:
                print("Response body:", json.dumps(data, indent=2))
        except Exception as e:
            print(f"Error parsing merchants response: {e}")
            print(merchants_response.text)

        # 3. Check Influencers
        print("\nChecking /api/influencers...")
        influencers_response = session.get(f"{BASE_URL}/api/influencers", headers=headers)
        print(f"Status: {influencers_response.status_code}")
        try:
            data = influencers_response.json()
            print(f"Total influencers: {data.get('total')}")
            print(f"Influencers list length: {len(data.get('influencers', []))}")
            if len(data.get('influencers', [])) > 0:
                print("First influencer sample:", json.dumps(data['influencers'][0], indent=2))
            else:
                print("Response body:", json.dumps(data, indent=2))
        except Exception as e:
            print(f"Error parsing influencers response: {e}")
            print(influencers_response.text)

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_api()
