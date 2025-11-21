#!/usr/bin/env python
"""Vérifier la réponse du login"""

import requests
import json

BASE_URL = "http://localhost:5000"
TEST_EMAIL = "admin@getyourshare.com"
TEST_PASSWORD = "Admin123!"

print("Test de login...")
login_data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}

response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json=login_data,
    timeout=5
)

print(f"\nStatus: {response.status_code}")
print(f"Headers: {dict(response.headers)}")
print(f"\nResponse:")
print(json.dumps(response.json(), indent=2))
