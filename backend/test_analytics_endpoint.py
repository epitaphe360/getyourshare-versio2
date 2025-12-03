#!/usr/bin/env python3
"""Test endpoint analytics"""

import requests

try:
    response = requests.get('http://localhost:5000/api/analytics/overview', timeout=5)
    
    if response.status_code == 200:
        data = response.json()
        print("=" * 70)
        print("✅ RÉSULTAT ENDPOINT /api/analytics/overview")
        print("=" * 70)
        print(f"📦 Services: {data.get('total_services', 0)}")
        print(f"📋 Leads: {data.get('total_leads', 0)}")
        print(f"💰 Commission plateforme: {data.get('platform_commission', 0)} MAD")
        print(f"👥 Utilisateurs actifs (24h): {data.get('active_users_24h', 0)}")
        print(f"💵 Revenus totaux: {data.get('total_revenue', 0)} MAD")
        print(f"🎯 Campagnes: {data.get('total_campaigns', 0)}")
        print("=" * 70)
    else:
        print(f"❌ Erreur {response.status_code}: {response.text}")
        
except Exception as e:
    print(f"❌ Erreur connexion: {e}")
    print("⚠️  Le serveur est-il démarré sur http://localhost:5000 ?")
