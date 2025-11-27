"""Appliquer la migration pour créer les tables influencers et merchants"""
from supabase_client import supabase
from utils.logger import logger
import os

# Lire le fichier SQL
script_dir = os.path.dirname(os.path.abspath(__file__))
sql_file = os.path.join(script_dir, "database", "CREATE_INFLUENCERS_MERCHANTS_TABLES.sql")

logger.info("=== MIGRATION: CRÉATION DES TABLES INFLUENCERS ET MERCHANTS ===\n")

try:
    # Lire le contenu du fichier SQL
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    logger.info("📄 Fichier SQL chargé")
    logger.info(f"   Taille: {len(sql_content)} caractères\n")
    
    # Exécuter le SQL via RPC
    logger.info("⚙️  Exécution de la migration via RPC...")
    
    try:
        # Utiliser la fonction RPC exec_sql si elle existe
        result = supabase.rpc('exec_sql', {'sql': sql_content}).execute()
        logger.info("✅ Migration exécutée avec succès via RPC!")
        logger.info(f"   Résultat: {result}")
    except Exception as rpc_error:
        logger.info(f"⚠️  RPC non disponible: {rpc_error}")
        logger.info("\n💡 SOLUTION ALTERNATIVE:")
        logger.info("   Copiez le SQL ci-dessous et exécutez-le dans Supabase SQL Editor\n")
        
        # Afficher le SQL à copier
        logger.info("═" * 80)
        logger.info("SQL À COPIER-COLLER DANS SUPABASE:")
        logger.info("═" * 80)
        print(sql_content)
        logger.info("═" * 80)
        
        logger.info("\n📋 ÉTAPES:")
        logger.info("   1. Allez sur https://supabase.com/dashboard")
        logger.info("   2. Sélectionnez votre projet")
        logger.info("   3. Cliquez sur 'SQL Editor' dans le menu")
        logger.info("   4. Cliquez sur 'New query'")
        logger.info("   5. Collez le SQL ci-dessus")
        logger.info("   6. Cliquez sur 'Run' (ou Ctrl+Enter)")
        logger.info("   7. Vérifiez que les tables sont créées\n")
    
    logger.info("✅ Migration prête")
    
except FileNotFoundError:
    logger.info(f"❌ Fichier SQL non trouvé: {sql_file}")
except Exception as e:
    logger.info(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
