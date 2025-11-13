"""Mettre à jour les plans d'abonnement selon les boutons de connexion rapide"""
from supabase_client import supabase
from utils.logger import logger

# Mapping des comptes avec leurs vrais plans
comptes_plans = {
    # Influenceurs
    "hassan.oudrhiri@getyourshare.com": "starter",
    "sarah.benali@getyourshare.com": "professional",
    "karim.benjelloun@getyourshare.com": "premium",
    
    # Marchands
    "boutique.maroc@getyourshare.com": "starter",
    "luxury.crafts@getyourshare.com": "professional",
    "electromaroc@getyourshare.com": "premium",
    
    # Admin reste admin
    "admin@getyourshare.com": "premium",
    "sofia.chakir@getyourshare.com": "premium"
}

logger.info("\n" + "="*70)
logger.info("MISE À JOUR DES PLANS D'ABONNEMENT")
logger.info("="*70 + "\n")

for email, plan in comptes_plans.items():
    try:
        # Mettre à jour le plan
        result = supabase.table("users").update({
            "subscription_plan": plan
        }).eq("email", email).execute()
        
        if result.data:
            logger.info(f"✅ {email:45} → {plan.upper()}")
        else:
            logger.info(f"⚠️  {email:45} → Compte non trouvé")
    except Exception as e:
        logger.info(f"❌ {email:45} → Erreur: {e}")

logger.info("\n" + "="*70)
logger.info("✅ Mise à jour terminée")
logger.info("="*70)
logger.info("\nLes boutons de connexion rapide correspondent maintenant aux vrais plans!\n")
