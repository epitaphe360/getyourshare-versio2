"""
Script pour créer les tables commerciales et insérer les données de test
=====================================================================
Exécute automatiquement :
1. CREATE_COMMERCIAL_TABLES.sql (anciennes tables existantes)
2. INSERT_COMMERCIAL_DATA.sql (nouvelles données)
"""

import os
import sys
from pathlib import Path
from supabase import create_client, Client
from utils.logger import logger

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://gwgvnusegnnhiciprvyc.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd3Z3ZudXNlZ25uaGljaXBydnljIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzA4MjE3NjgsImV4cCI6MjA0NjM5Nzc2OH0.gftLI_u0AxQUVIUi3hWjfJQ-m6Y56b5H5lDwbMEDGbU")

def read_sql_file(filepath: str) -> str:
    """Lit un fichier SQL"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.text()

def execute_sql_statements(supabase: Client, sql_content: str, filename: str):
    """
    Exécute des statements SQL un par un
    Note: Supabase Python client ne supporte pas l'exécution SQL directe
    Il faut utiliser l'API REST ou le dashboard Supabase
    """
    logger.info(f"\n⚠️  Le fichier {filename} doit être exécuté manuellement dans Supabase SQL Editor")
    logger.info(f"📋 Contenu à copier-coller :\n")
    logger.info("="*80)
    logger.info(sql_content[:500] + "...\n" + "="*80)
    logger.info(f"\n💡 Allez sur: {SUPABASE_URL.replace('https://', 'https://app.supabase.com/project/')}/sql/new")
    logger.info(f"   Collez le contenu de: {filename}")
    logger.info(f"   Cliquez sur 'Run'\n")

def main():
    """Fonction principale"""
    logger.info("="*80)
    logger.info("🚀 CRÉATION DES TABLES COMMERCIALES ET DONNÉES DE TEST")
    logger.info("="*80)
    
    # Initialiser Supabase client
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("✅ Connexion Supabase établie")
    except Exception as e:
        logger.info(f"❌ Erreur de connexion Supabase: {e}")
        return
    
    # Chemins des fichiers SQL
    root_dir = Path(__file__).parent.parent
    
    # Note: Les tables sont déjà créées avec CREATE_COMMERCIAL_TABLES.sql (ancien fichier)
    # On va juste exécuter les INSERT
    
    sql_files = [
        {
            'path': root_dir / 'INSERT_COMMERCIAL_DATA.sql',
            'name': 'INSERT_COMMERCIAL_DATA.sql',
            'description': 'Insertion des données de test (3 commerciaux, leads, liens, templates)'
        }
    ]
    
    logger.info("\n📦 Fichiers SQL à exécuter :")
    for idx, sql_file in enumerate(sql_files, 1):
        logger.info(f"   {idx}. {sql_file['name']} - {sql_file['description']}")
    
    logger.info("\n" + "="*80)
    logger.info("⚠️  IMPORTANT: Les scripts SQL doivent être exécutés dans le SQL Editor de Supabase")
    logger.info("="*80)
    
    for sql_file in sql_files:
        filepath = sql_file['path']
        
        if not filepath.exists():
            logger.info(f"\n❌ Fichier non trouvé: {filepath}")
            continue
        
        logger.info(f"\n{'='*80}")
        logger.info(f"📄 Fichier: {sql_file['name']}")
        logger.info(f"📝 Description: {sql_file['description']}")
        logger.info(f"{'='*80}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            logger.info(f"✅ Fichier lu ({len(sql_content)} caractères)")
            
            # Afficher les instructions
            execute_sql_statements(supabase, sql_content, sql_file['name'])
            
        except Exception as e:
            logger.info(f"❌ Erreur lors de la lecture de {sql_file['name']}: {e}")
    
    logger.info("\n" + "="*80)
    logger.info("🎯 PROCHAINES ÉTAPES")
    logger.info("="*80)
    logger.info("""
1. ✅ Ouvrir Supabase Dashboard: https://app.supabase.com/project/gwgvnusegnnhiciprvyc/sql/new

2. ✅ Exécuter INSERT_COMMERCIAL_DATA.sql :
   - Copier le contenu du fichier
   - Coller dans le SQL Editor
   - Cliquer sur "Run"
   - Vérifier qu'il n'y a pas d'erreurs

3. ✅ Vérifier les données insérées :
   SELECT * FROM users WHERE role = 'commercial';
   SELECT * FROM sales_representatives;
   SELECT * FROM commercial_leads LIMIT 10;
   SELECT * FROM commercial_tracking_links LIMIT 10;
   SELECT * FROM commercial_templates LIMIT 10;

4. ✅ Tester les endpoints backend :
   - Ajouter commercial_endpoints.py dans server.py
   - app.include_router(commercial_endpoints.router)
   - Redémarrer le backend
   - Tester : GET /api/commercial/stats

5. ✅ Créer le frontend CommercialDashboard.js
    """)
    
    logger.info("\n" + "="*80)
    logger.info("💾 COMPTES DE TEST CRÉÉS")
    logger.info("="*80)
    logger.info("""
Email: commercial.starter@tracknow.io
Mot de passe: Test123!
Niveau: STARTER (gratuit, 10 leads max, 3 liens)

Email: commercial.pro@tracknow.io
Mot de passe: Test123!
Niveau: PRO (29€/mois, leads illimités, 15 templates)

Email: commercial.enterprise@tracknow.io
Mot de passe: Test123!
Niveau: ENTERPRISE (99€/mois, tout débloqué + IA)
    """)
    
    logger.info("\n✨ Script terminé !")

if __name__ == "__main__":
    main()
