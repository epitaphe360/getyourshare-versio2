#!/usr/bin/env python3
"""
Test du comptage des services dans les stats du dashboard admin
"""

import sys
import os

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_helpers import get_dashboard_stats
from supabase import create_client
from utils.logger import logger

# Initialiser Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://jmehgebizhfabgjgflkd.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImptZWhnZWJpemhmYWJnamdmbGtkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcyMzU1ODUwOCwiZXhwIjoyMDM5MTM0NTA4fQ.pGIkBIw4qzaBT9d4BEVwdipKlLrjc52qsxmCPOCmBus")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

logger.info("🔍 TEST DES STATISTIQUES DASHBOARD ADMIN")
logger.info("=" * 70)

# Récupérer un admin ID pour le test
admin_result = supabase.table("users").select("id").eq("role", "admin").limit(1).execute()
admin_id = admin_result.data[0]["id"] if admin_result.data else "test-admin-id"

logger.info(f"\n📊 Admin ID utilisé: {admin_id}")
logger.info("-" * 70)

# Récupérer les stats
stats = get_dashboard_stats("admin", admin_id)

logger.info("\n✅ STATISTIQUES RÉCUPÉRÉES:")
logger.info("-" * 70)
logger.info(f"   👥 Total utilisateurs:   {stats.get('total_users', 0)}")
logger.info(f"   🏪 Total entreprises:    {stats.get('total_merchants', 0)}")
logger.info(f"   🌟 Total influenceurs:   {stats.get('total_influencers', 0)}")
logger.info(f"   📦 Total produits:       {stats.get('total_products', 0)}")
logger.info(f"   💼 Total services:       {stats.get('total_services', 0)}")
logger.info(f"   💰 Revenus total:        {stats.get('total_revenue', 0):.2f}€")

# Vérifications
logger.info("\n🔍 VÉRIFICATIONS:")
logger.info("-" * 70)

if 'total_services' in stats:
    logger.info("✅ Le champ 'total_services' est présent dans les stats")
    logger.info(f"   Valeur: {stats['total_services']}")
    
    if stats['total_services'] == 8:
        logger.info("✅ Le nombre de services correspond aux 8 services de test insérés")
    elif stats['total_services'] > 0:
        logger.info(f"ℹ️  {stats['total_services']} service(s) trouvé(s) dans la base")
    else:
        logger.info("⚠️  Aucun service trouvé (table vide ou erreur)")
else:
    logger.info("❌ Le champ 'total_services' est ABSENT des stats")
    logger.info("   La fonction get_dashboard_stats doit être mise à jour")

# Vérification directe dans la base
logger.info("\n🔍 VÉRIFICATION DIRECTE DANS LA BASE:")
logger.info("-" * 70)
services_direct = supabase.table("services").select("id", count="exact").execute()
services_count_direct = services_direct.count or 0
logger.info(f"   Services dans la base: {services_count_direct}")

if 'total_services' in stats and stats['total_services'] == services_count_direct:
    logger.info("✅ Le comptage des services dans les stats correspond à la base")
else:
    logger.info("❌ Incohérence entre les stats et la base")

logger.info("\n" + "=" * 70)
logger.info("✅ TEST TERMINÉ")
logger.info("=" * 70)
