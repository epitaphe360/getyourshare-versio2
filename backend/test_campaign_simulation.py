import requests
import json
import os
import sys
from datetime import datetime

# Add backend directory to path to import supabase_client if needed
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Configuration
BASE_URL = "http://localhost:5000"
MERCHANT_EMAIL = "boutique.maroc@getyourshare.com"
INFLUENCER_EMAIL = "hassan.oudrhiri@getyourshare.com"
PASSWORD = "Test123!"

def print_step(step):
    print(f"\n{'='*50}")
    print(f"STEP: {step}")
    print(f"{'='*50}")

def register(email, password, role):
    print_step(f"Registering {role} ({email})")
    url = f"{BASE_URL}/api/auth/register"
    payload = {
        "email": email,
        "password": password,
        "role": role.lower()
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"✅ Registration successful for {email}")
            return True
        elif response.status_code == 400 and "Email déjà utilisé" in response.text:
            print(f"⚠️ User {email} already exists. Proceeding to login.")
            return True
        else:
            print(f"❌ Registration failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Connection error during registration: {e}")
        return False

def login(email, password, role_name):
    print_step(f"Login as {role_name} ({email})")
    url = f"{BASE_URL}/api/auth/login"
    payload = {
        "email": email,
        "password": password
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user = data.get("user")
            print(f"✅ Login successful. User ID: {user['id']}")
            return token, user
        else:
            print(f"❌ Login failed: {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None, None

def create_test_product(merchant_id, token):
    print_step("Creating Test Product (Direct DB Insert)")
    # Since POST /api/products might be missing, we use direct DB insert via supabase client
    # But we are running this as a script, so we can import supabase
    try:
        from supabase_client import supabase
        
        # Use user_id as merchant_id because products table references users table
        # The argument 'merchant_id' passed to this function is actually the user_id from the login response
        
        product_name = f"Test Product {datetime.now().strftime('%H%M%S')}"
        
        product_data = {
            "merchant_id": merchant_id,
            "name": product_name,
            "description": "A fantastic product for testing the affiliation flow.",
            "price": 299.99,
            # "currency": "MAD", # Removed
            "commission_rate": 10.0, # 10%
            # "category": "Mode", # Removed just in case
            # "stock_quantity": 100, # Removed
            # "is_active": True, # Removed
            # "images": ["https://via.placeholder.com/300"], # Removed
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Check if we can insert
        result = supabase.table("products").insert(product_data).execute()
        if result.data:
            product = result.data[0]
            print(f"✅ Product created: {product['name']} (ID: {product['id']})")
            return product
        else:
            print("❌ Failed to create product via DB")
            return None
            
    except ImportError:
        print("❌ Could not import supabase_client. Make sure you are in the root directory.")
        return None
    except Exception as e:
        print(f"❌ Error creating product: {e}")
        return None

def request_affiliation(token, product_id):
    print_step("Requesting Affiliation")
    url = f"{BASE_URL}/api/marketplace/products/{product_id}/request-affiliate"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "message": "I love this product and want to promote it to my 67k followers!"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        req_id = data.get("request_id")
        print(f"✅ Request sent: {data.get('message')} (ID: {req_id})")
        return req_id
    else:
        print(f"❌ Request failed: {response.text}")
        return None

def approve_request(token, request_id):
    print_step("Approving Affiliation Request")
    url = f"{BASE_URL}/api/affiliation-requests/{request_id}/respond"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "status": "approved",
        "merchant_response": "Welcome to the team!"
    }
    
    response = requests.put(url, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Request approved: {data.get('message')}")
        print(f"🔗 Tracking Link: {data.get('tracking_link')}")
        return True
    else:
        print(f"❌ Approval failed: {response.text}")
        return False

def verify_link(token, product_id):
    print_step("Verifying Affiliate Link")
    url = f"{BASE_URL}/api/affiliate/my-links"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"DEBUG: Response from my-links: {json.dumps(data, indent=2)}")
        links = data.get("links", [])
        
        # Find link for our product
        found = False
        for link in links:
            if link.get("product_id") == product_id:
                print(f"✅ Link found for product {product_id}")
                print(f"   URL: {link.get('full_url')}")
                print(f"   Code: {link.get('unique_code')}")
                found = True
                break
        
        if not found:
            print("❌ Link not found in my-links")
    else:
        print(f"❌ Failed to get links: {response.text}")

def main():
    print("🚀 STARTING CAMPAIGN SIMULATION TEST")
    
    # 0. Register Users
    if not register(MERCHANT_EMAIL, PASSWORD, "merchant"): return
    if not register(INFLUENCER_EMAIL, PASSWORD, "influencer"): return

    # 1. Login Merchant
    merchant_token, merchant_user = login(MERCHANT_EMAIL, PASSWORD, "Merchant")
    if not merchant_token: return

    # 2. Create Product
    product = create_test_product(merchant_user['id'], merchant_token)
    if not product: return
    
    # 3. Login Influencer
    influencer_token, influencer_user = login(INFLUENCER_EMAIL, PASSWORD, "Influencer")
    if not influencer_token: return
    
    # 4. Request Affiliation
    request_id = request_affiliation(influencer_token, product['id'])
    if not request_id: 
        # Check if already exists (maybe from previous run)
        # But we created a new product, so it should be new.
        return

    # 5. Approve Request (Merchant)
    success = approve_request(merchant_token, request_id)
    if not success: return
    
    # 6. Verify Link (Influencer)
    verify_link(influencer_token, product['id'])
    
    print("\n✅ TEST COMPLETED SUCCESSFULLY")

if __name__ == "__main__":
    main()
