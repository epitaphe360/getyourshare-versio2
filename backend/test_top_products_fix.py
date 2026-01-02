"""
Test de la logique corrigée pour top-products
"""
from supabase_client import supabase

print("=" * 50)
print("TEST TOP PRODUCTS CORRIGÉ")
print("=" * 50)

# Récupérer les ventes
sales = supabase.table('sales').select('product_id, amount').execute()
print(f'\n📊 Nombre de ventes: {len(sales.data)}')

# Grouper par produit
products_revenue = {}
products_count = {}
for sale in (sales.data or []):
    product_id = sale.get('product_id')
    if product_id:
        if product_id not in products_revenue:
            products_revenue[product_id] = 0
            products_count[product_id] = 0
        products_revenue[product_id] += float(sale.get('amount', 0))
        products_count[product_id] += 1

print(f'📦 Produits avec revenus: {len(products_revenue)}')

# Construire top products
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
        top_products.append({
            "id": product_id,
            "name": f"Produit #{product_id[:8]}",
            "revenue": round(revenue, 2),
            "conversions": products_count.get(product_id, 0),
            "price": 0
        })

print(f'\n🎯 TOP {len(top_products)} PRODUITS:')
for i, p in enumerate(top_products, 1):
    print(f"  {i}. {p['name'][:35]} | Revenue: {p['revenue']}€ | Ventes: {p['conversions']}")

print("\n✅ Test terminé!")
