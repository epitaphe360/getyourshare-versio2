#!/usr/bin/env python
"""Simple test - no emojis to avoid encoding issues"""

import requests
import json

BASE_URL = "http://localhost:5000"

print("="*70)
print("TEST - AUTHENTICATION")
print("="*70)

# Login
print("\n1. LOGIN")
print("-" * 70)

login_response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"email": "admin@getyourshare.com", "password": "Admin123!"},
)

if login_response.status_code != 200:
    print(f"FAILED: {login_response.status_code}")
    exit(1)

print(f"SUCCESS: Login OK")

# Test endpoints
print("\n2. ENDPOINTS WITH COOKIES")
print("-" * 70)

session = requests.Session()
session.cookies.update(login_response.cookies)

endpoints = [
    "/api/analytics/overview",
    "/api/merchants",
    "/api/influencers",
    "/api/products",
    "/api/dashboard/stats",
]

for endpoint in endpoints:
    try:
        response = session.get(f"{BASE_URL}{endpoint}", timeout=5)
        status = "OK" if response.status_code == 200 else f"ERROR {response.status_code}"
        print(f"   {endpoint}: {status}")
    except Exception as e:
        print(f"   {endpoint}: EXCEPTION {type(e).__name__}")

# Test with Bearer Token
print("\n3. ENDPOINTS WITH BEARER TOKEN")
print("-" * 70)

# Get token from cookies
access_token = None
for cookie in login_response.cookies:
    if cookie.name == "access_token":
        access_token = cookie.value
        break

if access_token:
    headers = {"Authorization": f"Bearer {access_token}"}
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=5)
            status = "OK" if response.status_code == 200 else f"ERROR {response.status_code}"
            print(f"   {endpoint}: {status}")
        except Exception as e:
            print(f"   {endpoint}: EXCEPTION {type(e).__name__}")
else:
    print("   No access token found")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
