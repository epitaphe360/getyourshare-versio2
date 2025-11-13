"""Vérification des 5 fonctionnalités TOP"""
import os
from pathlib import Path
from utils.logger import logger

logger.info("\n" + "="*80)
logger.info("VÉRIFICATION DES 5 FONCTIONNALITÉS FLAGSHIP")
logger.info("="*80 + "\n")

# Racine du projet
root = Path(r"C:\Users\samye\OneDrive\Desktop\v3\getyourshareversion2-")

features = {
    "1. Gamification": [
        "backend/services/gamification_service.py",
        "frontend/src/components/gamification/GamificationWidget.jsx",
        "backend/endpoints/gamification_endpoints.py"
    ],
    "2. Matching IA Tinder-style": [
        "backend/services/influencer_matching_service.py",
        "backend/endpoints/matching_endpoints.py",
        "frontend/src/pages/matching/InfluencerMatching.jsx"
    ],
    "3. Lead Scoring": [
        "backend/services/lead_scoring_service.py",
        "backend/endpoints/lead_scoring_endpoints.py"
    ],
    "4. Analytics Pro IA": [
        "backend/services/analytics_pro_service.py",
        "frontend/src/pages/analytics/AnalyticsPro.jsx"
    ],
    "5. Mobile PWA": [
        "frontend/public/manifest.json",
        "frontend/src/serviceWorker.js",
        "frontend/public/service-worker.js"
    ]
}

for feature, files in features.items():
    logger.info(f"\n{feature}")
    logger.info("-" * 70)
    
    found = 0
    total = len(files)
    
    for file_path in files:
        full_path = root / file_path
        exists = full_path.exists()
        
        status = "✅" if exists else "❌"
        logger.info(f"  {status} {file_path}")
        
        if exists:
            found += 1
            # Afficher la taille
            size = full_path.stat().st_size
            logger.info(f"     ({size:,} bytes)")
    
    percentage = (found / total * 100) if total > 0 else 0
    status_emoji = "✅" if percentage == 100 else ("⚠️" if percentage > 0 else "❌")
    logger.info(f"\n  {status_emoji} Status: {found}/{total} fichiers présents ({percentage:.0f}%)")

logger.info("\n" + "="*80)
logger.info("RÉSUMÉ")
logger.info("="*80)

# Compter le total
all_files = []
for files in features.values():
    all_files.extend(files)

found_total = sum(1 for f in all_files if (root / f).exists())
total_files = len(all_files)

logger.info(f"\n✅ {found_total}/{total_files} fichiers trouvés ({found_total/total_files*100:.0f}%)")

if found_total < total_files:
    logger.info(f"\n⚠️  {total_files - found_total} fichiers manquants")
    logger.info("\nFichiers manquants:")
    for f in all_files:
        if not (root / f).exists():
            logger.info(f"  ❌ {f}")

logger.info("\n" + "="*80 + "\n")
