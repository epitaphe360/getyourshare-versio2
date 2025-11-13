"""
Script pour importer les traductions statiques existantes dans la base de données
À exécuter une seule fois après la création de la table translations
"""

import sys
import os
import asyncio
from dotenv import load_dotenv

# Ajouter le répertoire frontend au path pour importer les traductions
frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'src')
sys.path.insert(0, frontend_path)

load_dotenv()

# Import Supabase
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.info("❌ SUPABASE_URL et SUPABASE_KEY doivent être configurés dans .env")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Import du service de traduction
from translation_service import TranslationService
from utils.logger import logger

# Traductions statiques (copié depuis les fichiers i18n)
TRANSLATIONS_FR = {
    # Navigation
    "nav_dashboard": "Tableau de Bord",
    "nav_marketplace": "Marketplace",
    "nav_products": "Produits",
    "nav_links": "Mes Liens",
    "nav_affiliates": "Affiliés",
    "nav_analytics": "Analytics",
    "nav_messages": "Messages",
    "nav_settings": "Paramètres",
    "nav_profile": "Profil",
    "nav_getting_started": "Getting Started",
    "nav_my_campaigns": "Mes Campagnes",
    "nav_my_products": "Mes Produits",
    "nav_my_affiliates": "Mes Affiliés",
    "nav_performance": "Performance",
    "nav_tracking": "Suivi",
    "nav_subscription": "Abonnement",
    "nav_news": "News & Newsletter",
    "nav_advertisers": "Annonceurs",
    "nav_campaigns": "Campagnes/Offres",
    "nav_moderation": "Modération IA",
    "nav_logs": "Logs",
    "nav_tracking_links": "Liens de Tracking",
    "nav_integrations": "Intégrations",
    "nav_platform_subscriptions": "Abonnements Plateforme",
    
    # Sous-menus Navigation
    "nav_list": "Liste",
    "nav_applications": "Demandes",
    "nav_payouts": "Paiements",
    "nav_coupons": "Coupons",
    "nav_conversions": "Conversions",
    "nav_reports": "Rapports",
    "nav_personal": "Personnel",
    "nav_security": "Sécurité",
    "nav_company": "Entreprise",
    "nav_registrations": "Inscriptions",
    "nav_billing": "Facturation",
    "nav_mlm_commissions": "Commissions MLM",
    "nav_leads": "Leads",
    "nav_lost_orders": "Commandes Perdues",
    "nav_balance_report": "Rapport de Solde",
    "nav_clicks": "Clics",
    "nav_postback": "Postback",
    "nav_audit": "Audit",
    "nav_webhooks": "Webhooks",
    "nav_platform": "Plateforme",
    "nav_registration": "Inscription",
    "nav_mlm": "MLM",
    "nav_traffic_sources": "Sources de Trafic",
    "nav_permissions": "Permissions",
    "nav_users": "Utilisateurs",
    "nav_smtp": "SMTP",
    "nav_emails": "Emails",
    "nav_white_label": "White Label",
    
    # Général
    "app_name": "ShareYourSales",
    "welcome": "Bienvenue",
    "loading": "Chargement...",
    "logout": "Déconnexion",
    "settings": "Paramètres",
}

TRANSLATIONS_EN = {
    # Navigation
    "nav_dashboard": "Dashboard",
    "nav_marketplace": "Marketplace",
    "nav_products": "Products",
    "nav_links": "My Links",
    "nav_affiliates": "Affiliates",
    "nav_analytics": "Analytics",
    "nav_messages": "Messages",
    "nav_settings": "Settings",
    "nav_profile": "Profile",
    "nav_getting_started": "Getting Started",
    "nav_my_campaigns": "My Campaigns",
    "nav_my_products": "My Products",
    "nav_my_affiliates": "My Affiliates",
    "nav_performance": "Performance",
    "nav_tracking": "Tracking",
    "nav_subscription": "Subscription",
    "nav_news": "News & Newsletter",
    "nav_advertisers": "Advertisers",
    "nav_campaigns": "Campaigns/Offers",
    "nav_moderation": "AI Moderation",
    "nav_logs": "Logs",
    "nav_tracking_links": "Tracking Links",
    "nav_integrations": "Integrations",
    "nav_platform_subscriptions": "Platform Subscriptions",
    
    # Sous-menus Navigation
    "nav_list": "List",
    "nav_applications": "Applications",
    "nav_payouts": "Payouts",
    "nav_coupons": "Coupons",
    "nav_conversions": "Conversions",
    "nav_reports": "Reports",
    "nav_personal": "Personal",
    "nav_security": "Security",
    "nav_company": "Company",
    "nav_registrations": "Registrations",
    "nav_billing": "Billing",
    "nav_mlm_commissions": "MLM Commissions",
    "nav_leads": "Leads",
    "nav_lost_orders": "Lost Orders",
    "nav_balance_report": "Balance Report",
    "nav_clicks": "Clicks",
    "nav_postback": "Postback",
    "nav_audit": "Audit",
    "nav_webhooks": "Webhooks",
    "nav_platform": "Platform",
    "nav_registration": "Registration",
    "nav_mlm": "MLM",
    "nav_traffic_sources": "Traffic Sources",
    "nav_permissions": "Permissions",
    "nav_users": "Users",
    "nav_smtp": "SMTP",
    "nav_emails": "Emails",
    "nav_white_label": "White Label",
    
    # Général
    "app_name": "ShareYourSales",
    "welcome": "Welcome",
    "loading": "Loading...",
    "logout": "Logout",
    "settings": "Settings",
}

async def import_all():
    """Import toutes les traductions"""
    
    translation_service = TranslationService(supabase)
    
    logger.info("🚀 Démarrage de l'import des traductions...")
    logger.info("=" * 60)
    
    # Import FR
    logger.info("\n📦 Import des traductions françaises...")
    count_fr = await translation_service.import_static_translations(
        TRANSLATIONS_FR,
        'fr'
    )
    logger.info(f"✅ {count_fr} traductions françaises importées")
    
    # Import EN
    logger.info("\n📦 Import des traductions anglaises...")
    count_en = await translation_service.import_static_translations(
        TRANSLATIONS_EN,
        'en'
    )
    logger.info(f"✅ {count_en} traductions anglaises importées")
    
    logger.info("\n" + "=" * 60)
    logger.info(f"✅ IMPORT TERMINÉ: {count_fr + count_en} traductions au total")
    logger.info("\n💡 Les traductions AR et Darija seront générées automatiquement")
    logger.info("   par OpenAI lors de la première utilisation.")
    logger.info("\n⚠️  N'oubliez pas de configurer OPENAI_API_KEY dans .env")

if __name__ == "__main__":
    asyncio.run(import_all())
