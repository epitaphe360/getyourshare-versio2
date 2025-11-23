import requests
import json

BASE_URL = "http://localhost:5000/api/analytics"

def test_analytics():
    print("Testing Analytics Overview...")
    try:
        # Note: This endpoint might require authentication. 
        # If so, we might get a 401.
        response = requests.get(f"{BASE_URL}/overview")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
        else:
            print(response.text)
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_analytics()
