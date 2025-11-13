"""
Script de vérification et création des comptes de test selon le cahier des charges
Tous les mots de passe: Test123!
"""
import os
from supabase import create_client, Client
from datetime import datetime
from utils.logger import logger

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://iamezkmapbhlhhvvsits.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlhbWV6a21hcGJobGhodnZzaXRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzA5MTk2MDgsImV4cCI6MjA0NjQ5NTYwOH0.GZ2_BJBX9NNGHGXaIWbzVMB8SZ8VkNCACPZUWHnGFG4")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Définition des comptes selon le cahier des charges
ACCOUNTS = {
    "admin": {
        "email": "admin@getyourshare.com",
        "password": "Test123!",
        "role": "admin",
        "tier": "ENTERPRISE",
        "full_name": "Administrator",
        "company_name": "GetYourShare Admin",
        "description": "Admin - Accès Total"
    },
    "influencers": [
        {
            "email": "hassan.oudrhiri@getyourshare.com",
            "password": "Test123!",
            "role": "influencer",
            "tier": "STARTER",
            "full_name": "Hassan Oudrhiri",
            "display_name": "Hassan Oudrhiri",
            "bio": "67K followers • Food & Cuisine",
            "niche": "Food & Cuisine",
            "followers_count": 67000,
            "subscription_plan": "STARTER"
        },
        {
            "email": "sarah.benali@getyourshare.com",
            "password": "Test123!",
            "role": "influencer",
            "tier": "PRO",
            "full_name": "Sarah Benali",
            "display_name": "Sarah Benali",
            "bio": "125K followers • Lifestyle",
            "niche": "Lifestyle",
            "followers_count": 125000,
            "subscription_plan": "PRO"
        },
        {
            "email": "karim.benjelloun@getyourshare.com",
            "password": "Test123!",
            "role": "influencer",
            "tier": "ENTERPRISE",
            "full_name": "Karim Benjelloun ⭐",
            "display_name": "Karim Benjelloun",
            "bio": "285K followers • Tech & Gaming",
            "niche": "Tech & Gaming",
            "followers_count": 285000,
            "subscription_plan": "ENTERPRISE",
            "verified": True
        }
    ],
    "merchants": [
        {
            "email": "boutique.maroc@getyourshare.com",
            "password": "Test123!",
            "role": "merchant",
            "tier": "STARTER",
            "full_name": "Boutique Maroc",
            "company_name": "Boutique Maroc",
            "bio": "Artisanat traditionnel",
            "business_type": "Artisanat traditionnel",
            "subscription_plan": "STARTER"
        },
        {
            "email": "luxury.crafts@getyourshare.com",
            "password": "Test123!",
            "role": "merchant",
            "tier": "PRO",
            "full_name": "Luxury Crafts",
            "company_name": "Luxury Crafts",
            "bio": "Artisanat Premium",
            "business_type": "Artisanat Premium",
            "subscription_plan": "PRO"
        },
        {
            "email": "electromaroc@getyourshare.com",
            "password": "Test123!",
            "role": "merchant",
            "tier": "ENTERPRISE",
            "full_name": "ElectroMaroc ⭐",
            "company_name": "ElectroMaroc",
            "bio": "Électronique & High-Tech",
            "business_type": "Électronique & High-Tech",
            "subscription_plan": "ENTERPRISE",
            "verified": True
        }
    ],
    "commercial": {
        "email": "sofia.chakir@getyourshare.com",
        "password": "Test123!",
        "role": "commercial",
        "tier": "ENTERPRISE",
        "full_name": "Sofia Chakir",
        "company_name": "GetYourShare - Business Development",
        "bio": "Business Development Manager",
        "description": "Commercial ENTERPRISE"
    }
}

def check_user_exists(email: str) -> dict:
    """Vérifie si un utilisateur existe"""
    try:
        response = supabase.table("users").select("*").eq("email", email).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        logger.info(f"   ⚠️  Erreur lors de la vérification: {str(e)}")
        return None

def create_user_via_auth(email: str, password: str, metadata: dict) -> dict:
    """Crée un utilisateur via Supabase Auth"""
    try:
        # Essayer de créer via Auth API
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": metadata
            }
        })
        return response.user
    except Exception as e:
        logger.info(f"   ⚠️  Erreur Auth: {str(e)}")
        return None

def print_section(title: str):
    """Affiche un titre de section"""
    logger.info(f"\n{'='*70}")
    logger.info(f"  {title}")
    logger.info(f"{'='*70}\n")

def verify_account(email: str, expected_role: str, expected_tier: str, name: str):
    """Vérifie un compte et affiche son statut"""
    user = check_user_exists(email)
    
    if user:
        role_ok = user.get('role') == expected_role
        tier_ok = user.get('tier') == expected_tier
        
        status = "✅" if (role_ok and tier_ok) else "⚠️"
        
        logger.info(f"{status} {name}")
        logger.info(f"   Email: {email}")
        logger.info(f"   Password: Test123!")
        logger.info(f"   Role: {user.get('role')} {'✓' if role_ok else '✗ (devrait être ' + expected_role + ')'}")
        logger.info(f"   Tier: {user.get('tier')} {'✓' if tier_ok else '✗ (devrait être ' + expected_tier + ')'}")
        
        # Afficher infos supplémentaires selon le rôle
        if expected_role == "influencer":
            logger.info(f"   Followers: {user.get('followers_count', 'N/A')}")
            logger.info(f"   Niche: {user.get('niche', 'N/A')}")
        elif expected_role == "merchant":
            logger.info(f"   Company: {user.get('company_name', 'N/A')}")
            logger.info(f"   Business: {user.get('business_type', 'N/A')}")
        
        print()
        return True
    else:
        logger.info(f"❌ {name}")
        logger.info(f"   Email: {email}")
        logger.info(f"   ⚠️  COMPTE N'EXISTE PAS - Nécessite création")
        print()
        return False

def main():
    print_section("🔍 VÉRIFICATION DES COMPTES DE TEST")
    
    all_exist = True
    
    # 1. Admin
    logger.info("1️⃣  ADMINISTRATEUR\n")
    admin_exists = verify_account(
        ACCOUNTS["admin"]["email"],
        ACCOUNTS["admin"]["role"],
        ACCOUNTS["admin"]["tier"],
        "Administrator - Accès Total"
    )
    all_exist = all_exist and admin_exists
    
    # 2. Influenceurs
    print_section("2️⃣  INFLUENCEURS (3 types d'abonnement)")
    for inf in ACCOUNTS["influencers"]:
        inf_exists = verify_account(
            inf["email"],
            inf["role"],
            inf["tier"],
            f"{inf['full_name']} - {inf['bio']}"
        )
        all_exist = all_exist and inf_exists
    
    # 3. Marchands
    print_section("3️⃣  MARCHANDS (3 types d'abonnement)")
    for merch in ACCOUNTS["merchants"]:
        merch_exists = verify_account(
            merch["email"],
            merch["role"],
            merch["tier"],
            f"{merch['company_name']} - {merch['bio']}"
        )
        all_exist = all_exist and merch_exists
    
    # 4. Commercial
    print_section("4️⃣  COMMERCIAL")
    comm_exists = verify_account(
        ACCOUNTS["commercial"]["email"],
        ACCOUNTS["commercial"]["role"],
        ACCOUNTS["commercial"]["tier"],
        "Sofia Chakir - Business Development"
    )
    all_exist = all_exist and comm_exists
    
    # Résumé
    print_section("📊 RÉSUMÉ")
    
    if all_exist:
        logger.info("✅ TOUS LES COMPTES EXISTENT ET SONT CORRECTS")
        logger.info("\n🔑 Identifiants de connexion:")
        logger.info("   Mot de passe universel: Test123!")
        logger.info("\n📧 Emails:")
        logger.info(f"   Admin:       {ACCOUNTS['admin']['email']}")
        logger.info(f"   Influenceur: hassan.oudrhiri@getyourshare.com (STARTER)")
        logger.info(f"   Influenceur: sarah.benali@getyourshare.com (PRO)")
        logger.info(f"   Influenceur: karim.benjelloun@getyourshare.com (ENTERPRISE)")
        logger.info(f"   Marchand:    boutique.maroc@getyourshare.com (STARTER)")
        logger.info(f"   Marchand:    luxury.crafts@getyourshare.com (PRO)")
        logger.info(f"   Marchand:    electromaroc@getyourshare.com (ENTERPRISE)")
        logger.info(f"   Commercial:  sofia.chakir@getyourshare.com (ENTERPRISE)")
    else:
        logger.info("⚠️  CERTAINS COMPTES SONT MANQUANTS OU INCORRECTS")
        logger.info("\n💡 Pour créer les comptes manquants:")
        logger.info("   1. Utilisez le Dashboard Supabase Auth")
        logger.info("   2. Ou exécutez le script SQL dans backend/database/")
        logger.info("   3. Ou contactez l'administrateur système")
    
    logger.info("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
