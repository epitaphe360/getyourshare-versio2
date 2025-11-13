"""
============================================
CRÉATION DE CONVERSIONS DE TEST
Génère des conversions réalistes pour la page Conversions
============================================
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client
import random
from utils.logger import logger

# Charger les variables d'environnement
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.info("❌ ERREUR: Variables SUPABASE_URL et SUPABASE_SERVICE_ROLE_KEY requises dans .env")
    sys.exit(1)

# Initialiser le client Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

logger.info("\n" + "="*60)
logger.info("🎯 CRÉATION DE CONVERSIONS DE TEST")
logger.info("="*60 + "\n")

# ============================================
# 1. RÉCUPÉRER LES DONNÉES EXISTANTES
# ============================================

logger.info("📊 Récupération des données...")

# Récupérer les campagnes
campaigns_response = supabase.table("campaigns").select("*").limit(10).execute()
campaigns = campaigns_response.data
logger.info(f"✅ {len(campaigns)} campagnes trouvées")

# Récupérer les influenceurs
influencers_response = supabase.table("influencers").select("*").limit(10).execute()
influencers = influencers_response.data
logger.info(f"✅ {len(influencers)} influenceurs trouvés")

# Récupérer les marchands
merchants_response = supabase.table("merchants").select("*").limit(10).execute()
merchants = merchants_response.data
logger.info(f"✅ {len(merchants)} marchands trouvés")

if not campaigns or not influencers:
    logger.info("\n❌ ERREUR: Pas assez de données (besoin de campagnes et influenceurs)")
    sys.exit(1)

# ============================================
# 2. CRÉER DES LIENS D'AFFILIATION
# ============================================

logger.info("\n📎 Création des liens d'affiliation...")

affiliate_links = []
link_count = 0

for campaign in campaigns[:5]:  # 5 campagnes max
    for influencer in influencers[:3]:  # 3 influenceurs par campagne
        # Générer un code court unique
        short_code = f"{campaign['id'][:6]}{influencer['id'][:6]}{random.randint(100, 999)}"
        
        link_data = {
            "campaign_id": campaign["id"],
            "influencer_id": influencer["id"],
            "merchant_id": campaign.get("merchant_id"),
            "short_code": short_code,
            "original_url": f"https://shop.example.com/campaign/{campaign['id']}",
            "clicks": random.randint(50, 500),
            "conversions": 0,  # Sera mis à jour après
            "revenue": 0.0,
            "status": "active",
            "created_at": (datetime.now() - timedelta(days=random.randint(7, 30))).isoformat()
        }
        
        try:
            result = supabase.table("affiliate_links").insert(link_data).execute()
            affiliate_links.append(result.data[0])
            link_count += 1
            logger.info(f"  ✅ Lien créé: {short_code}")
        except Exception as e:
            if "duplicate" not in str(e).lower():
                logger.info(f"  ⚠️  Erreur lien {short_code}: {e}")

logger.info(f"\n✅ {link_count} liens d'affiliation créés")

# ============================================
# 3. CRÉER DES CONVERSIONS
# ============================================

logger.info("\n💰 Création des conversions...")

CONVERSION_STATUSES = ["pending", "validated", "paid", "refunded"]
CONVERSION_WEIGHTS = [0.3, 0.5, 0.15, 0.05]  # Probabilities

conversions_created = 0
total_revenue = 0

for link in affiliate_links:
    # Créer entre 2 et 10 conversions par lien
    num_conversions = random.randint(2, 10)
    
    for i in range(num_conversions):
        # Montant de commande réaliste (Maroc)
        order_amount = round(random.uniform(200, 5000), 2)
        
        # Taux de commission (5-25%)
        campaign = next((c for c in campaigns if c["id"] == link["campaign_id"]), None)
        commission_rate = campaign.get("commission_rate", 10) if campaign else 10
        commission_amount = round(order_amount * (commission_rate / 100), 2)
        
        # Statut avec distribution réaliste
        status = random.choices(CONVERSION_STATUSES, weights=CONVERSION_WEIGHTS)[0]
        
        # Date de conversion (dans les 30 derniers jours)
        conversion_date = datetime.now() - timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        # ID de commande unique
        order_id = f"ORD-{random.randint(10000, 99999)}"
        
        conversion_data = {
            "affiliate_link_id": link["id"],
            "campaign_id": link["campaign_id"],
            "influencer_id": link["influencer_id"],
            "merchant_id": link["merchant_id"],
            "order_id": order_id,
            "order_amount": order_amount,
            "commission_amount": commission_amount,
            "commission_rate": commission_rate,
            "status": status,
            "conversion_date": conversion_date.isoformat(),
            "validated_at": (conversion_date + timedelta(days=1)).isoformat() if status in ["validated", "paid"] else None,
            "paid_at": (conversion_date + timedelta(days=7)).isoformat() if status == "paid" else None,
            "created_at": conversion_date.isoformat(),
            "metadata": {
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "ip_address": f"41.{random.randint(100, 250)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
                "device": random.choice(["desktop", "mobile", "tablet"]),
                "browser": random.choice(["Chrome", "Safari", "Firefox", "Edge"])
            }
        }
        
        try:
            result = supabase.table("conversions").insert(conversion_data).execute()
            conversions_created += 1
            total_revenue += commission_amount
            
            # Afficher avec couleur selon statut
            status_emoji = {
                "pending": "⏳",
                "validated": "✅",
                "paid": "💵",
                "refunded": "↩️"
            }
            logger.info(f"  {status_emoji.get(status, '•')} {order_id}: {order_amount:.2f} MAD → {commission_amount:.2f} MAD ({status})")
            
        except Exception as e:
            logger.info(f"  ❌ Erreur conversion {order_id}: {e}")

logger.info(f"\n✅ {conversions_created} CONVERSIONS CRÉÉES!")
logger.info(f"💰 Revenu total commissions: {total_revenue:.2f} MAD")

# ============================================
# 4. METTRE À JOUR LES STATISTIQUES
# ============================================

logger.info("\n📊 Mise à jour des statistiques...")

for link in affiliate_links:
    try:
        # Compter les conversions pour ce lien
        conversions_response = supabase.table("conversions")\
            .select("*")\
            .eq("affiliate_link_id", link["id"])\
            .execute()
        
        link_conversions = conversions_response.data
        conversion_count = len(link_conversions)
        revenue = sum(c["commission_amount"] for c in link_conversions if c["status"] in ["validated", "paid"])
        
        # Mettre à jour le lien
        supabase.table("affiliate_links")\
            .update({
                "conversions": conversion_count,
                "revenue": revenue
            })\
            .eq("id", link["id"])\
            .execute()
        
        logger.info(f"  ✅ Lien {link['short_code']}: {conversion_count} conversions, {revenue:.2f} MAD")
        
    except Exception as e:
        logger.info(f"  ⚠️  Erreur mise à jour lien: {e}")

# ============================================
# 5. STATISTIQUES FINALES
# ============================================

logger.info("\n" + "="*60)
logger.info("📊 STATISTIQUES FINALES")
logger.info("="*60)

# Compter par statut
for status in CONVERSION_STATUSES:
    count_response = supabase.table("conversions")\
        .select("*", count="exact")\
        .eq("status", status)\
        .execute()
    count = count_response.count
    
    status_labels = {
        "pending": "⏳ En attente",
        "validated": "✅ Validées",
        "paid": "💵 Payées",
        "refunded": "↩️ Remboursées"
    }
    logger.info(f"{status_labels.get(status, status)}: {count}")

logger.info("\n" + "="*60)
logger.info("✅ CONVERSIONS PRÊTES À ÊTRE TESTÉES!")
logger.info("="*60)
logger.info("\n🌐 PAGES À TESTER:")
logger.info("  • http://localhost:3000/merchant/conversions")
logger.info("  • http://localhost:3000/influencer/conversions")
logger.info("  • http://localhost:3000/admin/conversions")
logger.info("\n📝 FONCTIONNALITÉS:")
logger.info("  ✅ Export des conversions")
logger.info("  ✅ Filtrage par statut")
logger.info("  ✅ Tri par date, montant, commission")
logger.info("  ✅ Recherche par ID commande")
logger.info("\n")
