"""Vérifier les comptes de test dans Supabase"""
from supabase_client import supabase
from utils.logger import logger

logger.info("=== VÉRIFICATION DES COMPTES DE TEST ===\n")

# 1. Admin
logger.info("1. ADMIN:")
admin = supabase.table("users").select("*").eq("email", "admin@getyourshare.com").execute()
status = '✅ EXISTE' if admin.data else "❌ N'EXISTE PAS"
logger.info(f"   admin@getyourshare.com: {status}")
if admin.data:
    logger.info(f"   Role: {admin.data[0].get('role')}, Tier: {admin.data[0].get('tier')}")

# 2. Influenceurs
logger.info("\n2. INFLUENCEURS:")
influencers = [
    ("Hassan Oudrhiri", "hassan.oudrhiri@getyourshare.com", "STARTER"),
    ("Sarah Benali", "sarah.benali@getyourshare.com", "PRO"),
    ("Karim Benjelloun", "karim.benjelloun@getyourshare.com", "ENTERPRISE")
]

for name, email, tier in influencers:
    user = supabase.table("users").select("*").eq("email", email).execute()
    logger.info(f"   {name} ({email}):")
    status = '✅ EXISTE' if user.data else "❌ N'EXISTE PAS"
    logger.info(f"      {status}")
    if user.data:
        logger.info(f"      Role: {user.data[0].get('role')}, Tier: {user.data[0].get('tier')}")

# 3. Marchands
logger.info("\n3. MARCHANDS:")
merchants = [
    ("Boutique Maroc", "boutique.maroc@getyourshare.com", "STARTER"),
    ("Luxury Crafts", "luxury.crafts@getyourshare.com", "PRO"),
    ("ElectroMaroc", "electro.maroc@getyourshare.com", "ENTERPRISE")
]

for name, email, tier in merchants:
    user = supabase.table("users").select("*").eq("email", email).execute()
    logger.info(f"   {name} ({email}):")
    status = '✅ EXISTE' if user.data else "❌ N'EXISTE PAS"
    logger.info(f"      {status}")
    if user.data:
        logger.info(f"      Role: {user.data[0].get('role')}, Tier: {user.data[0].get('tier')}")

# 4. Commercial
logger.info("\n4. COMMERCIAL:")
commercial = supabase.table("users").select("*").eq("email", "sofia.chakir@getyourshare.com").execute()
logger.info(f"   Sofia Chakir (sofia.chakir@getyourshare.com):")
status = '✅ EXISTE' if commercial.data else "❌ N'EXISTE PAS"
logger.info(f"      {status}")
if commercial.data:
    logger.info(f"      Role: {commercial.data[0].get('role')}, Tier: {commercial.data[0].get('tier')}")

# Vérifier TOUS les utilisateurs
logger.info("\n\n=== TOUS LES UTILISATEURS DANS LA BASE ===")
all_users = supabase.table("users").select("*").execute()
logger.info(f"Total utilisateurs: {len(all_users.data)}\n")

if all_users.data:
    # Afficher les colonnes disponibles
    logger.info("Colonnes disponibles:", list(all_users.data[0].keys()))
    print()
    
    for user in all_users.data[:15]:  # Afficher les 15 premiers
        email = user.get('email', 'N/A')
        role = user.get('role', 'N/A')
        subscription = user.get('subscription_tier', 'N/A')
        company = user.get('company_name', 'N/A')
        logger.info(f"   - {email:40} | {role:12} | {subscription:12} | {company}")
else:
    logger.info("❌ AUCUN utilisateur dans la base de données !")
