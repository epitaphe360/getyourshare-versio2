#!/usr/bin/env python3
"""
Test des endpoints /api/services
"""

import sys
import os

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_helpers import get_all_services, get_service_by_id
from supabase import create_client
import json
from utils.logger import logger

# Initialiser Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://jmehgebizhfabgjgflkd.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImptZWhnZWJpemhmYWJnamdmbGtkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcyMzU1ODUwOCwiZXhwIjoyMDM5MTM0NTA4fQ.pGIkBIw4qzaBT9d4BEVwdipKlLrjc52qsxmCPOCmBus")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

logger.info("🔍 TEST DES SERVICES")
logger.info("=" * 60)

# Test 1: Récupérer tous les services
logger.info("\n📋 Test 1: Récupération de tous les services")
logger.info("-" * 60)
services = get_all_services()
logger.info(f"✅ Total services: {len(services)}")

if services:
    logger.info("\n🔹 Premier service:")
    first_service = services[0]
    logger.info(f"   Nom: {first_service.get('name')}")
    logger.info(f"   Catégorie: {first_service.get('category')}")
    logger.info(f"   Prix par lead: {first_service.get('price_per_lead')}€")
    logger.info(f"   Capacité/mois: {first_service.get('capacity_per_month')}")
    logger.info(f"   Merchant ID: {first_service.get('merchant_id')}")
    
    if first_service.get('merchant'):
        logger.info(f"   Merchant: {first_service['merchant'].get('company_name')}")
    
    if first_service.get('lead_requirements'):
        logger.info(f"   Critères: {json.dumps(first_service['lead_requirements'], indent=6, ensure_ascii=False)}")

# Test 2: Récupérer par catégorie
logger.info("\n📊 Test 2: Services par catégorie")
logger.info("-" * 60)
categories = {}
for service in services:
    cat = service.get('category', 'Non défini')
    categories[cat] = categories.get(cat, 0) + 1

for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
    logger.info(f"   {cat}: {count} service(s)")

# Test 3: Récupérer un service spécifique
if services:
    logger.info("\n🔍 Test 3: Récupération d'un service par ID")
    logger.info("-" * 60)
    service_id = services[0].get('id')
    service = get_service_by_id(service_id)
    
    if service:
        logger.info(f"✅ Service trouvé: {service.get('name')}")
        logger.info(f"   ID: {service.get('id')}")
        logger.info(f"   Description: {service.get('description')[:100]}...")
        logger.info(f"   Tags: {service.get('tags')}")
    else:
        logger.info("❌ Service non trouvé")

# Test 4: Vérifier les colonnes importantes
logger.info("\n✅ Test 4: Vérification des colonnes")
logger.info("-" * 60)
required_columns = [
    'id', 'merchant_id', 'name', 'description', 'category',
    'price_per_lead', 'capacity_per_month', 'lead_requirements',
    'tags', 'images', 'is_available', 'created_at'
]

if services:
    missing_columns = [col for col in required_columns if col not in services[0]]
    if missing_columns:
        logger.info(f"⚠️  Colonnes manquantes: {', '.join(missing_columns)}")
    else:
        logger.info("✅ Toutes les colonnes requises sont présentes")

# Test 5: Statistiques
logger.info("\n📈 Test 5: Statistiques des services")
logger.info("-" * 60)
if services:
    prices = [s.get('price_per_lead', 0) for s in services]
    capacities = [s.get('capacity_per_month', 0) for s in services]
    
    logger.info(f"   Prix moyen par lead: {sum(prices) / len(prices):.2f}€")
    logger.info(f"   Prix min: {min(prices)}€")
    logger.info(f"   Prix max: {max(prices)}€")
    logger.info(f"   Capacité moyenne: {sum(capacities) / len(capacities):.0f} leads/mois")
    logger.info(f"   Services disponibles: {sum(1 for s in services if s.get('is_available', True))}")

logger.info("\n" + "=" * 60)
logger.info("✅ TESTS TERMINÉS")
logger.info("=" * 60)
