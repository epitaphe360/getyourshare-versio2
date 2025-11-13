"""
Test - Appeler l'API products directement
"""
import requests
from utils.logger import logger

# Test l'API sans authentification
try:
    response = requests.get("http://localhost:8000/api/products")
    logger.info(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        logger.info(f"\n✅ Total produits: {data.get('total', 0)}")
        
        if data.get('products'):
            logger.info("\n📦 Premiers produits:")
            for i, p in enumerate(data['products'][:3], 1):
                logger.info(f"{i}. {p.get('name')} - {p.get('price')}€")
    else:
        logger.info(f"❌ Erreur: {response.text}")
        
except requests.exceptions.ConnectionError:
    logger.info("❌ Serveur non accessible sur http://localhost:8000")
except Exception as e:
    logger.info(f"❌ Erreur: {e}")
