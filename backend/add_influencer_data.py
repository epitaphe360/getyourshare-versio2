"""
Script pour ajouter des données réalistes aux influenceurs
"""
import os
from supabase import create_client
from utils.logger import logger

# Charger manuellement les variables depuis .env
try:
    with open('.env', 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value
except Exception as e:
    logger.info(f"Erreur lors du chargement du .env: {e}")

# Connexion Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")

logger.info(f"URL: {supabase_url[:30] if supabase_url else 'None'}...")
logger.info(f"Key: {'✅ Chargée' if supabase_key else '❌ Manquante'}\n")

supabase = create_client(supabase_url, supabase_key)

def add_influencer_data():
    """Ajoute des données réalistes aux influenceurs"""
    
    logger.info("\n" + "="*60)
    logger.info("🔧 AJOUT DES DONNÉES AUX INFLUENCEURS")
    logger.info("="*60 + "\n")
    
    # Récupérer tous les influenceurs
    result = supabase.table("users").select("id, email").eq("role", "influencer").execute()
    influencers = result.data
    
    if not influencers:
        logger.info("❌ Aucun influenceur trouvé")
        return
    
    logger.info(f"✅ {len(influencers)} influenceurs trouvés\n")
    
    # Données d'influenceurs réalistes
    influencer_data = [
        {
            "first_name": "Sarah",
            "last_name": "Benali",
            "company_name": "@sarah_lifestyle",
            "country": "Maroc",
            "balance": 2450.00,
            "total_earned": 8900.50,
            "followers_count": 45000,
            "engagement_rate": 4.2
        },
        {
            "first_name": "Karim",
            "last_name": "Aziz",
            "company_name": "@karim_tech",
            "country": "France",
            "balance": 3200.00,
            "total_earned": 12500.00,
            "followers_count": 78000,
            "engagement_rate": 5.8
        },
        {
            "first_name": "Yasmine",
            "last_name": "El Mansouri",
            "company_name": "@yasmine_beauty",
            "country": "Maroc",
            "balance": 1850.00,
            "total_earned": 6700.00,
            "followers_count": 32000,
            "engagement_rate": 3.5
        },
        {
            "first_name": "Mohamed",
            "last_name": "Tazi",
            "company_name": "@mo_fitness",
            "country": "Maroc",
            "balance": 4100.00,
            "total_earned": 15300.00,
            "followers_count": 92000,
            "engagement_rate": 6.1
        },
        {
            "first_name": "Nadia",
            "last_name": "Khalil",
            "company_name": "@nadia_fashion",
            "country": "France",
            "balance": 5500.00,
            "total_earned": 22100.00,
            "followers_count": 125000,
            "engagement_rate": 7.3
        },
        {
            "first_name": "Omar",
            "last_name": "Alaoui",
            "company_name": "@omar_travel",
            "country": "Maroc",
            "balance": 2900.00,
            "total_earned": 9800.00,
            "followers_count": 58000,
            "engagement_rate": 4.9
        },
        {
            "first_name": "Leila",
            "last_name": "Benjelloun",
            "company_name": "@leila_food",
            "country": "Maroc",
            "balance": 3600.00,
            "total_earned": 11200.00,
            "followers_count": 67000,
            "engagement_rate": 5.2
        },
        {
            "first_name": "Amine",
            "last_name": "Rachidi",
            "company_name": "@amine_gaming",
            "country": "France",
            "balance": 4800.00,
            "total_earned": 18900.00,
            "followers_count": 110000,
            "engagement_rate": 6.7
        },
        {
            "first_name": "Fatima",
            "last_name": "Zahra",
            "company_name": "@fati_wellness",
            "country": "Maroc",
            "balance": 2200.00,
            "total_earned": 7500.00,
            "followers_count": 41000,
            "engagement_rate": 4.0
        },
        {
            "first_name": "Youssef",
            "last_name": "Idrissi",
            "company_name": "@youssef_photo",
            "country": "Maroc",
            "balance": 3300.00,
            "total_earned": 10900.00,
            "followers_count": 73000,
            "engagement_rate": 5.5
        },
        {
            "first_name": "Samira",
            "last_name": "Berrada",
            "company_name": "@samira_art",
            "country": "France",
            "balance": 2700.00,
            "total_earned": 8300.00,
            "followers_count": 52000,
            "engagement_rate": 4.6
        },
    ]
    
    # Mettre à jour chaque influenceur
    for i, influencer in enumerate(influencers):
        data = influencer_data[i % len(influencer_data)]
        
        try:
            supabase.table("users").update({
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "company_name": data["company_name"],
                "country": data["country"],
                "balance": data["balance"],
                "total_earned": data["total_earned"],
                "followers_count": data["followers_count"],
                "engagement_rate": data["engagement_rate"],
                "status": "active"
            }).eq("id", influencer["id"]).execute()
            
            logger.info(f"✅ {data['first_name']} {data['last_name']} ({data['company_name']})")
            logger.info(f"   Email: {influencer.get('email', 'N/A')}")
            logger.info(f"   Pays: {data['country']}")
            logger.info(f"   Followers: {data['followers_count']:,}")
            logger.info(f"   Engagement: {data['engagement_rate']}%")
            logger.info(f"   Balance: {data['balance']} €")
            logger.info(f"   Total gagné: {data['total_earned']} €")
            print()
            
        except Exception as e:
            logger.info(f"❌ Erreur: {e}")
            return
    
    logger.info("\n" + "="*60)
    logger.info("✅ DONNÉES INFLUENCEURS AJOUTÉES AVEC SUCCÈS!")
    logger.info("="*60)
    logger.info("\n💡 Rafraîchissez la page des influenceurs")

if __name__ == "__main__":
    add_influencer_data()
