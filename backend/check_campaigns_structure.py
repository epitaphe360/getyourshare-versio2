"""
Vérifier la structure de la table campaigns
"""
import os
from supabase import create_client
from dotenv import load_dotenv
from utils.logger import logger

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

logger.info("\n🔍 Vérification structure table 'campaigns'...\n")

try:
    # Essayer de récupérer une campagne vide pour voir la structure
    response = supabase.table("campaigns").select("*").limit(1).execute()
    
    if response.data:
        logger.info("✅ Table 'campaigns' existe avec données:")
        logger.info(f"   Colonnes trouvées: {list(response.data[0].keys())}")
        logger.info(f"\n📄 Exemple de donnée:")
        for key, value in response.data[0].items():
            logger.info(f"   {key}: {value}")
    else:
        logger.info("✅ Table 'campaigns' existe mais est vide")
        logger.info("   Impossible de déterminer la structure exacte")
        
        # Essayer d'insérer une campagne minimale pour voir quelles colonnes sont requises
        logger.info("\n🧪 Test d'insertion minimale...")
        
except Exception as e:
    logger.info(f"❌ Erreur: {e}")
    logger.info("\n💡 La table 'campaigns' n'existe probablement pas dans Supabase")
    logger.info("   Vous devez d'abord exécuter le script SQL de création:")
    logger.info("   backend/database/INIT_SUPABASE_COMPLET.sql")
