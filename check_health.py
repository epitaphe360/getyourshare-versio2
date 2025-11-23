import requests
import sys

try:
    response = requests.get("http://localhost:5000/health")
    if response.status_code == 200:
        print("✅ Backend is healthy!")
        print(response.json())
    else:
        print(f"❌ Backend returned status code {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ Could not connect to backend: {e}")
