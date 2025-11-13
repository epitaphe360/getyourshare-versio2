"""Vérifier et corriger les plans des commerciaux"""
from supabase_client import supabase
from utils.logger import logger

# Plans des commerciaux selon leurs emails
commerciaux = {
    "commercial.free@getyourshare.com": "free",
    "commercial.starter@getyourshare.com": "starter",
    "commercial.pro@getyourshare.com": "professional",
    "commercial.premium@getyourshare.com": "premium",
    "fatima.bennani@getyourshare.com": "starter",
    "youssef.alami@getyourshare.com": "professional"
}

logger.info("\n" + "="*70)
logger.info("CORRECTION DES PLANS DES COMMERCIAUX")
logger.info("="*70 + "\n")

for email, expected_plan in commerciaux.items():
    # Vérifier le plan actuel
    result = supabase.table("users").select("subscription_plan").eq("email", email).execute()
    
    if result.data:
        current_plan = result.data[0].get("subscription_plan")
        
        if current_plan != expected_plan:
            # Corriger
            supabase.table("users").update({"subscription_plan": expected_plan}).eq("email", email).execute()
            logger.info(f"✅ {email:45} {current_plan} → {expected_plan}")
        else:
            logger.info(f"✓  {email:45} {expected_plan} (OK)")
    else:
        logger.info(f"❌ {email:45} NON TROUVÉ")

logger.info("\n" + "="*70)
logger.info("✅ Vérification terminée")
logger.info("="*70 + "\n")
