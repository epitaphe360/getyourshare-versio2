"""
Script pour ajouter des produits de test pour le Live Shopping
"""
from config.supabase_config import get_supabase_client

def add_test_products():
    supabase = get_supabase_client()
    
    # Récupérer un merchant existant
    merchants = supabase.table('merchants').select('id').limit(1).execute()
    if not merchants.data:
        print("❌ Aucun merchant trouvé. Créez un merchant d'abord.")
        return
    
    merchant_id = merchants.data[0]['id']
    print(f"✅ Merchant trouvé: {merchant_id}")
    
    # Produits de test pour Live Shopping
    test_products = [
        {
            'merchant_id': merchant_id,
            'name': '🌸 Parfum Oriental Rose Luxe',
            'description': 'Parfum oriental aux notes de rose et d\'ambre. Idéal pour les soirées élégantes.',
            'price': 89.99,
            'category': 'parfums',
            'stock_quantity': 50,
            'image_url': 'https://images.unsplash.com/photo-1541643600914-78b084683601?w=500',
            'is_active': True
        },
        {
            'merchant_id': merchant_id,
            'name': '💄 Rouge à Lèvres Mat Velours',
            'description': 'Rouge à lèvres longue tenue, effet mat velouté. Disponible en 12 teintes.',
            'price': 24.99,
            'category': 'maquillage',
            'stock_quantity': 120,
            'image_url': 'https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=500',
            'is_active': True
        },
        {
            'merchant_id': merchant_id,
            'name': '👗 Robe Soirée Paillettes Or',
            'description': 'Robe de soirée élégante avec paillettes dorées. Parfaite pour les événements.',
            'price': 149.99,
            'category': 'mode',
            'stock_quantity': 25,
            'image_url': 'https://images.unsplash.com/photo-1566174053879-31528523f8ae?w=500',
            'is_active': True
        },
        {
            'merchant_id': merchant_id,
            'name': '⌚ Montre Connectée Sport Pro',
            'description': 'Montre intelligente avec suivi GPS, cardiofréquencemètre et 50+ modes sport.',
            'price': 199.99,
            'category': 'electronique',
            'stock_quantity': 40,
            'image_url': 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=500',
            'is_active': True
        },
        {
            'merchant_id': merchant_id,
            'name': '🎧 Écouteurs Sans Fil Premium',
            'description': 'Écouteurs Bluetooth avec réduction de bruit active et autonomie 30h.',
            'price': 129.99,
            'category': 'electronique',
            'stock_quantity': 60,
            'image_url': 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500',
            'is_active': True
        },
        {
            'merchant_id': merchant_id,
            'name': '💼 Sac à Main Cuir Véritable',
            'description': 'Sac en cuir italien fait main. Design intemporel et élégant.',
            'price': 299.99,
            'category': 'accessoires',
            'stock_quantity': 15,
            'image_url': 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=500',
            'is_active': True
        },
        {
            'merchant_id': merchant_id,
            'name': '👟 Baskets Running Ultra Confort',
            'description': 'Chaussures de sport avec technologie d\'amorti avancée.',
            'price': 89.99,
            'category': 'sport',
            'stock_quantity': 80,
            'image_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500',
            'is_active': True
        },
        {
            'merchant_id': merchant_id,
            'name': '🧴 Sérum Anti-Âge Vitamine C',
            'description': 'Sérum facial enrichi en vitamine C. Résultats visibles en 2 semaines.',
            'price': 44.99,
            'category': 'beaute',
            'stock_quantity': 100,
            'image_url': 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=500',
            'is_active': True
        }
    ]
    
    # Vérifier si des produits existent déjà
    existing = supabase.table('products').select('id').limit(1).execute()
    
    if existing.data:
        print(f"ℹ️  {len(existing.data)} produit(s) déjà présent(s) dans la base.")
        response = input("Voulez-vous ajouter quand même les produits de test? (o/n): ")
        if response.lower() != 'o':
            print("⏭️  Annulé.")
            return
    
    # Insérer les produits
    print("\n🔄 Ajout des produits de test...")
    
    for i, product in enumerate(test_products, 1):
        try:
            result = supabase.table('products').insert(product).execute()
            print(f"  ✅ [{i}/{len(test_products)}] {product['name']} - {product['price']}€")
        except Exception as e:
            print(f"  ❌ [{i}/{len(test_products)}] Erreur: {e}")
    
    # Vérifier le nombre total de produits
    total = supabase.table('products').select('id', count='exact').execute()
    print(f"\n✅ Total produits dans la base: {total.count}")
    print("\n🎉 Produits de test ajoutés avec succès!")
    print("💡 Vous pouvez maintenant créer des Lives Shopping avec ces produits.")

if __name__ == "__main__":
    add_test_products()
