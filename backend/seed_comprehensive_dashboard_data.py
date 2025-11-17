#!/usr/bin/env python3
"""
Script de seed de données complètes pour les 3 dashboards
Génère des données de test réalistes pour Admin, Merchant et Influencer
"""

import os
import sys
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv
from supabase_client import supabase

load_dotenv()

def generate_seed_data():
    """Génère et insère des données de test complètes"""

    logger.info("="*70)
    logger.info("🌱 GÉNÉRATION DE DONNÉES DE TEST POUR LES DASHBOARDS")
    logger.info("="*70)
    print()

    try:
        # 1. Ajouter des produits supplémentaires
        logger.info("📦 Ajout de produits de test...")

        # Récupérer un merchant existant
        merchants = supabase.table("merchants").select("id").limit(1).execute()
        if not merchants.data:
            logger.info("❌ Aucun merchant trouvé. Créez d'abord des utilisateurs.")
            return False

        merchant_id = merchants.data[0]["id"]

        products = [
            {
                "name": "iPhone 15 Pro Max",
                "description": "Dernier iPhone avec puce A17",
                "price": 1299.00,
                "category": "Électronique",
                "merchant_id": merchant_id,
                "image_url": "https://picsum.photos/400/300?random=1",
                "commission_rate": 5.0,
                "is_active": True,
                "stock_quantity": 50,
                "total_views": random.randint(5000, 15000),
                "total_clicks": random.randint(500, 2000),
                "total_sales": random.randint(50, 200)
            },
            {
                "name": "MacBook Pro 16\" M3",
                "description": "MacBook avec puce M3 Max",
                "price": 2899.00,
                "category": "Électronique",
                "merchant_id": merchant_id,
                "image_url": "https://picsum.photos/400/300?random=2",
                "commission_rate": 4.5,
                "is_active": True,
                "stock_quantity": 30,
                "total_views": random.randint(8000, 18000),
                "total_clicks": random.randint(800, 2500),
                "total_sales": random.randint(30, 150)
            },
            {
                "name": "AirPods Pro 2",
                "description": "Écouteurs sans fil avec ANC",
                "price": 279.00,
                "category": "Électronique",
                "merchant_id": merchant_id,
                "image_url": "https://picsum.photos/400/300?random=3",
                "commission_rate": 6.0,
                "is_active": True,
                "stock_quantity": 100,
                "total_views": random.randint(10000, 25000),
                "total_clicks": random.randint(1500, 3500),
                "total_sales": random.randint(100, 300)
            },
            {
                "name": "Nike Air Max 2024",
                "description": "Sneakers dernière génération",
                "price": 169.00,
                "category": "Mode",
                "merchant_id": merchant_id,
                "image_url": "https://picsum.photos/400/300?random=4",
                "commission_rate": 8.0,
                "is_active": True,
                "stock_quantity": 200,
                "total_views": random.randint(15000, 30000),
                "total_clicks": random.randint(2000, 4000),
                "total_sales": random.randint(150, 400)
            },
            {
                "name": "PS5 Slim Digital",
                "description": "Console PlayStation 5 version Slim",
                "price": 449.00,
                "category": "Gaming",
                "merchant_id": merchant_id,
                "image_url": "https://picsum.photos/400/300?random=5",
                "commission_rate": 3.5,
                "is_active": True,
                "stock_quantity": 75,
                "total_views": random.randint(20000, 35000),
                "total_clicks": random.randint(3000, 5000),
                "total_sales": random.randint(80, 250)
            }
        ]

        # Insérer les produits
        for product in products:
            try:
                supabase.table("products").insert(product).execute()
                logger.info(f"  ✅ Produit ajouté: {product['name']}")
            except Exception as e:
                # Produit existe peut-être déjà, on continue
                logger.info(f"  ⚠️  {product['name']}: {str(e)[:50]}")

        print()

        # 2. Ajouter des influencers supplémentaires
        logger.info("👥 Ajout d'influencers de test...")

        influencers_data = [
            {
                "full_name": "Sophie Martin",
                "username": "sophie_lifestyle",
                "email": "sophie@influencer.com",
                "influencer_type": "Lifestyle",
                "total_followers": 125000,
                "engagement_rate": 4.8,
                "total_earnings": random.randint(15000, 35000),
                "total_clicks": random.randint(8000, 15000),
                "total_sales": random.randint(120, 280),
                "balance": random.randint(2000, 5000)
            },
            {
                "full_name": "Thomas Dubois",
                "username": "tech_thomas",
                "email": "thomas@tech.com",
                "influencer_type": "Tech",
                "total_followers": 89000,
                "engagement_rate": 5.2,
                "total_earnings": random.randint(18000, 40000),
                "total_clicks": random.randint(10000, 18000),
                "total_sales": random.randint(150, 320),
                "balance": random.randint(3000, 7000)
            },
            {
                "full_name": "Laura Benoit",
                "username": "fashion_laura",
                "email": "laura@fashion.com",
                "influencer_type": "Fashion",
                "total_followers": 210000,
                "engagement_rate": 6.1,
                "total_earnings": random.randint(25000, 55000),
                "total_clicks": random.randint(15000, 25000),
                "total_sales": random.randint(200, 450),
                "balance": random.randint(4000, 9000)
            }
        ]

        for inf_data in influencers_data:
            try:
                # Créer d'abord l'utilisateur
                from db_helpers import create_user, get_user_by_email

                existing = get_user_by_email(inf_data["email"])
                if not existing:
                    user = create_user(
                        email=inf_data["email"],
                        password="influencer123",
                        role="influencer"
                    )

                    if user:
                        # Créer l'influencer
                        influencer = {
                            "user_id": user["id"],
                            "full_name": inf_data["full_name"],
                            "username": inf_data["username"],
                            "influencer_type": inf_data["influencer_type"],
                            "total_followers": inf_data["total_followers"],
                            "engagement_rate": inf_data["engagement_rate"],
                            "total_earnings": inf_data["total_earnings"],
                            "total_clicks": inf_data["total_clicks"],
                            "total_sales": inf_data["total_sales"],
                            "balance": inf_data["balance"]
                        }
                        supabase.table("influencers").insert(influencer).execute()
                        logger.info(f"  ✅ Influencer ajouté: {inf_data['full_name']}")
                else:
                    logger.info(f"  ⚠️  {inf_data['full_name']} existe déjà")
            except Exception as e:
                logger.info(f"  ⚠️  Erreur {inf_data['full_name']}: {str(e)[:50]}")

        print()

        # 3. Générer des ventes pour les derniers 30 jours
        logger.info("💰 Génération de ventes historiques (30 jours)...")

        # Récupérer tous les produits
        all_products = supabase.table("products").select("id, price, merchant_id").execute()
        if not all_products.data:
            logger.info("  ⚠️  Aucun produit trouvé")
            return False

        # Récupérer tous les influencers
        all_influencers = supabase.table("influencers").select("id").execute()
        if not all_influencers.data:
            logger.info("  ⚠️  Aucun influencer trouvé")
            return False

        sales_generated = 0
        for day_offset in range(30):
            sale_date = datetime.now() - timedelta(days=day_offset)

            # Générer 5 à 15 ventes par jour
            num_sales = random.randint(5, 15)

            for _ in range(num_sales):
                product = random.choice(all_products.data)
                influencer = random.choice(all_influencers.data)

                amount = float(product["price"])
                commission = amount * 0.10  # 10% de commission

                sale_data = {
                    "product_id": product["id"],
                    "merchant_id": product["merchant_id"],
                    "influencer_id": influencer["id"],
                    "amount": amount,
                    "commission": commission,
                    "status": "completed",
                    "sale_timestamp": sale_date.isoformat()
                }

                try:
                    supabase.table("sales").insert(sale_data).execute()
                    sales_generated += 1
                except Exception as e:
                    pass  # Continue même en cas d'erreur

        logger.info(f"  ✅ {sales_generated} ventes générées sur 30 jours")
        print()

        # 4. Générer des clics
        logger.info("🖱️  Génération de clics...")

        # Récupérer tous les liens trackables
        trackable_links = supabase.table("trackable_links").select("id").execute()

        if trackable_links.data:
            clicks_generated = 0
            for day_offset in range(7):  # 7 derniers jours
                click_date = datetime.now() - timedelta(days=day_offset)

                # 50 à 150 clics par jour
                num_clicks = random.randint(50, 150)

                for _ in range(num_clicks):
                    link = random.choice(trackable_links.data)

                    click_data = {
                        "link_id": link["id"],
                        "ip_address": f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "referrer": random.choice(["facebook.com", "instagram.com", "twitter.com", "tiktok.com", "direct"]),
                        "country": "MA",
                        "city": random.choice(["Casablanca", "Rabat", "Marrakech", "Fès", "Tanger"]),
                        "device_type": random.choice(["mobile", "desktop", "tablet"]),
                        "clicked_at": click_date.isoformat()
                    }

                    try:
                        supabase.table("click_tracking").insert(click_data).execute()
                        clicks_generated += 1
                    except Exception:
                        pass

            logger.info(f"  ✅ {clicks_generated} clics générés")
        else:
            logger.info("  ⚠️  Aucun lien trackable trouvé, création de liens...")

            # Créer des liens trackables
            products = all_products.data[:5]  # 5 premiers produits
            influencers = all_influencers.data[:5]  # 5 premiers influencers

            import uuid
            for product in products:
                for influencer in influencers:
                    unique_code = str(uuid.uuid4())[:8]
                    link_data = {
                        "product_id": product["id"],
                        "influencer_id": influencer["id"],
                        "unique_code": unique_code,
                        "full_url": f"https://shareyoursales.com/track/{unique_code}",
                        "short_url": f"shs.io/{unique_code[:6]}",
                        "is_active": True
                    }
                    try:
                        supabase.table("trackable_links").insert(link_data).execute()
                    except Exception:
                        pass

            logger.info("  ✅ Liens trackables créés")

        print()

        # 5. Mettre à jour les stats des merchants
        logger.info("📊 Mise à jour des statistiques merchants...")

        for merchant_data in merchants.data:
            # Calculer les ventes totales
            sales = supabase.table("sales").select("amount").eq("merchant_id", merchant_data["id"]).eq("status", "completed").execute()
            total_sales = sum([float(s["amount"]) for s in sales.data]) if sales.data else 0

            # Compter les produits
            products_count = supabase.table("products").select("id", count="exact").eq("merchant_id", merchant_data["id"]).execute()

            update_data = {
                "total_sales": total_sales,
                "products_count": products_count.count if products_count else 0
            }

            supabase.table("merchants").update(update_data).eq("id", merchant_data["id"]).execute()
            logger.info(f"  ✅ Stats merchant mises à jour")

        print()
        logger.info("="*70)
        logger.info("✅ DONNÉES DE TEST GÉNÉRÉES AVEC SUCCÈS!")
        logger.info("="*70)
        print()
        logger.info("📈 Résumé:")
        logger.info(f"  • Produits: 5 nouveaux produits ajoutés")
        logger.info(f"  • Influencers: 3 nouveaux influencers")
        logger.info(f"  • Ventes: {sales_generated} ventes sur 30 jours")
        logger.info(f"  • Clics: Historique de 7 jours")
        print()
        logger.info("🎉 Vous pouvez maintenant tester les dashboards avec des données réalistes!")
        print()

        return True

    except Exception as e:
        logger.info(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        logger.info("\n🔍 Vérification de la connexion Supabase...")
        result = supabase.table("users").select("id").limit(1).execute()
        logger.info("✅ Connexion Supabase OK\n")

        success = generate_seed_data()

        if success:
            sys.exit(0)
        else:
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("\n\n❌ Opération annulée par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Erreur fatale: {e}")
        sys.exit(1)
