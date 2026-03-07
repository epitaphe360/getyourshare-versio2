import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajouter le backend au path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from supabase_client import supabase_admin as supabase
from datetime import datetime, timedelta

def test_analytics_endpoint():
    """Tester toutes les requêtes de l'endpoint analytics"""
    print("🔍 Test des requêtes analytics...\n")
    
    errors = []
    
    # Test 1: Users count
    try:
        merchants_count = supabase.table("users").select("id", count="exact", head=True).eq("role", "merchant").execute()
        print(f"✅ Merchants count: {merchants_count.count}")
    except Exception as e:
        errors.append(f"❌ Merchants count: {e}")
        print(f"❌ Merchants count: {e}")
    
    try:
        influencers_count = supabase.table("users").select("id", count="exact", head=True).eq("role", "influencer").execute()
        print(f"✅ Influencers count: {influencers_count.count}")
    except Exception as e:
        errors.append(f"❌ Influencers count: {e}")
        print(f"❌ Influencers count: {e}")
    
    try:
        commercials_count = supabase.table("users").select("id", count="exact", head=True).eq("role", "commercial").execute()
        print(f"✅ Commercials count: {commercials_count.count}")
    except Exception as e:
        errors.append(f"❌ Commercials count: {e}")
        print(f"❌ Commercials count: {e}")
    
    # Test 2: Active users
    try:
        yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
        active_users_count = supabase.table("users").select("id", count="exact", head=True).gt("last_login", yesterday).execute()
        print(f"✅ Active users 24h: {active_users_count.count}")
    except Exception as e:
        errors.append(f"❌ Active users: {e}")
        print(f"❌ Active users: {e}")
    
    # Test 3: Products
    try:
        products_result = supabase.table("products").select("id", count="exact", head=True).execute()
        print(f"✅ Products count: {products_result.count}")
    except Exception as e:
        errors.append(f"❌ Products: {e}")
        print(f"❌ Products: {e}")
    
    # Test 4: Services
    try:
        services_result = supabase.table("services").select("id", count="exact", head=True).execute()
        print(f"✅ Services count: {services_result.count}")
    except Exception as e:
        errors.append(f"❌ Services: {e}")
        print(f"❌ Services: {e}")
    
    # Test 5: Campaigns
    try:
        campaigns_result = supabase.table("campaigns").select("id", count="exact", head=True).execute()
        print(f"✅ Campaigns count: {campaigns_result.count}")
    except Exception as e:
        errors.append(f"❌ Campaigns: {e}")
        print(f"❌ Campaigns: {e}")
    
    # Test 6: Sales
    try:
        sales_result = supabase.table("sales").select("amount, platform_commission, commission_amount").eq("status", "completed").execute()
        print(f"✅ Sales count: {len(sales_result.data or [])}")
    except Exception as e:
        errors.append(f"❌ Sales: {e}")
        print(f"❌ Sales: {e}")
    
    # Test 7: Commissions
    try:
        commissions_result = supabase.table("commissions").select("amount").execute()
        print(f"✅ Commissions count: {len(commissions_result.data or [])}")
    except Exception as e:
        errors.append(f"❌ Commissions: {e}")
        print(f"❌ Commissions: {e}")
    
    # Test 8: Payouts
    try:
        payouts_result = supabase.table("payouts").select("amount").eq("status", "pending").execute()
        print(f"✅ Pending payouts: {len(payouts_result.data or [])}")
    except Exception as e:
        errors.append(f"❌ Payouts: {e}")
        print(f"❌ Payouts: {e}")
    
    # Test 9: Clicks
    try:
        clicks_result = supabase.table("clicks").select("id", count="exact", head=True).execute()
        print(f"✅ Clicks count: {clicks_result.count}")
    except Exception as e:
        errors.append(f"❌ Clicks: {e}")
        print(f"❌ Clicks: {e}")
    
    # Test 10: Conversions
    try:
        conversions_result = supabase.table("conversions").select("id", count="exact", head=True).execute()
        print(f"✅ Conversions count: {conversions_result.count}")
    except Exception as e:
        errors.append(f"❌ Conversions: {e}")
        print(f"❌ Conversions: {e}")
    
    # Test 11: Subscriptions
    try:
        subscriptions_result = supabase.table("subscriptions").select("id, plan_id", count="exact").in_("status", ["active", "trialing"]).execute()
        print(f"✅ Active subscriptions: {subscriptions_result.count}")
    except Exception as e:
        errors.append(f"❌ Subscriptions: {e}")
        print(f"❌ Subscriptions: {e}")
    
    # Test 12: Subscription plans
    try:
        plans_result = supabase.table("subscription_plans").select("id, price").execute()
        print(f"✅ Subscription plans: {len(plans_result.data or [])}")
    except Exception as e:
        errors.append(f"❌ Subscription plans: {e}")
        print(f"❌ Subscription plans: {e}")
    
    print("\n" + "="*50)
    if errors:
        print(f"❌ {len(errors)} erreur(s) trouvée(s):")
        for err in errors:
            print(f"  - {err}")
    else:
        print("✅ Toutes les requêtes ont réussi!")
    
    return len(errors) == 0

if __name__ == "__main__":
    test_analytics_endpoint()
