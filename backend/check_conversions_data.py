"""
Script pour vérifier l'état des données de conversions
"""
import os
from supabase import create_client
from dotenv import load_dotenv
from utils.logger import logger

# Charger les variables d'environnement
load_dotenv()

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.info("❌ Erreur: Variables d'environnement manquantes")
    logger.info("   SUPABASE_URL et SUPABASE_SERVICE_ROLE_KEY requis")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

logger.info("\n" + "="*60)
logger.info("🔍 VÉRIFICATION DES DONNÉES DE CONVERSIONS")
logger.info("="*60 + "\n")

# 1. Vérifier les tables
logger.info("📊 Vérification des tables...")
tables_to_check = ['affiliate_links', 'conversions', 'clicks']

for table_name in tables_to_check:
    try:
        result = supabase.table(table_name).select("*", count='exact').limit(1).execute()
        count = result.count if hasattr(result, 'count') else len(result.data)
        logger.info(f"✅ Table '{table_name}' existe: {count} ligne(s) trouvée(s)")
    except Exception as e:
        logger.info(f"❌ Erreur table '{table_name}': {str(e)}")

logger.info("\n" + "-"*60 + "\n")

# 2. Compter les conversions
logger.info("💰 Conversions:")
try:
    conversions = supabase.table('conversions').select("*", count='exact').execute()
    total = conversions.count if hasattr(conversions, 'count') else len(conversions.data)
    logger.info(f"   Total: {total} conversions")
    
    if total > 0:
        # Par statut
        for status in ['pending', 'validated', 'paid', 'refunded']:
            status_result = supabase.table('conversions')\
                .select("*", count='exact')\
                .eq('status', status)\
                .execute()
            status_count = status_result.count if hasattr(status_result, 'count') else len(status_result.data)
            logger.info(f"   {status.capitalize()}: {status_count}")
        
        # Exemples
        logger.info("\n📝 Exemples de conversions:")
        examples = supabase.table('conversions')\
            .select("order_id, order_amount, commission_amount, status")\
            .limit(5)\
            .execute()
        
        for conv in examples.data:
            logger.info(f"   {conv['order_id']}: {conv['order_amount']} MAD → {conv['commission_amount']} MAD ({conv['status']})")
    else:
        logger.info("   ⚠️  Aucune conversion trouvée!")
        
except Exception as e:
    logger.info(f"   ❌ Erreur: {str(e)}")

logger.info("\n" + "-"*60 + "\n")

# 3. Compter les liens d'affiliation
logger.info("📎 Liens d'affiliation:")
try:
    links = supabase.table('affiliate_links').select("*", count='exact').execute()
    total = links.count if hasattr(links, 'count') else len(links.data)
    logger.info(f"   Total: {total} liens")
    
    if total > 0:
        # Exemples
        logger.info("\n📝 Exemples de liens:")
        examples = supabase.table('affiliate_links')\
            .select("short_code, clicks, conversions, revenue")\
            .limit(5)\
            .execute()
        
        for link in examples.data:
            logger.info(f"   {link['short_code']}: {link['clicks']} clics, {link['conversions']} conversions, {link['revenue']} MAD")
    else:
        logger.info("   ⚠️  Aucun lien trouvé!")
        
except Exception as e:
    logger.info(f"   ❌ Erreur: {str(e)}")

logger.info("\n" + "-"*60 + "\n")

# 4. Vérifier les campagnes
logger.info("📢 Campagnes:")
try:
    campaigns = supabase.table('campaigns').select("id, name", count='exact').execute()
    total = campaigns.count if hasattr(campaigns, 'count') else len(campaigns.data)
    logger.info(f"   Total: {total} campagnes")
    
    if total > 0:
        for camp in campaigns.data[:5]:
            logger.info(f"   - {camp['name']}")
    else:
        logger.info("   ⚠️  Aucune campagne trouvée!")
        
except Exception as e:
    logger.info(f"   ❌ Erreur: {str(e)}")

logger.info("\n" + "-"*60 + "\n")

# 5. Vérifier les influenceurs
logger.info("👥 Influenceurs:")
try:
    influencers = supabase.table('influencers').select("id, full_name", count='exact').execute()
    total = influencers.count if hasattr(influencers, 'count') else len(influencers.data)
    logger.info(f"   Total: {total} influenceurs")
    
    if total > 0:
        for inf in influencers.data[:5]:
            logger.info(f"   - {inf['full_name']}")
    else:
        logger.info("   ⚠️  Aucun influenceur trouvé!")
        
except Exception as e:
    logger.info(f"   ❌ Erreur: {str(e)}")

logger.info("\n" + "-"*60 + "\n")

# 6. Vérifier les marchands
logger.info("🏪 Marchands:")
try:
    merchants = supabase.table('merchants').select("id, company_name", count='exact').execute()
    total = merchants.count if hasattr(merchants, 'count') else len(merchants.data)
    logger.info(f"   Total: {total} marchands")
    
    if total > 0:
        for merch in merchants.data[:5]:
            logger.info(f"   - {merch['company_name']}")
    else:
        logger.info("   ⚠️  Aucun marchand trouvé!")
        
except Exception as e:
    logger.info(f"   ❌ Erreur: {str(e)}")

logger.info("\n" + "="*60)
logger.info("✅ VÉRIFICATION TERMINÉE")
logger.info("="*60 + "\n")
