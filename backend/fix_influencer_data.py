"""
Script pour corriger les données des influenceurs et ajouter des données de test réalistes
"""
from supabase_client import supabase
from datetime import datetime, timedelta
import random

print("🔍 Vérification des données actuelles...")

# 1. Récupérer tous les influenceurs
influencers = supabase.table('users').select('*').eq('role', 'influencer').execute()
print(f"\n✅ {len(influencers.data)} influenceurs trouvés")

# 2. Récupérer tous les marchands
merchants = supabase.table('users').select('*').eq('role', 'merchant').execute()
print(f"✅ {len(merchants.data)} marchands trouvés")

# 3. Récupérer tous les produits
products = supabase.table('products').select('*').execute()
print(f"✅ {len(products.data)} produits trouvés")

# 4. Vérifier les liens de tracking existants
existing_links = supabase.table('tracking_links').select('*').execute()
print(f"✅ {len(existing_links.data)} liens de tracking existants")

# 5. Vérifier les conversions existantes
existing_conversions = supabase.table('conversions').select('*').execute()
print(f"✅ {len(existing_conversions.data)} conversions existantes")

print("\n" + "="*60)
print("🔧 Création de données de test réalistes...")
print("="*60)

# Supprimer les anciennes conversions et liens pour recommencer proprement
print("\n🧹 Nettoyage des anciennes données...")
supabase.table('conversions').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
supabase.table('tracking_links').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()

# Créer des liens de tracking pour chaque influenceur
links_created = 0
conversions_created = 0

for influencer in influencers.data[:5]:  # Les 5 premiers influenceurs
    influencer_id = influencer['id']
    influencer_email = influencer['email']
    
    # Créer 3-5 liens par influenceur
    num_links = random.randint(3, 5)
    
    for i in range(num_links):
        # Sélectionner un produit aléatoire
        product = random.choice(products.data)
        merchant = random.choice(merchants.data)
        
        # Créer le lien de tracking
        unique_code = f"inf{influencer_id[:4]}{i}{random.randint(100, 999)}"
        
        link_data = {
            'influencer_id': influencer_id,
            'merchant_id': merchant['id'],
            'product_id': product['id'],
            'full_url': f"https://example.com/product/{product['id']}",
            'unique_code': unique_code,
            'short_url': f"https://gys.co/{unique_code}",
            'clicks': random.randint(50, 500),
            'conversions': random.randint(5, 50),
            'is_active': True,
            'created_at': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
        }
        
        link_result = supabase.table('tracking_links').insert(link_data).execute()
        links_created += 1
        
        if link_result.data:
            link_id = link_result.data[0]['id']
            
            # Créer 2-8 conversions par lien
            num_conversions = random.randint(2, 8)
            
            for j in range(num_conversions):
                sale_amount = round(random.uniform(20, 500), 2)
                commission_rate = product.get('commission_rate', 10)
                commission = round(sale_amount * commission_rate / 100, 2)
                
                conversion_data = {
                    'tracking_link_id': link_id,
                    'influencer_id': influencer_id,
                    'merchant_id': merchant['id'],
                    'product_id': product['id'],
                    'sale_amount': sale_amount,
                    'commission_amount': commission,
                    'commission_rate': commission_rate,
                    'status': random.choice(['pending', 'completed', 'completed', 'completed']),  # 75% complétées
                    'created_at': (datetime.now() - timedelta(days=random.randint(1, 25))).isoformat()
                }
                
                supabase.table('conversions').insert(conversion_data).execute()
                conversions_created += 1

print(f"\n✅ {links_created} liens de tracking créés")
print(f"✅ {conversions_created} conversions créées")

# Afficher un résumé par influenceur
print("\n" + "="*60)
print("📊 RÉSUMÉ PAR INFLUENCEUR")
print("="*60)

for influencer in influencers.data[:5]:
    influencer_id = influencer['id']
    influencer_email = influencer['email']
    
    # Compter les liens
    links = supabase.table('tracking_links').select('*').eq('influencer_id', influencer_id).execute()
    
    # Compter les conversions et calculer les gains
    conversions = supabase.table('conversions').select('*').eq('influencer_id', influencer_id).execute()
    
    total_earnings = sum(c['commission_amount'] for c in conversions.data if c.get('commission_amount'))
    total_clicks = sum(link['clicks'] for link in links.data if link.get('clicks'))
    
    print(f"\n👤 {influencer_email}")
    print(f"   📊 {len(links.data)} liens de tracking")
    print(f"   👆 {total_clicks} clics")
    print(f"   💰 {len(conversions.data)} conversions")
    print(f"   💵 {total_earnings:.2f} € de gains")

print("\n" + "="*60)
print("✅ Données de test créées avec succès!")
print("="*60)
