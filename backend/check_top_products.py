"""
Script pour vérifier les produits et les données top-products
"""
import os
from dotenv import load_dotenv
from supabase import create_client

# Charger les variables d'environnement
load_dotenv()

# Créer le client Supabase
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')
supabase = create_client(supabase_url, supabase_key)

print("=" * 60)
print("🔍 DIAGNOSTIC TOP PRODUCTS")
print("=" * 60)

# 1. Vérifier les produits
print("\n📦 1. PRODUITS:")
try:
    products = supabase.table('products').select('id, name, price, category').limit(20).execute()
    print(f"   Nombre de produits: {len(products.data)}")
    for p in products.data[:10]:
        print(f"   - {p.get('name', 'N/A')[:30]} | {p.get('price', 0)}€ | {p.get('category', 'N/A')}")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# 2. Vérifier les conversions
print("\n📊 2. CONVERSIONS:")
try:
    conversions = supabase.table('conversions').select('id, product_id, order_total, created_at').limit(20).execute()
    print(f"   Nombre de conversions: {len(conversions.data)}")
    for c in conversions.data[:5]:
        print(f"   - Product ID: {c.get('product_id', 'N/A')} | Total: {c.get('order_total', 0)}€")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# 3. Vérifier les ventes
print("\n💰 3. SALES:")
try:
    sales = supabase.table('sales').select('id, product_id, amount, created_at').limit(20).execute()
    print(f"   Nombre de ventes: {len(sales.data)}")
    for s in sales.data[:5]:
        print(f"   - Product ID: {s.get('product_id', 'N/A')} | Montant: {s.get('amount', 0)}€")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# 4. Simuler ce que fait l'endpoint top-products
print("\n🎯 4. SIMULATION TOP PRODUCTS:")
try:
    # Récupérer les conversions avec produits
    conversions = supabase.table('conversions').select('product_id, order_total').execute()
    print(f"   Conversions trouvées: {len(conversions.data or [])}")
    
    # Grouper par produit
    products_revenue = {}
    products_count = {}
    for conversion in (conversions.data or []):
        product_id = conversion.get('product_id')
        if product_id:
            if product_id not in products_revenue:
                products_revenue[product_id] = 0
                products_count[product_id] = 0
            products_revenue[product_id] += float(conversion.get('order_total', 0))
            products_count[product_id] += 1
    
    print(f"   Produits avec revenus: {len(products_revenue)}")
    
    if products_revenue:
        # Récupérer infos des produits
        top_products = []
        for product_id, revenue in sorted(products_revenue.items(), key=lambda x: x[1], reverse=True)[:10]:
            try:
                product = supabase.table('products').select('id, name, price, category').eq('id', product_id).single().execute()
                if product.data:
                    top_products.append({
                        "id": product_id,
                        "name": product.data.get('name', 'Produit sans nom'),
                        "revenue": round(revenue, 2),
                        "conversions": products_count.get(product_id, 0),
                        "price": float(product.data.get('price', 0))
                    })
            except Exception as e:
                print(f"   ⚠️ Erreur produit {product_id}: {e}")
        
        if top_products:
            print("\n   ✅ TOP PRODUCTS CALCULÉS:")
            for i, p in enumerate(top_products[:5], 1):
                print(f"      {i}. {p['name'][:25]} | Revenue: {p['revenue']}€ | Conversions: {p['conversions']}")
        else:
            print("   ❌ Aucun produit dans les top products (problème de jointure)")
    else:
        print("   ❌ Aucune conversion avec product_id trouvée")
        print("   → L'endpoint retournera les données DEMO")

except Exception as e:
    print(f"   ❌ Erreur: {e}")

print("\n" + "=" * 60)
print("✅ DIAGNOSTIC TERMINÉ")
print("=" * 60)
