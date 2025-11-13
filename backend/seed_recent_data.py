"""
Script pour ajouter des données de test récentes (7 derniers jours)
Pour les graphiques "Évolution des Gains" et "Clics & Conversions"
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, timedelta
import random
from utils.logger import logger

# Charger les variables d'environnement
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Client Supabase avec droits admin
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

logger.info("=" * 80)
logger.info("📊 Ajout de données récentes pour les graphiques (7 derniers jours)")
logger.info("=" * 80)

# Récupérer les IDs existants
influencers_result = supabase.table("influencers").select("id,user_id").execute()
influencers = influencers_result.data

merchants_result = supabase.table("merchants").select("id").execute()
merchants = merchants_result.data

products_result = supabase.table("products").select("id").execute()
products = products_result.data

links_result = supabase.table("trackable_links").select("id,influencer_id,product_id").execute()
links = links_result.data

if not influencers or not merchants or not products or not links:
    logger.info("❌ Données de base manquantes. Exécutez d'abord seed_all_data.py")
    exit(1)

logger.info(f"📍 {len(influencers)} influencers trouvés")
logger.info(f"📍 {len(merchants)} merchants trouvés")
logger.info(f"📍 {len(products)} produits trouvés")
logger.info(f"📍 {len(links)} liens trouvés\n")

# ============================================
# CRÉER DES VENTES POUR LES 7 DERNIERS JOURS
# ============================================

logger.info("💰 Création de ventes récentes...")
logger.info("-" * 80)

today = datetime.now()
sales_created = 0

for day_offset in range(6, -1, -1):  # 7 derniers jours
    target_date = today - timedelta(days=day_offset)

    # 3 à 8 ventes par jour
    num_sales = random.randint(3, 8)

    for _ in range(num_sales):
        try:
            link = random.choice(links)
            merchant = random.choice(merchants)

            # Montant de la vente
            amount = round(random.uniform(50, 500), 2)

            # Commission influenceur (10-25%)
            commission_rate = random.uniform(10, 25)
            influencer_commission = round(amount * (commission_rate / 100), 2)

            # Commission plateforme (5%)
            platform_commission = round(amount * 0.05, 2)

            # Revenue merchant
            merchant_revenue = round(amount - influencer_commission - platform_commission, 2)

            # Timestamp aléatoire dans la journée
            random_hour = random.randint(8, 22)
            random_minute = random.randint(0, 59)
            sale_timestamp = target_date.replace(hour=random_hour, minute=random_minute)

            sale_data = {
                "link_id": link["id"],
                "product_id": link["product_id"],
                "influencer_id": link["influencer_id"],
                "merchant_id": merchant["id"],
                "customer_email": f"customer{random.randint(1000,9999)}@example.com",
                "customer_name": f"Client {random.randint(1,100)}",
                "quantity": random.randint(1, 3),
                "amount": amount,
                "currency": "EUR",
                "influencer_commission": influencer_commission,
                "platform_commission": platform_commission,
                "merchant_revenue": merchant_revenue,
                "status": "completed",
                "payment_status": "paid",
                "sale_timestamp": sale_timestamp.isoformat(),
                "created_at": sale_timestamp.isoformat(),
            }

            result = supabase.table("sales").insert(sale_data).execute()

            if result.data:
                sales_created += 1

        except Exception as e:
            logger.info(f"  ⚠️  Erreur vente: {str(e)}")

    logger.info(f"  ✅ {target_date.strftime('%d/%m')}: {num_sales} ventes créées")

logger.info(f"\n  📊 Total: {sales_created} ventes créées\n")

# ============================================
# CRÉER DES CLICS POUR LES 7 DERNIERS JOURS
# ============================================

logger.info("🖱️  Création de clics récents...")
logger.info("-" * 80)

clicks_created = 0

for day_offset in range(6, -1, -1):  # 7 derniers jours
    target_date = today - timedelta(days=day_offset)

    # 30 à 80 clics par jour
    num_clicks = random.randint(30, 80)

    for _ in range(num_clicks):
        try:
            link = random.choice(links)

            # Timestamp aléatoire dans la journée
            random_hour = random.randint(0, 23)
            random_minute = random.randint(0, 59)
            random_second = random.randint(0, 59)
            clicked_at = target_date.replace(
                hour=random_hour, minute=random_minute, second=random_second
            )

            click_data = {
                "link_id": link["id"],
                "ip_address": f"192.168.{random.randint(1,255)}.{random.randint(1,255)}",
                "user_agent": random.choice(
                    [
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                    ]
                ),
                "referrer": random.choice(
                    [
                        "https://instagram.com",
                        "https://facebook.com",
                        "https://twitter.com",
                        "https://tiktok.com",
                        None,
                    ]
                ),
                "country": random.choice(["FR", "BE", "CH", "CA"]),
                "city": random.choice(["Paris", "Lyon", "Marseille", "Lille", "Toulouse"]),
                "device_type": random.choice(["Mobile", "Desktop", "Tablet"]),
                "os": random.choice(["Windows", "iOS", "Android", "macOS"]),
                "browser": random.choice(["Chrome", "Safari", "Firefox", "Edge"]),
                "is_unique_visitor": random.choice([True, True, False]),
                "clicked_at": clicked_at.isoformat(),
            }

            result = supabase.table("click_tracking").insert(click_data).execute()

            if result.data:
                clicks_created += 1

        except Exception as e:
            if clicks_created == 0:
                logger.info(f"  ⚠️  Erreur clic: {str(e)}")

    logger.info(f"  ✅ {target_date.strftime('%d/%m')}: {num_clicks} clics créés")

logger.info(f"\n  📊 Total: {clicks_created} clics créés\n")

# ============================================
# STATISTIQUES FINALES
# ============================================

logger.info("=" * 80)
logger.info("✅ Données récentes ajoutées avec succès !")
logger.info("=" * 80)

# Compter les données des 7 derniers jours
seven_days_ago = (today - timedelta(days=7)).isoformat()

sales_count = (
    supabase.table("sales")
    .select("id", count="exact")
    .gte("created_at", seven_days_ago)
    .execute()
    .count
)

clicks_count = (
    supabase.table("click_tracking")
    .select("id", count="exact")
    .gte("clicked_at", seven_days_ago)
    .execute()
    .count
)

logger.info(f"\n📊 Données des 7 derniers jours:")
logger.info(f"  💰 {sales_count} ventes")
logger.info(f"  🖱️  {clicks_count} clics")

logger.info(f"\n🎉 Les graphiques vont maintenant afficher des données réelles de Supabase !")
logger.info(f"   - Évolution des Gains (7 jours)")
logger.info(f"   - Clics & Conversions (7 jours)")
