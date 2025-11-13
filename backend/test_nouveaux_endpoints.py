"""
TEST RAPIDE - Vérifier que tous les nouveaux endpoints sont accessibles
"""

import requests
import json
from utils.logger import logger

BASE_URL = "http://localhost:8000"

def test_endpoints():
    """Teste tous les nouveaux endpoints"""
    
    logger.info("🧪 TEST DES NOUVEAUX ENDPOINTS")
    logger.info("=" * 60)
    
    # Test 1: Health check
    logger.info("\n1️⃣ Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        logger.info(f"   ✅ Status: {response.status_code}")
        logger.info(f"   Response: {response.json()}")
    except Exception as e:
        logger.info(f"   ❌ Erreur: {e}")
    
    # Test 2: Gamification endpoints
    logger.info("\n2️⃣ Gamification - Badges...")
    try:
        response = requests.get(f"{BASE_URL}/api/gamification/badges")
        data = response.json()
        logger.info(f"   ✅ Status: {response.status_code}")
        logger.info(f"   Total badges: {data.get('total', 0)}")
    except Exception as e:
        logger.info(f"   ❌ Erreur: {e}")
    
    logger.info("\n3️⃣ Gamification - Missions...")
    try:
        response = requests.get(f"{BASE_URL}/api/gamification/missions")
        data = response.json()
        logger.info(f"   ✅ Status: {response.status_code}")
        logger.info(f"   Total missions: {data.get('total', 0)}")
    except Exception as e:
        logger.info(f"   ❌ Erreur: {e}")
    
    logger.info("\n4️⃣ Gamification - Leaderboard...")
    try:
        response = requests.get(f"{BASE_URL}/api/gamification/leaderboard?limit=5")
        data = response.json()
        logger.info(f"   ✅ Status: {response.status_code}")
        logger.info(f"   Total utilisateurs: {data.get('total', 0)}")
    except Exception as e:
        logger.info(f"   ❌ Erreur: {e}")
    
    # Test 3: Transaction endpoints
    logger.info("\n5️⃣ Transactions - Pending...")
    try:
        response = requests.get(f"{BASE_URL}/api/transactions/pending")
        data = response.json()
        logger.info(f"   ✅ Status: {response.status_code}")
        logger.info(f"   Transactions en attente: {data.get('count', 0)}")
    except Exception as e:
        logger.info(f"   ❌ Erreur: {e}")
    
    # Test 4: Webhook endpoints
    logger.info("\n6️⃣ Webhooks - Stats...")
    try:
        response = requests.get(f"{BASE_URL}/api/webhooks/stats?period=30d")
        data = response.json()
        logger.info(f"   ✅ Status: {response.status_code}")
        stats = data.get('stats', {})
        logger.info(f"   Total webhooks: {stats.get('total_webhooks', 0)}")
        logger.info(f"   Taux de succès: {stats.get('success_rate', 0)}%")
    except Exception as e:
        logger.info(f"   ❌ Erreur: {e}")
    
    logger.info("\n7️⃣ Webhooks - Logs...")
    try:
        response = requests.get(f"{BASE_URL}/api/webhooks/logs?limit=5")
        data = response.json()
        logger.info(f"   ✅ Status: {response.status_code}")
        logger.info(f"   Total logs: {data.get('total', 0)}")
    except Exception as e:
        logger.info(f"   ❌ Erreur: {e}")
    
    # Test 5: Test webhook POST
    logger.info("\n8️⃣ Webhooks - Test POST...")
    try:
        payload = {
            "event_type": "test.manual",
            "source": "test_script",
            "payload": {
                "test": True,
                "message": "Test depuis script Python"
            }
        }
        response = requests.post(f"{BASE_URL}/api/webhooks/test", json=payload)
        logger.info(f"   ✅ Status: {response.status_code}")
        logger.info(f"   Response: {response.json()}")
    except Exception as e:
        logger.info(f"   ❌ Erreur: {e}")
    
    # Test 6: Documentation
    logger.info("\n9️⃣ Documentation OpenAPI...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        logger.info(f"   ✅ Status: {response.status_code}")
        logger.info(f"   Documentation accessible à: {BASE_URL}/docs")
    except Exception as e:
        logger.info(f"   ❌ Erreur: {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ TESTS TERMINÉS !")
    logger.info("\n📚 Documentation complète:")
    logger.info(f"   - Swagger UI: {BASE_URL}/docs")
    logger.info(f"   - ReDoc: {BASE_URL}/redoc")
    logger.info(f"   - OpenAPI JSON: {BASE_URL}/openapi.json")
    logger.info("\n💡 Pour tester avec authentification, obtenez d'abord un token:")
    logger.info(f"   curl -X POST {BASE_URL}/api/auth/login \\")
    logger.info('     -H "Content-Type: application/json" \\')
    logger.info('     -d \'{"email":"admin@getyourshare.com","password":"Admin123!"}\'')


if __name__ == "__main__":
    logger.info("⏳ Assurez-vous que le serveur FastAPI tourne (python server.py)...")
    input("Appuyez sur Entrée pour commencer les tests...")
    test_endpoints()
