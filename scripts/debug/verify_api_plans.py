
import requests
import json

try:
    response = requests.get("http://localhost:5000/api/subscription-plans")
    if response.status_code == 200:
        data = response.json()
        print("Influencers Plans:")
        for plan in data.get("influencers", []):
            print(f"- {plan['name']} ({plan['code']}): {plan['price']} EUR / {plan['prices']['MAD']} MAD")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Connection error: {e}")
