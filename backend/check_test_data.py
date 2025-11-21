"""
Vérification des données de test pour tous les dashboards
"""
from supabase_client import supabase

print("=" * 60)
print("VÉRIFICATION DES DONNÉES DE TEST")
print("=" * 60)

# 1. Utilisateurs
print("\n1. UTILISATEURS:")
users_result = supabase.table('users').select('id, email, role, status').execute()
users = users_result.data or []
print(f"   Total: {len(users)} utilisateurs")

roles = {}
for u in users:
    role = u.get('role', 'unknown')
    roles[role] = roles.get(role, 0) + 1

for role, count in sorted(roles.items()):
    print(f"   - {role}: {count}")

# 2. Produits
print("\n2. PRODUITS:")
products_result = supabase.table('products').select('id, name, price, merchant_id').execute()
products = products_result.data or []
print(f"   Total: {len(products)} produits")
if products:
    print(f"   Prix moyen: {sum(float(p.get('price', 0)) for p in products) / len(products):.2f} MAD")

# 3. Tracking Links
print("\n3. TRACKING LINKS:")
links_result = supabase.table('tracking_links').select('id, influencer_id, product_id').execute()
links = links_result.data or []
print(f"   Total: {len(links)} liens de tracking")

# 4. Conversions
print("\n4. CONVERSIONS:")
conversions_result = supabase.table('conversions').select('id, status, commission_amount').execute()
conversions = conversions_result.data or []
print(f"   Total: {len(conversions)} conversions")
if conversions:
    completed = [c for c in conversions if c.get('status') == 'completed']
    print(f"   Complétées: {len(completed)}")
    total_commission = sum(float(c.get('commission_amount', 0)) for c in completed)
    print(f"   Commissions totales: {total_commission:.2f} MAD")

# 5. Abonnements
print("\n5. ABONNEMENTS:")
subs_result = supabase.table('subscriptions').select('id, user_id, status').execute()
subs = subs_result.data or []
print(f"   Total: {len(subs)} abonnements")
if subs:
    active = [s for s in subs if s.get('status') == 'active']
    print(f"   Actifs: {len(active)}")

# 6. Leads Commerciaux
print("\n6. LEADS COMMERCIAUX:")
try:
    leads_result = supabase.table('commercial_leads').select('id, status').execute()
    leads = leads_result.data or []
    print(f"   Total: {len(leads)} leads")
except Exception as e:
    print(f"   ⚠️ Table commercial_leads non disponible: {e}")

# 7. Invitations
print("\n7. INVITATIONS:")
try:
    invitations_result = supabase.table('invitations').select('id, status').execute()
    invitations = invitations_result.data or []
    print(f"   Total: {len(invitations)} invitations")
except Exception as e:
    print(f"   ⚠️ Table invitations non disponible")

# 8. Collaboration Requests
print("\n8. DEMANDES DE COLLABORATION:")
try:
    collab_result = supabase.table('collaboration_requests').select('id, status').execute()
    collabs = collab_result.data or []
    print(f"   Total: {len(collabs)} demandes")
except Exception as e:
    print(f"   ⚠️ Table collaboration_requests non disponible")

print("\n" + "=" * 60)
print("RÉSUMÉ PAR DASHBOARD")
print("=" * 60)

# Dashboard Admin
admin_count = roles.get('admin', 0)
print(f"\n📊 DASHBOARD ADMIN:")
print(f"   Utilisateurs admin: {admin_count}")
print(f"   Total merchants: {roles.get('merchant', 0)}")
print(f"   Total influencers: {roles.get('influencer', 0)}")
print(f"   Total commercials: {roles.get('commercial', 0)}")
print(f"   Produits: {len(products)}")
print(f"   Status: {'✅ Données complètes' if admin_count > 0 and len(products) > 0 else '⚠️ Données manquantes'}")

# Dashboard Merchant
merchant_count = roles.get('merchant', 0)
print(f"\n🏪 DASHBOARD MERCHANT:")
print(f"   Comptes merchants: {merchant_count}")
print(f"   Produits disponibles: {len(products)}")
print(f"   Tracking links: {len(links)}")
print(f"   Status: {'✅ Données complètes' if merchant_count > 0 else '⚠️ Pas de merchant'}")

# Dashboard Influenceur
influencer_count = roles.get('influencer', 0)
print(f"\n👤 DASHBOARD INFLUENCEUR:")
print(f"   Comptes influenceurs: {influencer_count}")
print(f"   Liens tracking: {len(links)}")
print(f"   Conversions: {len(conversions)}")
status_inf = "✅ Données complètes" if influencer_count > 0 else "⚠️ Pas d'influenceur"
print(f"   Status: {status_inf}")

# Dashboard Commercial
commercial_count = roles.get('commercial', 0)
print(f"\n💼 DASHBOARD COMMERCIAL:")
print(f"   Comptes commerciaux: {commercial_count}")
leads_count = len(leads) if 'leads' in locals() else 'N/A'
print(f"   Leads: {leads_count}")
status_com = "✅ Données complètes" if commercial_count > 0 else "⚠️ Pas de commercial"
print(f"   Status: {status_com}")

print("\n" + "=" * 60)
