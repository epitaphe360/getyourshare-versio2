import os
import sys
from datetime import datetime, timedelta

# Add backend directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_client import get_supabase_client

def insert_mock_data():
    supabase = get_supabase_client()
    print("Connected to Supabase")

    # 1. Create Merchants
    merchants_data = [
        {"email": "techstore@example.com", "full_name": "TechStore", "role": "merchant"},
        {"email": "zenlife@example.com", "full_name": "ZenLife", "role": "merchant"},
        {"email": "audioworld@example.com", "full_name": "AudioWorld", "role": "merchant"}
    ]

    merchants = {}

    # Try to find existing merchants first
    print("Checking for existing merchants...")
    res = supabase.table('users').select('id, full_name').eq('role', 'merchant').limit(10).execute()
    existing_merchants = res.data
    
    if existing_merchants:
        print(f"Found {len(existing_merchants)} existing merchants.")
        # Use existing merchants cyclically
        merchants['TechStore'] = existing_merchants[0]['id']
        merchants['ZenLife'] = existing_merchants[1 % len(existing_merchants)]['id']
        merchants['AudioWorld'] = existing_merchants[2 % len(existing_merchants)]['id']
    else:
        print("No merchants found. Trying to find ANY user to act as merchant...")
        res = supabase.table('users').select('id').limit(1).execute()
        if res.data:
            user_id = res.data[0]['id']
            merchants['TechStore'] = user_id
            merchants['ZenLife'] = user_id
            merchants['AudioWorld'] = user_id
        else:
            print("CRITICAL: No users found in database. Cannot create products.")
            return

    # 2. Create Products
    products_data = [
        {
            "name": "Montre Connectée Pro",
            "merchant_id": merchants['TechStore'],
            "price": 299.99,
            "category": "Electronics",
            "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=300&q=80",
            "commission_rate": 15.0,
            "description": "Une montre connectée haute performance."
        },
        {
            "name": "Kit Yoga Premium",
            "merchant_id": merchants['ZenLife'],
            "price": 89.99,
            "category": "Sports",
            "image_url": "https://images.unsplash.com/photo-1545205597-3d9d02c29597?auto=format&fit=crop&w=300&q=80",
            "commission_rate": 28.0,
            "description": "Tout ce qu'il faut pour le yoga."
        },
        {
            "name": "Écouteurs Sans Fil",
            "merchant_id": merchants['AudioWorld'],
            "price": 59.99,
            "category": "Audio",
            "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=300&q=80",
            "commission_rate": 25.0,
            "description": "Son haute fidélité sans fil."
        }
    ]

    created_products = {}

    for p_data in products_data:
        # Check if product exists
        res = supabase.table('products').select('id').eq('name', p_data['name']).execute()
        if res.data:
            created_products[p_data['name']] = res.data[0]['id']
            print(f"Product {p_data['name']} exists: {created_products[p_data['name']]}")
        else:
            print(f"Creating product {p_data['name']}...")
            try:
                res = supabase.table('products').insert(p_data).execute()
                if res.data:
                    created_products[p_data['name']] = res.data[0]['id']
                else:
                    print(f"Failed to create product {p_data['name']}")
            except Exception as e:
                print(f"Error creating product {p_data['name']}: {e}")

    # 3. Create Recommendations for Influencers
    # Get all influencers and admins
    res = supabase.table('users').select('id').in_('role', ['influencer', 'admin']).execute()
    influencers = res.data
    print(f"Found {len(influencers)} influencers/admins to assign recommendations to.")

    recommendations_data = [
        {
            "product_name": "Montre Connectée Pro",
            "match_score": 98,
            "match_reasons": ["Correspond à votre audience tech et sport"],
            "is_active": True,
            "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
        },
        {
            "product_name": "Kit Yoga Premium",
            "match_score": 92,
            "match_reasons": ["Tendance forte chez vos followers féminins"],
            "is_active": True,
            "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
        },
        {
            "product_name": "Écouteurs Sans Fil",
            "match_score": 88,
            "match_reasons": ["Produit complémentaire à vos dernières ventes"],
            "is_active": True,
            "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
    ]

    for user in influencers:
        user_id = user['id']
        for rec_data in recommendations_data:
            product_id = created_products.get(rec_data['product_name'])
            if not product_id:
                continue
            
            # Check if recommendation exists
            res = supabase.table('product_recommendations').select('id')\
                .eq('influencer_id', user_id)\
                .eq('product_id', product_id)\
                .execute()
            
            if not res.data:
                print(f"Creating recommendation for user {user_id} - {rec_data['product_name']}")
                new_rec = {
                    "influencer_id": user_id,
                    "product_id": product_id,
                    "match_score": rec_data['match_score'],
                    "match_reasons": rec_data['match_reasons'],
                    "is_active": rec_data['is_active'],
                    "expires_at": rec_data['expires_at']
                }
                try:
                    supabase.table('product_recommendations').insert(new_rec).execute()
                except Exception as e:
                    print(f"Error creating recommendation: {e}")
            else:
                print(f"Recommendation already exists for user {user_id} - {rec_data['product_name']}")

if __name__ == "__main__":
    insert_mock_data()
