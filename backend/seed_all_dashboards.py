
#!/usr/bin/env python3
"""
MASTER SEED SCRIPT
Exécute tous les scripts de seed pour peupler les dashboards Influencer, Merchant et Commercial.
"""

import os
import sys
import subprocess
from dotenv import load_dotenv
from utils.logger import logger

load_dotenv()

def run_script(script_name):
    """Exécute un script Python et affiche sa sortie"""
    logger.info(f"\n{'='*80}")
    logger.info(f"🚀 EXÉCUTION DE: {script_name}")
    logger.info(f"{'='*80}\n")
    
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    
    if not os.path.exists(script_path):
        logger.error(f"❌ Script introuvable: {script_path}")
        return False
        
    try:
        # Utiliser l'interpréteur Python actuel
        python_exe = sys.executable
        result = subprocess.run([python_exe, script_path], check=False)
        
        if result.returncode == 0:
            logger.info(f"\n✅ {script_name} terminé avec succès.")
            return True
        else:
            logger.error(f"\n❌ {script_name} a échoué (Code: {result.returncode}).")
            return False
            
    except Exception as e:
        logger.error(f"\n❌ Erreur lors de l'exécution de {script_name}: {e}")
        return False

def main():
    logger.info("="*80)
    logger.info("🛠️  INITIALISATION DU PEUPLEMENT DES DASHBOARDS")
    logger.info("="*80)
    print("Ce script va analyser les tables vides et ajouter des données pour:")
    print("1. Influencers (Profils, Stats, Clics)")
    print("2. Merchants (Produits, Ventes, Invoices)")
    print("3. Commercials (Leads, Activités, Pipeline)")
    print("4. Fonctionnalités transverses (Messages, Abonnements, Avis)")
    print()
    
    scripts = [
        "seed_comprehensive_dashboard_data.py", # Base: Products, Influencers, Sales, Clicks
        "seed_commercial_data.py",              # Commercial: Leads, Activities
        "seed_missing_features.py"              # Extras: Subscriptions, Messages, Reviews
    ]
    
    success_count = 0
    
    for script in scripts:
        if run_script(script):
            success_count += 1
            
    print()
    logger.info("="*80)
    logger.info(f"🏁 TERMINÉ: {success_count}/{len(scripts)} scripts exécutés avec succès.")
    logger.info("="*80)
    
    if success_count == len(scripts):
        logger.info("✨ Tous les dashboards devraient maintenant avoir des données!")
    else:
        logger.warning("⚠️  Certains scripts ont échoué. Vérifiez les logs ci-dessus.")

if __name__ == "__main__":
    main()
