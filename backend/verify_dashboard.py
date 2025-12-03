#!/usr/bin/env python3
"""Vérification des données du dashboard"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

print("=" * 70)
print("VÉRIFICATION DONNÉES DASHBOARD")
print("=" * 70)

# Services
services = supabase.table('services').select('id', count='exact', head=True).execute()
print(f"\n📦 Services: {services.count}")

# Leads
leads = supabase.table('leads').select('id', count='exact', head=True).execute()
print(f"📋 Leads: {leads.count}")

# Commission plateforme (dernières 24h)
from datetime import datetime, timedelta
yesterday = (datetime.now() - timedelta(days=1)).isoformat()
transactions = supabase.table('transactions')\
    .select('amount, platform_commission, commission_amount')\
    .eq('status', 'completed')\
    .gte('created_at', yesterday)\
    .execute()

total_commission = sum(float(t.get('platform_commission', 0) or t.get('commission_amount', 0)) for t in transactions.data)
print(f"💰 Commission plateforme (24h): {total_commission:.2f} MAD")

# Utilisateurs actifs
users = supabase.table('users')\
    .select('id', count='exact', head=True)\
    .gte('last_login', yesterday)\
    .execute()
print(f"👥 Utilisateurs actifs (24h): {users.count}")

print("\n✅ Le dashboard devrait maintenant afficher:")
print(f"   - Services: {services.count}")
print(f"   - Leads: {leads.count}")
print(f"   - Commission: {total_commission:.2f} MAD")
print(f"   - Utilisateurs actifs: {users.count}")
print("=" * 70)
