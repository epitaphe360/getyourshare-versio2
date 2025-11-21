import requests
import json

BASE_URL = "http://localhost:5000"

print("=" * 60)
print("TEST DE CONNEXION AU TABLEAU DE BORD")
print("=" * 60)

# Test 1: Login
print("\n1. Test Login avec admin@getyourshare.com")
login_data = {
    "email": "admin@getyourshare.com",
    "password": "Admin123!"
}

try:
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Login réussi!")
        print(f"   User: {data.get('user', {}).get('email')}")
        print(f"   Role: {data.get('user', {}).get('role')}")
        
        # Récupérer le cookie
        cookies = response.cookies
        if 'access_token' in cookies:
            print(f"   ✓ Cookie access_token présent")
            token = cookies['access_token']
        else:
            print(f"   ✗ Pas de cookie access_token")
            print(f"   Cookies reçus: {list(cookies.keys())}")
            token = data.get('access_token')
            if token:
                print(f"   → Token dans la réponse JSON")
        
        # Test 2: Accès au dashboard
        print("\n2. Test Accès Dashboard Stats")
        headers = {}
        if token and 'access_token' not in cookies:
            headers['Authorization'] = f'Bearer {token}'
        
        dashboard_response = requests.get(
            f"{BASE_URL}/api/dashboard/stats",
            cookies=cookies,
            headers=headers
        )
        
        print(f"   Status: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            stats = dashboard_response.json()
            print(f"   ✓ Dashboard accessible!")
            print(f"   Stats: {json.dumps(stats, indent=2)}")
        else:
            print(f"   ✗ Erreur: {dashboard_response.text}")
        
        # Test 3: Vérifier /api/auth/me
        print("\n3. Test /api/auth/me")
        me_response = requests.get(
            f"{BASE_URL}/api/auth/me",
            cookies=cookies,
            headers=headers
        )
        
        print(f"   Status: {me_response.status_code}")
        if me_response.status_code == 200:
            user_data = me_response.json()
            print(f"   ✓ User vérifié: {user_data.get('email')} - {user_data.get('role')}")
        else:
            print(f"   ✗ Erreur: {me_response.text}")
            
    else:
        print(f"   ✗ Login échoué!")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"   ✗ Exception: {str(e)}")

print("\n" + "=" * 60)
