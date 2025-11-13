"""
Nettoyage complet de toutes les données mockées
ATTENTION: Ce script va SUPPRIMER des données !
"""
from supabase_client import supabase
from utils.logger import logger

logger.info("\n" + "="*80)
logger.info("🧹 NETTOYAGE DES DONNÉES MOCKÉES")
logger.info("="*80)
logger.info("\n⚠️  ATTENTION: Ce script va supprimer des données !")
logger.info("   Appuyez sur Ctrl+C maintenant pour annuler\n")

input("Appuyez sur ENTER pour continuer...")

deleted_count = {}

# Liste des tables à nettoyer (avec condition)
tables_to_clean = [
    ("sales", "Ventes"),
    ("click_tracking", "Clics"),
    ("commissions", "Commissions"),
    ("affiliate_requests", "Demandes d'affiliation"),
    ("campaigns", "Campagnes"),
    ("products", "Produits"),
    ("services", "Services"),
]

logger.info("\n" + "="*80)
logger.info("SUPPRESSION EN COURS...")
logger.info("="*80 + "\n")

for table_name, description in tables_to_clean:
    try:
        # Compter d'abord
        count_before = supabase.table(table_name).select("id", count="exact").execute().count or 0
        
        if count_before > 0:
            # Supprimer
            supabase.table(table_name).delete().neq("id", "").execute()
            
            # Vérifier
            count_after = supabase.table(table_name).select("id", count="exact").execute().count or 0
            deleted = count_before - count_after
            
            deleted_count[table_name] = deleted
            logger.info(f"✅ {description:30} - {deleted} enregistrements supprimés")
        else:
            logger.info(f"ℹ️  {description:30} - Déjà vide")
            
    except Exception as e:
        logger.info(f"❌ {description:30} - Erreur: {e}")

logger.info("\n" + "="*80)
logger.info("RÉSUMÉ")
logger.info("="*80)
total = sum(deleted_count.values())
logger.info(f"\n✅ {total} enregistrements supprimés au total")
logger.info("\n⚠️  Note: Les utilisateurs ont été conservés")
logger.info("   Utilisez reset_all_passwords.py pour les mots de passe\n")
