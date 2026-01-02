import requests
import json

BASE_URL = "http://localhost:5000/api/roi"

def test_roi():
    print("Testing ROI Calculator...")
    
    # 1. Get Benchmarks
    print("\n1. Fetching Benchmarks...")
    try:
        response = requests.get(f"{BASE_URL}/benchmarks")
        if response.status_code == 200:
            print("Benchmarks fetched successfully")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Failed to fetch benchmarks: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")
        return

    # 2. Calculate ROI
    print("\n2. Calculating ROI...")
    payload = {
        "budget": 1000,
        "industry": "fashion",
        "campaign_type": "influencer",
        "average_order_value": 75.0
    }
    
    try:
        response = requests.post(f"{BASE_URL}/calculate", json=payload)
        if response.status_code == 200:
            print("ROI Calculation successful")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Failed to calculate ROI: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_roi()
