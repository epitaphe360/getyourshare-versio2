#!/usr/bin/env python3
"""
Vérifier que toutes les tables du script CLEAN_ALL_DATA.sql existent
"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('backend/.env')

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

# Liste des tables dans CLEAN_ALL_DATA.sql
tables_requises = [
    'notifications', 'tracking_events', 'tracking_links', 'transactions',
    'kyc_verifications', 'campaign_influencers', 'campaigns', 'leads',
    'trust_scores', 'payment_accounts', 'payout_preferences', 'invoices',
    'webhook_logs', 'webhooks', 'api_keys', 'rate_limits', 'data_exports',
    'security_events', 'promotions', 'commercial_objectives', 'referral_codes',
    'live_streams', 'user_badges', 'disputes', 'workspace_comments',
    'workspace_members', 'workspaces', 'integration_sync_logs', 'integrations',
    'social_media_accounts', 'social_media_publications', 'product_reviews',
    'qr_scan_events', 'nfc_tap_events', 'offline_actions', 'report_runs',
    'custom_reports', 'content_templates', 'media_library', 'seo_metadata',
    'user_2fa', 'user_sessions', 'sales_assignments', 'affiliation_requests',
    'analytics_reports', 'support_tickets', 'payment_integrations',
    'subscriptions', 'email_campaigns', 'sms_campaigns', 'product_collections',
    'wishlists', 'shipments', 'warehouses', 'coupons', 'conversations', 'events'
]

print("🔍 Vérification des tables dans Supabase...\n")

tables_existantes = []
tables_manquantes = []

for table in tables_requises:
    try:
        # Tenter de faire un SELECT sur la table
        result = supabase.table(table).select("*").limit(1).execute()
        tables_existantes.append(table)
        print(f"✅ {table}")
    except Exception as e:
        if '404' in str(e) or 'not found' in str(e).lower():
            tables_manquantes.append(table)
            print(f"❌ {table} - TABLE MANQUANTE")
        else:
            # Peut exister mais avoir une erreur de permissions
            tables_existantes.append(table)
            print(f"⚠️  {table} - Existe mais erreur: {str(e)[:50]}")

print(f"\n{'='*60}")
print(f"📊 RÉSUMÉ:")
print(f"   ✅ Tables existantes: {len(tables_existantes)}/{len(tables_requises)}")
print(f"   ❌ Tables manquantes: {len(tables_manquantes)}/{len(tables_requises)}")

if tables_manquantes:
    print(f"\n⚠️  TABLES MANQUANTES:")
    for table in tables_manquantes:
        print(f"   - {table}")
    print(f"\n❌ Vous devez créer ces tables avant de lancer le test!")
else:
    print(f"\n🎉 TOUTES LES TABLES EXISTENT! Vous pouvez lancer le test!")

print(f"{'='*60}")
