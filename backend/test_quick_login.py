import requests

print("=" * 70)
print("TEST DES COMPTES DE CONNEXION RAPIDE")
print("=" * 70)

accounts = [
    ("influencer1@fashion.com", "Influencer"),
    ("merchant1@fashionstore.com", "Merchant"),
    ("commercial1@getyourshare.com", "Commercial"),
]

for email, role in accounts:
    try:
        r = requests.post("http://localhost:5000/api/auth/login", json={
            "email": email,
            "password": "Test123!"
        })
        
        if r.status_code == 200:
            data = r.json()
            print(f"✓ {role:15} {email:40} → {data['user']['role']}")
        else:
            print(f"✗ {role:15} {email:40} → Status {r.status_code}")
    except Exception as e:
        print(f"✗ {role:15} {email:40} → Erreur: {str(e)}")

print("=" * 70)
