import os
from dotenv import load_dotenv
from supabase import create_client

# Load env vars
load_dotenv("backend/.env")

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("❌ Erreur: Impossible de charger les clés Supabase")
    exit(1)

supabase = create_client(url, key)

def check_plans_for_roles():
    print("🔍 Vérification des plans pour chaque rôle...\n")

    try:
        response = supabase.table("subscription_plans").select("*").execute()
        plans = response.data
        
        if not plans:
            print("⚠️ Aucun plan trouvé !")
            return

        # Categorize plans
        merchant_plans = []
        influencer_plans = []
        commercial_plans = []
        other_plans = []

        for p in plans:
            name = p.get('name', '').lower()
            code = p.get('code', '').lower()
            ptype = p.get('type', '').lower()
            
            # Logic to guess target audience based on name/code/type
            if 'influencer' in name or 'influencer' in code or 'influencer' in ptype:
                influencer_plans.append(p)
            elif 'commercial' in name or 'commercial' in code or 'commercial' in ptype:
                commercial_plans.append(p)
            elif 'marketplace' in name or 'marketplace' in code:
                # Marketplace is often for commercials/influencers in this context? 
                # Or maybe merchants? The docstring said "Marketplace: 99 MAD/mois (indépendant)"
                # Indépendant usually means influencer or commercial agent.
                commercial_plans.append(p) 
                influencer_plans.append(p) # Could be both?
            elif 'small' in name or 'medium' in name or 'large' in name or 'enterprise' in ptype:
                merchant_plans.append(p)
            else:
                other_plans.append(p)

        print(f"🛒 Plans Marchands ({len(merchant_plans)}):")
        for p in merchant_plans:
            print(f"   - {p['name']} ({p['price_mad']} MAD)")

        print(f"\n🤳 Plans Influenceurs ({len(influencer_plans)}):")
        for p in influencer_plans:
            print(f"   - {p['name']} ({p['price_mad']} MAD)")
            
        print(f"\n💼 Plans Commerciaux ({len(commercial_plans)}):")
        for p in commercial_plans:
            print(f"   - {p['name']} ({p['price_mad']} MAD)")

        print(f"\n❓ Autres Plans ({len(other_plans)}):")
        for p in other_plans:
            print(f"   - {p['name']} ({p['price_mad']} MAD)")

    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    check_plans_for_roles()
