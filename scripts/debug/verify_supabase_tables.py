#!/usr/bin/env python3
"""
Script pour vérifier que toutes les tables Supabase nécessaires existent
"""
import os
from supabase import create_client

def check_supabase_tables():
    """Vérifie l'existence de toutes les tables"""
    
    # Configuration Supabase
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_KEY", "")
    
    if not supabase_url or not supabase_key:
        print("❌ ERREUR: Variables d'environnement SUPABASE_URL et SUPABASE_KEY non définies")
        print("\nDéfinissez-les dans votre .env:")
        print("SUPABASE_URL=https://votre-projet.supabase.co")
        print("SUPABASE_KEY=votre_clé_supabase")
        return
    
    supabase = create_client(supabase_url, supabase_key)
    
    # Liste complète des 91 tables de données (pas les vues)
    required_tables = [
        # Core
        'users', 'merchants', 'influencers',
        
        # Products & Services
        'products', 'services', 'product_categories',
        
        # Campaigns
        'campaigns', 'campaign_products', 'campaign_settings',
        
        # Tracking
        'tracking_links', 'trackable_links', 'conversions',
        'click_tracking', 'click_logs', 'tracking_events',
        
        # Sales & Commissions
        'sales', 'commissions', 'payouts',
        
        # Invitations & Collaborations
        'invitations', 'collaboration_requests', 'collaboration_invitations',
        'collaboration_history', 'influencer_agreements',
        
        # Affiliation
        'affiliation_requests', 'influencer_affiliation_requests',
        'merchant_affiliation_requests', 'affiliate_requests',
        'affiliation_requests_stats', 'affiliation_request_history', 'affiliate_links',
        
        # Subscriptions
        'subscription_plans', 'subscriptions', 'subscription_usage',
        'subscription_events', 'subscription_coupons',
        
        # Invoices & Payments
        'invoices', 'platform_invoices', 'invoice_line_items',
        'payments', 'payment_methods', 'payment_accounts', 'payment_transactions',
        
        # Leads
        'leads', 'sales_leads', 'lead_validation',
        'merchant_deposits', 'company_deposits', 'deposit_transactions',
        
        # Social Media
        'social_connections', 'social_media_connections',
        'social_media_accounts', 'social_media_publications', 'social_media_stats',
        
        # Admin Social
        'admin_social_posts', 'admin_social_post_templates',
        
        # Sales Representatives
        'sales_representatives', 'sales_activities', 'deals',
        'sales_deals', 'sales_targets', 'sales_commissions',
        
        # Messaging
        'conversations', 'messages', 'notifications',
        
        # Reviews
        'reviews', 'product_reviews',
        
        # Gamification
        'user_gamification', 'badges', 'missions', 'user_missions',
        
        # KYC
        'kyc_submissions', 'user_kyc_profile', 'user_kyc_documents',
        'kyc_verification_logs', 'trust_scores',
        
        # Gateway
        'gateway_transactions', 'gateway_statistics',
        
        # Team
        'team_members', 'team_invitations', 'company_settings',
        
        # Settings
        'platform_settings', 'settings',
        
        # Contact & Moderation
        'contact_messages', 'moderation_queue',
        
        # Autres
        'swipe_history', 'user_sessions', 'webhook_logs',
        'translations', 'match_preferences', 'influencer_profiles_extended',
        'performance_metrics'
    ]
    
    print("🔍 VÉRIFICATION DES TABLES SUPABASE")
    print("="*60)
    
    existing_tables = []
    missing_tables = []
    
    for table in required_tables:
        try:
            # Essayer de faire une requête simple sur chaque table
            result = supabase.table(table).select("id").limit(1).execute()
            existing_tables.append(table)
            print(f"✅ {table}")
        except Exception as e:
            missing_tables.append(table)
            print(f"❌ {table} - MANQUANTE")
    
    print("\n" + "="*60)
    print(f"📊 RÉSULTAT")
    print("="*60)
    print(f"✅ Tables existantes: {len(existing_tables)}/{len(required_tables)}")
    print(f"❌ Tables manquantes: {len(missing_tables)}/{len(required_tables)}")
    
    if missing_tables:
        print("\n⚠️  TABLES MANQUANTES:")
        for table in missing_tables:
            print(f"   - {table}")
        print("\n💡 Exécutez le script CREATE_ALL_TABLES_COMPLETE.sql dans Supabase")
    else:
        print("\n🎉 TOUTES LES TABLES SONT PRÉSENTES!")
    
    # Vérifier les données par défaut
    print("\n" + "="*60)
    print("🔍 VÉRIFICATION DES DONNÉES PAR DÉFAUT")
    print("="*60)
    
    try:
        plans = supabase.table("subscription_plans").select("name").execute()
        print(f"✅ Plans d'abonnement: {len(plans.data)} trouvés")
        for plan in plans.data:
            print(f"   - {plan['name']}")
    except Exception as e:
        print(f"❌ Erreur lecture subscription_plans: {e}")
    
    try:
        categories = supabase.table("product_categories").select("name").execute()
        print(f"✅ Catégories de produits: {len(categories.data)} trouvées")
        for cat in categories.data:
            print(f"   - {cat['name']}")
    except Exception as e:
        print(f"❌ Erreur lecture product_categories: {e}")
    
    print("\n" + "="*60)
    print("✅ VÉRIFICATION TERMINÉE")
    print("="*60)

if __name__ == "__main__":
    check_supabase_tables()
