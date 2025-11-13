"""Vérifier les plans d'abonnement des comptes de test"""
from supabase_client import supabase
from utils.logger import logger

comptes_test = [
    # Influenceurs
    "hassan.oudrhiri@getyourshare.com",
    "sarah.benali@getyourshare.com", 
    "karim.benjelloun@getyourshare.com",
    # Marchands
    "boutique.maroc@getyourshare.com",
    "luxury.crafts@getyourshare.com",
    "electromaroc@getyourshare.com",
    # Commercial
    "sofia.chakir@getyourshare.com"
]

logger.info("\n" + "="*70)
logger.info("VÉRIFICATION DES PLANS D'ABONNEMENT")
logger.info("="*70 + "\n")

for email in comptes_test:
    result = supabase.table("users").select("email, role, subscription_plan").eq("email", email).execute()
    
    if result.data:
        user = result.data[0]
        plan = user.get("subscription_plan", "N/A")
        role = user.get("role", "N/A")
        logger.info(f"✅ {email}")
        logger.info(f"   Rôle: {role}")
        logger.info(f"   Plan: {plan}")
        print()
    else:
        logger.info(f"❌ {email} - NON TROUVÉ")
        print()
